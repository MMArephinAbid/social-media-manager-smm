/**
 * Comments List Page
 * Created by: Karim (Frontend Lead)
 */

import { useState } from 'react'
import { Search, Filter, RefreshCw, MessageSquare, Check, X, Clock } from 'lucide-react'
import { cn } from '@/utils/cn'

const comments = [
  {
    id: '1',
    page: 'My Business Page',
    commenter: 'আহমেদ আলী',
    commenterPicture: null,
    comment: 'আপনাদের পণ্যের দাম কত?',
    reply: 'ধন্যবাদ আপনার আগ্রহের জন্য! আমাদের পণ্যের দাম ₹499 থেকে শুরু। বিস্তারিত জানতে আমাদের ওয়েবসাইট ভিজিট করুন।',
    status: 'replied',
    sentiment: 'neutral',
    createdAt: '2 min ago',
    repliedAt: '1 min ago',
  },
  {
    id: '2',
    page: 'My Business Page',
    commenter: 'ফাতেমা খান',
    commenterPicture: null,
    comment: 'ডেলিভারি কতদিন লাগে ঢাকায়?',
    reply: 'ঢাকায় সাধারণত ২-৩ কার্যদিবসের মধ্যে ডেলিভারি হয়ে যায়। ধন্যবাদ।',
    status: 'replied',
    sentiment: 'neutral',
    createdAt: '15 min ago',
    repliedAt: '14 min ago',
  },
  {
    id: '3',
    page: 'My Business Page',
    commenter: 'করিম সাহেব',
    commenterPicture: null,
    comment: 'খুব ভালো সার্ভিস! অনেক ধন্যবাদ।',
    reply: null,
    status: 'pending',
    sentiment: 'positive',
    createdAt: '1 hour ago',
    repliedAt: null,
  },
  {
    id: '4',
    page: 'Second Page',
    commenter: 'রহিমা বেগম',
    commenterPicture: null,
    comment: 'কেন এত দেরি হচ্ছে অর্ডার আসতে?',
    reply: null,
    status: 'pending',
    sentiment: 'negative',
    createdAt: '2 hours ago',
    repliedAt: null,
  },
]

const statusOptions = [
  { value: 'all', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'replied', label: 'Replied' },
  { value: 'failed', label: 'Failed' },
  { value: 'skipped', label: 'Skipped' },
]

export default function CommentsList() {
  const [statusFilter, setStatusFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  const filteredComments = comments.filter((comment) => {
    if (statusFilter !== 'all' && comment.status !== statusFilter) {
      return false
    }
    if (
      searchQuery &&
      !comment.comment.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !comment.commenter.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false
    }
    return true
  })

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'replied':
        return <span className="badge-success">Replied</span>
      case 'pending':
        return <span className="badge-warning">Pending</span>
      case 'failed':
        return <span className="badge-danger">Failed</span>
      case 'skipped':
        return <span className="badge-gray">Skipped</span>
      default:
        return null
    }
  }

  const getSentimentBadge = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return <span className="text-green-600">😊</span>
      case 'negative':
        return <span className="text-red-600">😞</span>
      default:
        return <span className="text-gray-400">😐</span>
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Comments</h1>
          <p className="text-gray-600 mt-1">
            View and manage comments from your connected pages
          </p>
        </div>
        <button className="btn-secondary">
          <RefreshCw className="w-4 h-4 mr-2" />
          Sync
        </button>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search comments..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Status filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input w-auto"
            >
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Comments list */}
      <div className="card divide-y divide-gray-100">
        {filteredComments.length > 0 ? (
          filteredComments.map((comment) => (
            <div key={comment.id} className="p-5 hover:bg-gray-50">
              <div className="flex items-start gap-4">
                {/* Avatar */}
                <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                  {comment.commenterPicture ? (
                    <img
                      src={comment.commenterPicture}
                      alt={comment.commenter}
                      className="w-10 h-10 rounded-full"
                    />
                  ) : (
                    <span className="text-gray-500 font-medium">
                      {comment.commenter.charAt(0)}
                    </span>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-gray-900">
                      {comment.commenter}
                    </span>
                    <span className="text-xs text-gray-400">•</span>
                    <span className="text-xs text-gray-500">{comment.page}</span>
                    <span className="text-xs text-gray-400">•</span>
                    <span className="text-xs text-gray-500">
                      {comment.createdAt}
                    </span>
                    {getStatusBadge(comment.status)}
                    {getSentimentBadge(comment.sentiment)}
                  </div>

                  {/* Original comment */}
                  <p className="mt-2 text-gray-800 font-bengali">
                    "{comment.comment}"
                  </p>

                  {/* Reply */}
                  {comment.reply && (
                    <div className="mt-3 pl-4 border-l-2 border-primary-200">
                      <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                        <MessageSquare className="w-3 h-3" />
                        <span>AI Reply • {comment.repliedAt}</span>
                      </div>
                      <p className="text-sm text-gray-600 font-bengali">
                        {comment.reply}
                      </p>
                    </div>
                  )}

                  {/* Actions for pending */}
                  {comment.status === 'pending' && (
                    <div className="mt-3 flex items-center gap-2">
                      <button className="btn-primary text-sm py-1 px-3">
                        <Check className="w-3 h-3 mr-1" />
                        Generate Reply
                      </button>
                      <button className="btn-secondary text-sm py-1 px-3">
                        <Clock className="w-3 h-3 mr-1" />
                        Skip
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="p-12 text-center">
            <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-1">
              No comments found
            </h3>
            <p className="text-gray-500">
              {searchQuery
                ? 'Try adjusting your search or filters'
                : 'Comments will appear here when they come in'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
