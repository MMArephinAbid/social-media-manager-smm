/**
 * Pages List Page
 * Created by: Karim (Frontend Lead)
 */

import { Link } from 'react-router-dom'
import { Plus, Facebook, Settings, Trash2, RefreshCw } from 'lucide-react'

const pages = [
  {
    id: '1',
    name: 'My Business Page',
    category: 'Business',
    followers: '12.5K',
    isActive: true,
    lastSynced: '2 min ago',
    repliesThisMonth: 234,
    pictureUrl: null,
  },
]

export default function PagesList() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Facebook Pages</h1>
          <p className="text-gray-600 mt-1">
            Manage your connected Facebook pages
          </p>
        </div>
        <Link to="/pages/connect" className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          Connect Page
        </Link>
      </div>

      {/* Pages Grid */}
      {pages.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pages.map((page) => (
            <div key={page.id} className="card p-5">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 bg-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
                  {page.pictureUrl ? (
                    <img
                      src={page.pictureUrl}
                      alt={page.name}
                      className="w-14 h-14 rounded-xl"
                    />
                  ) : (
                    <Facebook className="w-7 h-7 text-white" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900 truncate">
                      {page.name}
                    </h3>
                    {page.isActive ? (
                      <span className="w-2 h-2 bg-green-500 rounded-full" />
                    ) : (
                      <span className="w-2 h-2 bg-gray-300 rounded-full" />
                    )}
                  </div>
                  <p className="text-sm text-gray-500">{page.category}</p>
                  <p className="text-sm text-gray-500">
                    {page.followers} followers
                  </p>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Replies this month</span>
                  <span className="font-medium">{page.repliesThisMonth}</span>
                </div>
                <div className="flex items-center justify-between text-sm mt-1">
                  <span className="text-gray-500">Last synced</span>
                  <span className="text-gray-600">{page.lastSynced}</span>
                </div>
              </div>

              <div className="mt-4 flex items-center gap-2">
                <button className="flex-1 btn-secondary text-sm py-1.5">
                  <Settings className="w-4 h-4 mr-1" />
                  Settings
                </button>
                <button className="p-2 hover:bg-gray-100 rounded-lg">
                  <RefreshCw className="w-4 h-4 text-gray-500" />
                </button>
                <button className="p-2 hover:bg-red-50 rounded-lg">
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card p-12 text-center">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Facebook className="w-8 h-8 text-blue-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No pages connected
          </h2>
          <p className="text-gray-600 mb-6">
            Connect your Facebook pages to start auto-replying to comments
          </p>
          <Link to="/pages/connect" className="btn-primary">
            <Plus className="w-4 h-4 mr-2" />
            Connect Your First Page
          </Link>
        </div>
      )}
    </div>
  )
}
