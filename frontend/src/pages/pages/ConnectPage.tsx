/**
 * Connect Facebook Page
 * Created by: Karim (Frontend Lead)
 */

import { ArrowLeft, Facebook, Shield, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function ConnectPage() {
  const handleConnectFacebook = () => {
    // TODO: Implement Facebook OAuth flow
    console.log('Connect to Facebook')
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Back link */}
      <Link
        to="/pages"
        className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Pages
      </Link>

      <div className="card p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Facebook className="w-8 h-8 text-blue-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Connect Facebook Page
          </h1>
          <p className="text-gray-600">
            Connect your Facebook page to enable automatic AI-powered replies
          </p>
        </div>

        {/* Permissions info */}
        <div className="bg-gray-50 rounded-xl p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-4">
            We'll request access to:
          </h3>
          <ul className="space-y-3">
            {[
              'View pages you manage',
              'Read comments on your posts',
              'Reply to comments on your behalf',
              'View page insights',
            ].map((permission, i) => (
              <li key={i} className="flex items-center gap-3 text-sm">
                <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center">
                  <Shield className="w-3 h-3 text-green-600" />
                </div>
                <span className="text-gray-700">{permission}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Security note */}
        <div className="bg-blue-50 rounded-xl p-4 mb-8">
          <div className="flex gap-3">
            <Zap className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900">Secure & Private</h4>
              <p className="text-sm text-blue-700 mt-1">
                Your Facebook credentials are never stored. We use OAuth for
                secure authentication.
              </p>
            </div>
          </div>
        </div>

        {/* Connect button */}
        <button
          onClick={handleConnectFacebook}
          className="w-full bg-[#1877f2] hover:bg-[#166fe5] text-white font-medium py-3 rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          <Facebook className="w-5 h-5" />
          Continue with Facebook
        </button>

        <p className="text-xs text-gray-500 text-center mt-4">
          By connecting, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  )
}
