/**
 * Subscription Management Page
 * Created by: Karim (Frontend Lead)
 */

import { Link } from 'react-router-dom'
import { ArrowLeft, CreditCard, Calendar, AlertCircle } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'

export default function Subscription() {
  const { subscription } = useAuthStore()

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/billing" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Subscription</h1>
          <p className="text-gray-600 mt-1">Manage your subscription and billing</p>
        </div>
      </div>

      {/* Current Plan */}
      <div className="card p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Current Plan</h2>
        <div className="flex items-center justify-between p-4 bg-primary-50 rounded-xl">
          <div>
            <p className="text-2xl font-bold text-primary-700">
              {subscription?.plan_name || 'Free'}
            </p>
            {subscription?.status === 'trialing' && (
              <p className="text-sm text-primary-600 mt-1">
                Trial ends in 7 days
              </p>
            )}
          </div>
          <Link to="/billing" className="btn-primary">
            Upgrade Plan
          </Link>
        </div>
      </div>

      {/* Usage */}
      {subscription && (
        <div className="card p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Usage This Month</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">AI Replies</span>
                <span className="font-medium">
                  {subscription.replies_used} / {subscription.replies_limit}
                </span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-500 rounded-full transition-all"
                  style={{
                    width: `${Math.min(
                      (subscription.replies_used / subscription.replies_limit) * 100,
                      100
                    )}%`,
                  }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600">Connected Pages</span>
                <span className="font-medium">
                  {subscription.pages_used} / {subscription.pages_limit}
                </span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-accent-500 rounded-full transition-all"
                  style={{
                    width: `${Math.min(
                      (subscription.pages_used / subscription.pages_limit) * 100,
                      100
                    )}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Payment Method */}
      <div className="card p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Payment Method</h2>
        <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl">
          <div className="w-12 h-8 bg-white rounded flex items-center justify-center border">
            <CreditCard className="w-6 h-6 text-gray-400" />
          </div>
          <div className="flex-1">
            <p className="text-gray-500 text-sm">No payment method added</p>
          </div>
          <button className="btn-secondary text-sm">Add Card</button>
        </div>
      </div>

      {/* Billing History */}
      <div className="card p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Billing History</h2>
        <div className="text-center py-8 text-gray-500">
          <Calendar className="w-12 h-12 mx-auto text-gray-300 mb-2" />
          <p>No invoices yet</p>
        </div>
      </div>

      {/* Cancel */}
      <div className="card p-6 border-red-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-gray-900">Cancel Subscription</h3>
            <p className="text-sm text-gray-600 mt-1">
              If you cancel, you'll lose access to premium features at the end
              of your billing period.
            </p>
            <button className="mt-3 text-sm text-red-600 hover:text-red-700 font-medium">
              Cancel subscription
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
