"""
Billing API Routes - Razorpay & Stripe Integration
Created by: Sadia (Backend Lead)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import hashlib
import hmac
import json

from app.database import get_db
from app.api.deps import get_current_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.models.subscription import Subscription, Plan, SubscriptionStatus, PaymentProvider
from app.config import settings
from app.schemas.billing import (
    PlanResponse,
    PlanListResponse,
    SubscriptionResponse,
    CreateSubscriptionRequest,
    RazorpayOrderResponse,
    VerifyPaymentRequest,
)

router = APIRouter(prefix="/billing", tags=["Billing"])


# ============== Plans ==============

@router.get("/plans", response_model=PlanListResponse)
async def list_plans(
    db: AsyncSession = Depends(get_db),
):
    """List all available subscription plans"""
    result = await db.execute(
        select(Plan)
        .where(Plan.is_active == True)
        .order_by(Plan.price_monthly)
    )
    plans = result.scalars().all()

    return {"plans": plans, "total": len(plans)}


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific plan"""
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )

    return plan


# ============== Subscription ==============

@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get current organization subscription"""
    result = await db.execute(
        select(Subscription)
        .where(Subscription.organization_id == organization.id)
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        # Return free tier info
        return {
            "id": None,
            "plan_name": "Free",
            "status": "active",
            "replies_used": 0,
            "replies_limit": 50,
            "pages_used": organization.pages_count or 0,
            "pages_limit": 1,
            "current_period_start": None,
            "current_period_end": None,
            "is_trial": False,
        }

    return subscription


@router.post("/subscribe/razorpay", response_model=RazorpayOrderResponse)
async def create_razorpay_order(
    request: CreateSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Create a Razorpay order for subscription"""
    import razorpay

    # Get plan
    result = await db.execute(
        select(Plan).where(Plan.id == request.plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )

    # Calculate amount
    if request.billing_cycle == "yearly":
        amount = int(plan.price_yearly * 100)  # Razorpay uses paise
    else:
        amount = int(plan.price_monthly * 100)

    # Create Razorpay client
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    # Create order
    order_data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"sub_{organization.id}_{datetime.utcnow().timestamp()}",
        "notes": {
            "organization_id": str(organization.id),
            "plan_id": str(plan.id),
            "billing_cycle": request.billing_cycle,
        }
    }

    try:
        order = client.order.create(data=order_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Razorpay order: {str(e)}"
        )

    return {
        "order_id": order["id"],
        "amount": amount,
        "currency": "INR",
        "key_id": settings.RAZORPAY_KEY_ID,
        "plan_name": plan.name,
        "organization_name": organization.name,
        "user_email": current_user.email,
        "user_name": f"{current_user.first_name} {current_user.last_name}",
    }


@router.post("/verify/razorpay")
async def verify_razorpay_payment(
    request: VerifyPaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Verify Razorpay payment and activate subscription"""
    import razorpay

    # Verify signature
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': request.order_id,
            'razorpay_payment_id': request.payment_id,
            'razorpay_signature': request.signature,
        })
    except razorpay.errors.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment signature"
        )

    # Get order details
    order = client.order.fetch(request.order_id)
    notes = order.get("notes", {})

    plan_id = notes.get("plan_id")
    billing_cycle = notes.get("billing_cycle", "monthly")

    # Get plan
    result = await db.execute(
        select(Plan).where(Plan.id == plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan not found"
        )

    # Cancel existing subscription if any
    existing = await db.execute(
        select(Subscription).where(
            and_(
                Subscription.organization_id == organization.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        )
    )
    existing_sub = existing.scalar_one_or_none()
    if existing_sub:
        existing_sub.status = SubscriptionStatus.CANCELLED
        existing_sub.cancelled_at = datetime.utcnow()

    # Create subscription
    now = datetime.utcnow()
    if billing_cycle == "yearly":
        period_end = now + timedelta(days=365)
    else:
        period_end = now + timedelta(days=30)

    subscription = Subscription(
        organization_id=organization.id,
        plan_id=plan.id,
        status=SubscriptionStatus.ACTIVE,
        payment_provider=PaymentProvider.RAZORPAY,
        provider_subscription_id=request.payment_id,
        current_period_start=now,
        current_period_end=period_end,
        billing_cycle=billing_cycle,
        amount_paid=order["amount"] / 100,  # Convert from paise
        currency="INR",
    )

    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)

    return {
        "message": "Subscription activated successfully",
        "subscription_id": str(subscription.id),
        "plan_name": plan.name,
        "valid_until": period_end.isoformat(),
    }


@router.post("/subscribe/stripe")
async def create_stripe_checkout(
    request: CreateSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Create a Stripe checkout session"""
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get plan
    result = await db.execute(
        select(Plan).where(Plan.id == request.plan_id)
    )
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )

    # Get or create Stripe price ID
    if request.billing_cycle == "yearly":
        price_id = plan.stripe_price_id_yearly
        amount = plan.price_yearly
    else:
        price_id = plan.stripe_price_id_monthly
        amount = plan.price_monthly

    if not price_id:
        # Create price in Stripe
        try:
            price = stripe.Price.create(
                unit_amount=int(amount * 100),  # cents
                currency="usd",
                recurring={"interval": "year" if request.billing_cycle == "yearly" else "month"},
                product_data={
                    "name": f"{plan.name} Plan",
                    "metadata": {"plan_id": str(plan.id)},
                },
            )
            price_id = price.id

            # Save price ID to plan
            if request.billing_cycle == "yearly":
                plan.stripe_price_id_yearly = price_id
            else:
                plan.stripe_price_id_monthly = price_id
            await db.commit()

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create Stripe price: {str(e)}"
            )

    # Create checkout session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/billing/cancelled",
            customer_email=current_user.email,
            metadata={
                "organization_id": str(organization.id),
                "plan_id": str(plan.id),
                "billing_cycle": request.billing_cycle,
            },
        )

        return {
            "checkout_url": session.url,
            "session_id": session.id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Stripe session: {str(e)}"
        )


@router.post("/cancel")
async def cancel_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Cancel current subscription"""
    result = await db.execute(
        select(Subscription).where(
            and_(
                Subscription.organization_id == organization.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        )
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )

    # Mark as cancelled (will remain active until period end)
    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = datetime.utcnow()
    subscription.cancel_at_period_end = True

    await db.commit()

    return {
        "message": "Subscription cancelled",
        "active_until": subscription.current_period_end.isoformat(),
    }


# ============== Webhooks ==============

@router.post("/webhook/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Handle Razorpay webhook events"""
    body = await request.body()

    # Verify signature
    expected_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if x_razorpay_signature != expected_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )

    payload = json.loads(body)
    event = payload.get("event")

    if event == "subscription.charged":
        # Subscription renewed
        payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
        subscription_id = payload.get("payload", {}).get("subscription", {}).get("entity", {}).get("id")

        # Update subscription
        result = await db.execute(
            select(Subscription).where(
                Subscription.provider_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.current_period_start = datetime.utcnow()
            if subscription.billing_cycle == "yearly":
                subscription.current_period_end = datetime.utcnow() + timedelta(days=365)
            else:
                subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
            subscription.replies_used = 0  # Reset usage
            await db.commit()

    elif event == "subscription.cancelled":
        subscription_id = payload.get("payload", {}).get("subscription", {}).get("entity", {}).get("id")

        result = await db.execute(
            select(Subscription).where(
                Subscription.provider_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()
            await db.commit()

    elif event == "payment.failed":
        subscription_id = payload.get("payload", {}).get("subscription", {}).get("entity", {}).get("id")

        result = await db.execute(
            select(Subscription).where(
                Subscription.provider_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE
            await db.commit()

    return {"status": "ok"}


@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events"""
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    body = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            body,
            stripe_signature,
            settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})

        organization_id = metadata.get("organization_id")
        plan_id = metadata.get("plan_id")
        billing_cycle = metadata.get("billing_cycle", "monthly")

        if organization_id and plan_id:
            # Get plan
            result = await db.execute(
                select(Plan).where(Plan.id == plan_id)
            )
            plan = result.scalar_one_or_none()

            if plan:
                # Cancel existing
                existing = await db.execute(
                    select(Subscription).where(
                        and_(
                            Subscription.organization_id == organization_id,
                            Subscription.status == SubscriptionStatus.ACTIVE,
                        )
                    )
                )
                existing_sub = existing.scalar_one_or_none()
                if existing_sub:
                    existing_sub.status = SubscriptionStatus.CANCELLED
                    existing_sub.cancelled_at = datetime.utcnow()

                # Create subscription
                now = datetime.utcnow()
                period_end = now + timedelta(days=365 if billing_cycle == "yearly" else 30)

                subscription = Subscription(
                    organization_id=organization_id,
                    plan_id=plan.id,
                    status=SubscriptionStatus.ACTIVE,
                    payment_provider=PaymentProvider.STRIPE,
                    provider_subscription_id=session.get("subscription"),
                    current_period_start=now,
                    current_period_end=period_end,
                    billing_cycle=billing_cycle,
                    amount_paid=session.get("amount_total", 0) / 100,
                    currency="USD",
                )

                db.add(subscription)
                await db.commit()

    elif event["type"] == "invoice.paid":
        subscription_id = event["data"]["object"].get("subscription")

        result = await db.execute(
            select(Subscription).where(
                Subscription.provider_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.current_period_start = datetime.utcnow()
            if subscription.billing_cycle == "yearly":
                subscription.current_period_end = datetime.utcnow() + timedelta(days=365)
            else:
                subscription.current_period_end = datetime.utcnow() + timedelta(days=30)
            subscription.replies_used = 0
            await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        subscription_id = event["data"]["object"].get("id")

        result = await db.execute(
            select(Subscription).where(
                Subscription.provider_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.cancelled_at = datetime.utcnow()
            await db.commit()

    elif event["type"] == "invoice.payment_failed":
        subscription_id = event["data"]["object"].get("subscription")

        result = await db.execute(
            select(Subscription).where(
                Subscription.provider_subscription_id == subscription_id
            )
        )
        subscription = result.scalar_one_or_none()

        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE
            await db.commit()

    return {"status": "ok"}


@router.get("/invoices")
async def list_invoices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """List organization invoices/payment history"""
    result = await db.execute(
        select(Subscription)
        .where(Subscription.organization_id == organization.id)
        .order_by(Subscription.created_at.desc())
    )
    subscriptions = result.scalars().all()

    invoices = []
    for sub in subscriptions:
        if sub.amount_paid and sub.amount_paid > 0:
            invoices.append({
                "id": str(sub.id),
                "date": sub.created_at.isoformat(),
                "amount": sub.amount_paid,
                "currency": sub.currency,
                "plan_name": sub.plan.name if sub.plan else "Unknown",
                "status": "paid",
                "provider": sub.payment_provider.value if sub.payment_provider else None,
            })

    return {"invoices": invoices, "total": len(invoices)}


@router.get("/usage")
async def get_usage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get current usage statistics"""
    result = await db.execute(
        select(Subscription)
        .where(
            and_(
                Subscription.organization_id == organization.id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription and subscription.plan:
        plan = subscription.plan
        return {
            "plan_name": plan.name,
            "replies": {
                "used": subscription.replies_used or 0,
                "limit": plan.replies_limit,
                "percentage": round((subscription.replies_used or 0) / plan.replies_limit * 100, 2) if plan.replies_limit > 0 else 0,
            },
            "pages": {
                "used": organization.pages_count or 0,
                "limit": plan.pages_limit,
                "percentage": round((organization.pages_count or 0) / plan.pages_limit * 100, 2) if plan.pages_limit > 0 else 0,
            },
            "ai_tokens": {
                "used": subscription.tokens_used or 0,
                "limit": plan.tokens_limit or 0,
            },
            "period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        }
    else:
        # Free tier
        return {
            "plan_name": "Free",
            "replies": {
                "used": 0,
                "limit": 50,
                "percentage": 0,
            },
            "pages": {
                "used": organization.pages_count or 0,
                "limit": 1,
                "percentage": (organization.pages_count or 0) * 100,
            },
            "ai_tokens": {
                "used": 0,
                "limit": 10000,
            },
            "period_end": None,
        }
