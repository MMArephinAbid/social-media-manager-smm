/**
 * Reply Rules Settings Page
 * Created by: Karim (Frontend Lead)
 */

import { ArrowLeft, Plus, Edit2, Trash2, Play, Pause } from 'lucide-react'
import { Link } from 'react-router-dom'
import { cn } from '@/utils/cn'

const rules = [
  {
    id: '1',
    name: 'Price Inquiry',
    description: 'Auto-reply to price-related questions',
    ruleType: 'keyword',
    keywords: ['দাম', 'price', 'কত', 'cost'],
    action: 'auto_reply',
    isActive: true,
    timesMatched: 234,
  },
  {
    id: '2',
    name: 'Negative Sentiment',
    description: 'Flag negative comments for review',
    ruleType: 'sentiment',
    matchSentiment: 'negative',
    action: 'flag',
    isActive: true,
    timesMatched: 45,
  },
  {
    id: '3',
    name: 'Spam Filter',
    description: 'Skip spam-like comments',
    ruleType: 'keyword',
    keywords: ['earn money', 'click here', 'free'],
    action: 'skip',
    isActive: false,
    timesMatched: 12,
  },
]

const actionLabels: Record<string, { label: string; color: string }> = {
  auto_reply: { label: 'Auto Reply', color: 'bg-green-100 text-green-700' },
  template_reply: { label: 'Template', color: 'bg-blue-100 text-blue-700' },
  skip: { label: 'Skip', color: 'bg-gray-100 text-gray-700' },
  flag: { label: 'Flag', color: 'bg-yellow-100 text-yellow-700' },
  escalate: { label: 'Escalate', color: 'bg-red-100 text-red-700' },
}

export default function ReplyRules() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to="/settings" className="p-2 hover:bg-gray-100 rounded-lg">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Reply Rules</h1>
            <p className="text-gray-600 mt-1">
              Automate how comments are handled
            </p>
          </div>
        </div>
        <button className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          New Rule
        </button>
      </div>

      {/* Rules list */}
      <div className="space-y-4">
        {rules.map((rule) => (
          <div
            key={rule.id}
            className={cn('card p-5', !rule.isActive && 'opacity-60')}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <button
                  className={cn(
                    'w-10 h-10 rounded-lg flex items-center justify-center',
                    rule.isActive
                      ? 'bg-green-100 text-green-600'
                      : 'bg-gray-100 text-gray-400'
                  )}
                >
                  {rule.isActive ? (
                    <Play className="w-5 h-5" />
                  ) : (
                    <Pause className="w-5 h-5" />
                  )}
                </button>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900">{rule.name}</h3>
                    <span
                      className={cn(
                        'text-xs px-2 py-0.5 rounded-full',
                        actionLabels[rule.action]?.color
                      )}
                    >
                      {actionLabels[rule.action]?.label}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-0.5">
                    {rule.description}
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                    <span>Type: {rule.ruleType}</span>
                    {rule.keywords && (
                      <span>Keywords: {rule.keywords.join(', ')}</span>
                    )}
                    {rule.matchSentiment && (
                      <span>Sentiment: {rule.matchSentiment}</span>
                    )}
                    <span>Matched: {rule.timesMatched} times</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button className="p-2 hover:bg-gray-100 rounded-lg" title="Edit">
                  <Edit2 className="w-4 h-4 text-gray-500" />
                </button>
                <button
                  className="p-2 hover:bg-red-50 rounded-lg"
                  title="Delete"
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Info */}
      <div className="bg-purple-50 rounded-xl p-5">
        <h3 className="font-semibold text-purple-900 mb-2">
          🔄 How rules work
        </h3>
        <p className="text-sm text-purple-700">
          Rules are checked in order of priority. When a comment matches a rule,
          the specified action is taken. Higher priority rules are checked first.
        </p>
      </div>
    </div>
  )
}
