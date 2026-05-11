/**
 * Billing Plans Page
 * Created by: Karim (Frontend Lead)
 */

import { Check } from 'lucide-react'
import { cn } from '@/utils/cn'

const plans = [
  {
    name: 'Free',
    description: 'Get started with basic features',
    priceMonthly: 0,
    priceYearly: 0,
    features: [
      '1 Facebook page',
      '100 AI replies/month',
      'Basic analytics',
      'Email support',
    ],
    highlighted: false,
    buttonText: 'Current Plan',
    disabled: true,
  },
  {
    name: 'Starter',
    description: 'Perfect for small businesses',
    priceMonthly: 499,
    priceYearly: 4990,
    features: [
      '3 Facebook pages',
      '1,000 AI replies/month',
      'Custom AI prompts',
      'Advanced analytics',
      'Priority support',
    ],
    highlighted: false,
    buttonText: 'Upgrade',
    disabled: false,
  },
  {
    name: 'Pro',
    description: 'For growing businesses',
    priceMonthly: 1499,
    priceYearly: 14990,
    features: [
      '10 Facebook pages',
      '5,000 AI replies/month',
      'Custom AI prompts',
      'Reply rules engine',
      'API access',
      'Dedicated support',
    ],
    highlighted: true,
    buttonText: 'Upgrade',
    disabled: false,
  },
  {
    name: 'Business',
    description: 'For large organizations',
    priceMonthly: 4999,
    priceYearly: 49990,
    features: [
      '25 Facebook pages',
      '20,000 AI replies/month',
      'Everything in Pro',
      'White-label options',
      'Custom integrations',
      'SLA guarantee',
    ],
    highlighted: false,
    buttonText: 'Contact Sales',
    disabled: false,
  },
]

export default function Plans() {
  return (
    <div className="space-y-6">
      <div className="text-center max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-900">
          Choose Your Plan
        </h1>
        <p className="text-gray-600 mt-2">
          Scale your Facebook engagement with the right plan for your business
        </p>
      </div>

      {/* Plans grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={cn(
              'card p-6 relative',
              plan.highlighted && 'ring-2 ring-primary-500'
            )}
          >
            {plan.highlighted && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="bg-primary-500 text-white text-xs font-medium px-3 py-1 rounded-full">
                  Most Popular
                </span>
              </div>
            )}

            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold text-gray-900">
                {plan.name}
              </h3>
              <p className="text-sm text-gray-500 mt-1">{plan.description}</p>
              <div className="mt-4">
                <span className="text-3xl font-bold text-gray-900">
                  ₹{plan.priceMonthly}
                </span>
                {plan.priceMonthly > 0 && (
                  <span className="text-gray-500">/month</span>
                )}
              </div>
              {plan.priceYearly > 0 && (
                <p className="text-xs text-gray-500 mt-1">
                  ₹{plan.priceYearly}/year (save 17%)
                </p>
              )}
            </div>

            <ul className="space-y-3 mb-6">
              {plan.features.map((feature, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <Check className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-600">{feature}</span>
                </li>
              ))}
            </ul>

            <button
              disabled={plan.disabled}
              className={cn(
                'w-full py-2 rounded-lg font-medium transition-colors',
                plan.highlighted
                  ? 'bg-primary-600 text-white hover:bg-primary-700'
                  : plan.disabled
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              {plan.buttonText}
            </button>
          </div>
        ))}
      </div>

      {/* FAQ */}
      <div className="max-w-2xl mx-auto mt-12">
        <h2 className="text-lg font-semibold text-gray-900 text-center mb-6">
          Frequently Asked Questions
        </h2>
        <div className="space-y-4">
          <div className="card p-4">
            <h3 className="font-medium text-gray-900">
              Can I change plans later?
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Yes, you can upgrade or downgrade your plan at any time. Changes
              take effect immediately.
            </p>
          </div>
          <div className="card p-4">
            <h3 className="font-medium text-gray-900">
              What payment methods do you accept?
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              We accept all major credit/debit cards, UPI, and net banking
              through Razorpay.
            </p>
          </div>
          <div className="card p-4">
            <h3 className="font-medium text-gray-900">Is there a free trial?</h3>
            <p className="text-sm text-gray-600 mt-1">
              Yes! All new accounts get a 14-day free trial with Starter plan
              features.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
