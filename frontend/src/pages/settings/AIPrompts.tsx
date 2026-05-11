/**
 * AI Prompts Settings Page
 * Created by: Karim (Frontend Lead)
 */

import { useState } from 'react'
import { ArrowLeft, Plus, Edit2, Trash2, Star, Copy } from 'lucide-react'
import { Link } from 'react-router-dom'

const prompts = [
  {
    id: '1',
    name: 'Default Professional',
    description: 'Professional and courteous responses',
    tone: 'professional',
    language: 'bn',
    isDefault: true,
    timesUsed: 1234,
  },
  {
    id: '2',
    name: 'Friendly Support',
    description: 'Warm and friendly customer support tone',
    tone: 'friendly',
    language: 'bn',
    isDefault: false,
    timesUsed: 567,
  },
]

export default function AIPrompts() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            to="/settings"
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Prompts</h1>
            <p className="text-gray-600 mt-1">
              Customize how AI generates replies
            </p>
          </div>
        </div>
        <button className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          New Prompt
        </button>
      </div>

      {/* Prompts list */}
      <div className="space-y-4">
        {prompts.map((prompt) => (
          <div key={prompt.id} className="card p-5">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-accent-100 rounded-lg flex items-center justify-center">
                  <span className="text-accent-600 font-bold">
                    {prompt.name.charAt(0)}
                  </span>
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900">{prompt.name}</h3>
                    {prompt.isDefault && (
                      <span className="flex items-center gap-1 text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">
                        <Star className="w-3 h-3" />
                        Default
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-500 mt-0.5">
                    {prompt.description}
                  </p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                    <span>Tone: {prompt.tone}</span>
                    <span>Language: {prompt.language.toUpperCase()}</span>
                    <span>Used: {prompt.timesUsed} times</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button className="p-2 hover:bg-gray-100 rounded-lg" title="Edit">
                  <Edit2 className="w-4 h-4 text-gray-500" />
                </button>
                <button className="p-2 hover:bg-gray-100 rounded-lg" title="Duplicate">
                  <Copy className="w-4 h-4 text-gray-500" />
                </button>
                {!prompt.isDefault && (
                  <button className="p-2 hover:bg-red-50 rounded-lg" title="Delete">
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Tips */}
      <div className="bg-blue-50 rounded-xl p-5">
        <h3 className="font-semibold text-blue-900 mb-2">
          💡 Tips for better prompts
        </h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Be specific about the tone and style you want</li>
          <li>• Include context about your business</li>
          <li>• Define what the AI should NOT say</li>
          <li>• Test prompts before setting as default</li>
        </ul>
      </div>
    </div>
  )
}
