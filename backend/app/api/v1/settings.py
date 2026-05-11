"""
Settings API Routes - Organization settings, AI Prompts, Reply Rules
Created by: Sadia (Backend Lead)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.api.deps import get_current_user, get_current_organization, require_permission
from app.models.user import User
from app.models.organization import Organization
from app.models.ai_prompt import AIPrompt, ReplyRule, RuleActionType
from app.schemas.organization import (
    OrganizationSettingsUpdate,
    OrganizationSettingsResponse,
)
from app.schemas.ai import (
    AIPromptCreate,
    AIPromptUpdate,
    AIPromptResponse,
    AIPromptListResponse,
    ReplyRuleCreate,
    ReplyRuleUpdate,
    ReplyRuleResponse,
    ReplyRuleListResponse,
)

router = APIRouter(prefix="/settings", tags=["Settings"])


# ============== Organization Settings ==============

@router.get("", response_model=OrganizationSettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get organization settings"""
    return {
        "id": str(organization.id),
        "name": organization.name,
        "slug": organization.slug,
        "settings": organization.settings or {},
        "created_at": organization.created_at.isoformat(),
    }


@router.put("", response_model=OrganizationSettingsResponse)
async def update_settings(
    request: OrganizationSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Update organization settings"""
    # Merge with existing settings
    current_settings = organization.settings or {}
    new_settings = request.settings or {}

    merged_settings = {**current_settings, **new_settings}
    organization.settings = merged_settings

    if request.name:
        organization.name = request.name

    await db.commit()
    await db.refresh(organization)

    return {
        "id": str(organization.id),
        "name": organization.name,
        "slug": organization.slug,
        "settings": organization.settings,
        "created_at": organization.created_at.isoformat(),
    }


# ============== AI Prompts ==============

@router.get("/prompts", response_model=AIPromptListResponse)
async def list_prompts(
    tone: Optional[str] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """List AI prompts for the organization"""
    query = select(AIPrompt).where(AIPrompt.organization_id == organization.id)

    if tone:
        query = query.where(AIPrompt.tone == tone)

    if is_active is not None:
        query = query.where(AIPrompt.is_active == is_active)

    query = query.order_by(AIPrompt.is_default.desc(), AIPrompt.created_at.desc())

    result = await db.execute(query)
    prompts = result.scalars().all()

    return {"prompts": prompts, "total": len(prompts)}


@router.post("/prompts", response_model=AIPromptResponse)
async def create_prompt(
    request: AIPromptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Create a new AI prompt"""
    # Check prompt limit (based on subscription)
    # TODO: Check against subscription limits

    prompt = AIPrompt(
        organization_id=organization.id,
        name=request.name,
        description=request.description,
        prompt_type=request.prompt_type,
        system_prompt=request.system_prompt,
        user_prompt_template=request.user_prompt_template,
        tone=request.tone,
        language=request.language,
        max_length=request.max_length,
        temperature=request.temperature,
        is_active=request.is_active,
        is_default=False,  # Can only be set by separate endpoint
        created_by=current_user.id,
    )

    db.add(prompt)
    await db.commit()
    await db.refresh(prompt)

    return prompt


@router.get("/prompts/{prompt_id}", response_model=AIPromptResponse)
async def get_prompt(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get a specific AI prompt"""
    result = await db.execute(
        select(AIPrompt).where(
            and_(
                AIPrompt.id == prompt_id,
                AIPrompt.organization_id == organization.id,
            )
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    return prompt


@router.put("/prompts/{prompt_id}", response_model=AIPromptResponse)
async def update_prompt(
    prompt_id: UUID,
    request: AIPromptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Update an AI prompt"""
    result = await db.execute(
        select(AIPrompt).where(
            and_(
                AIPrompt.id == prompt_id,
                AIPrompt.organization_id == organization.id,
            )
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(prompt, field, value)

    prompt.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(prompt)

    return prompt


@router.delete("/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Delete an AI prompt"""
    result = await db.execute(
        select(AIPrompt).where(
            and_(
                AIPrompt.id == prompt_id,
                AIPrompt.organization_id == organization.id,
            )
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    if prompt.is_default:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete default prompt"
        )

    await db.delete(prompt)
    await db.commit()

    return {"message": "Prompt deleted successfully"}


@router.post("/prompts/{prompt_id}/set-default")
async def set_default_prompt(
    prompt_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Set a prompt as the default for its type"""
    result = await db.execute(
        select(AIPrompt).where(
            and_(
                AIPrompt.id == prompt_id,
                AIPrompt.organization_id == organization.id,
            )
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    # Unset current default for this type
    await db.execute(
        select(AIPrompt).where(
            and_(
                AIPrompt.organization_id == organization.id,
                AIPrompt.prompt_type == prompt.prompt_type,
                AIPrompt.is_default == True,
            )
        )
    )
    current_defaults = (await db.execute(
        select(AIPrompt).where(
            and_(
                AIPrompt.organization_id == organization.id,
                AIPrompt.prompt_type == prompt.prompt_type,
                AIPrompt.is_default == True,
            )
        )
    )).scalars().all()

    for default in current_defaults:
        default.is_default = False

    # Set new default
    prompt.is_default = True

    await db.commit()

    return {"message": "Default prompt updated"}


@router.post("/prompts/{prompt_id}/test")
async def test_prompt(
    prompt_id: UUID,
    test_comment: str,
    test_context: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Test a prompt with sample comment"""
    from app.services.ai_service import AIService

    result = await db.execute(
        select(AIPrompt).where(
            and_(
                AIPrompt.id == prompt_id,
                AIPrompt.organization_id == organization.id,
            )
        )
    )
    prompt = result.scalar_one_or_none()

    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )

    ai_service = AIService()

    try:
        reply_result = await ai_service.generate_reply(
            comment_text=test_comment,
            post_context=test_context,
            organization=organization,
            prompt_id=prompt_id,
        )

        return {
            "input_comment": test_comment,
            "input_context": test_context,
            "generated_reply": reply_result["reply_text"],
            "sentiment": reply_result.get("sentiment"),
            "model": reply_result.get("model"),
            "tokens_used": reply_result.get("tokens_used"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test prompt: {str(e)}"
        )


# ============== Reply Rules ==============

@router.get("/rules", response_model=ReplyRuleListResponse)
async def list_rules(
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """List reply rules for the organization"""
    query = select(ReplyRule).where(ReplyRule.organization_id == organization.id)

    if is_active is not None:
        query = query.where(ReplyRule.is_active == is_active)

    query = query.order_by(ReplyRule.priority.desc(), ReplyRule.created_at.desc())

    result = await db.execute(query)
    rules = result.scalars().all()

    return {"rules": rules, "total": len(rules)}


@router.post("/rules", response_model=ReplyRuleResponse)
async def create_rule(
    request: ReplyRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Create a new reply rule"""
    rule = ReplyRule(
        organization_id=organization.id,
        name=request.name,
        description=request.description,
        condition_type=request.condition_type,
        condition_value=request.condition_value,
        condition_operator=request.condition_operator,
        action_type=request.action_type,
        action_value=request.action_value,
        priority=request.priority,
        is_active=request.is_active,
        created_by=current_user.id,
    )

    db.add(rule)
    await db.commit()
    await db.refresh(rule)

    return rule


@router.get("/rules/{rule_id}", response_model=ReplyRuleResponse)
async def get_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Get a specific reply rule"""
    result = await db.execute(
        select(ReplyRule).where(
            and_(
                ReplyRule.id == rule_id,
                ReplyRule.organization_id == organization.id,
            )
        )
    )
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )

    return rule


@router.put("/rules/{rule_id}", response_model=ReplyRuleResponse)
async def update_rule(
    rule_id: UUID,
    request: ReplyRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Update a reply rule"""
    result = await db.execute(
        select(ReplyRule).where(
            and_(
                ReplyRule.id == rule_id,
                ReplyRule.organization_id == organization.id,
            )
        )
    )
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )

    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    rule.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(rule)

    return rule


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Delete a reply rule"""
    result = await db.execute(
        select(ReplyRule).where(
            and_(
                ReplyRule.id == rule_id,
                ReplyRule.organization_id == organization.id,
            )
        )
    )
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )

    await db.delete(rule)
    await db.commit()

    return {"message": "Rule deleted successfully"}


@router.post("/rules/{rule_id}/toggle")
async def toggle_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Toggle a rule's active status"""
    result = await db.execute(
        select(ReplyRule).where(
            and_(
                ReplyRule.id == rule_id,
                ReplyRule.organization_id == organization.id,
            )
        )
    )
    rule = result.scalar_one_or_none()

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )

    rule.is_active = not rule.is_active
    rule.updated_at = datetime.utcnow()

    await db.commit()

    return {
        "message": f"Rule {'activated' if rule.is_active else 'deactivated'}",
        "is_active": rule.is_active,
    }


@router.post("/rules/reorder")
async def reorder_rules(
    rule_priorities: List[dict],  # [{"id": "uuid", "priority": 1}, ...]
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    organization: Organization = Depends(get_current_organization),
):
    """Reorder rules by updating priorities"""
    for item in rule_priorities:
        rule_id = item.get("id")
        priority = item.get("priority")

        if rule_id and priority is not None:
            result = await db.execute(
                select(ReplyRule).where(
                    and_(
                        ReplyRule.id == rule_id,
                        ReplyRule.organization_id == organization.id,
                    )
                )
            )
            rule = result.scalar_one_or_none()

            if rule:
                rule.priority = priority

    await db.commit()

    return {"message": "Rules reordered successfully"}
