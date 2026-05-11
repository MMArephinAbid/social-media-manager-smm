/**
 * Dashboard Page
 * Created by: Karim (Frontend Lead)
 */

import {
  MessageSquare,
  ThumbsUp,
  Zap,
  Clock,
  TrendingUp,
  Facebook,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/utils/cn'

interface StatCard {
  title: string
  value: string
  change: number
  changeLabel: string
  icon: React.ElementType
  color: 'blue' | 'green' | 'purple' | 'orange'
}

const stats: StatCard[] = [
  {
    title: 'Total Replies',
    value: '1,234',
    change: 12.5,
    changeLabel: 'vs last month',
    icon: MessageSquare,
    color: 'blue',
  },
  {
    title: 'Response Rate',
    value: '98.2%',
    change: 2.1,
    changeLabel: 'vs last month',
    icon: ThumbsUp,
    color: 'green',
  },
  {
    title: 'Avg. Response Time',
    value: '45s',
    change: -15,
    changeLabel: 'vs last month',
    icon: Clock,
    color: 'purple',
  },
  {
    title: 'AI Tokens Used',
    value: '45.2K',
    change: 8.3,
    changeLabel: 'vs last month',
    icon: Zap,
    color: 'orange',
  },
]

const colorClasses = {
  blue: {
    bg: 'bg-blue-50',
    text: 'text-blue-600',
    icon: 'bg-blue-100',
  },
  green: {
    bg: 'bg-green-50',
    text: 'text-green-600',
    icon: 'bg-green-100',
  },
  purple: {
    bg: 'bg-purple-50',
    text: 'text-purple-600',
    icon: 'bg-purple-100',
  },
  orange: {
    bg: 'bg-orange-50',
    text: 'text-orange-600',
    icon: 'bg-orange-100',
  },
}

const recentComments = [
  {
    id: 1,
    page: 'My Business Page',
    commenter: 'আহমেদ আলী',
    comment: 'আপনাদের পণ্যের দাম কত?',
    reply: 'ধন্যবাদ আপনার আগ্রহের জন্য! আমাদের পণ্যের দাম ₹499 থেকে শুরু...',
    status: 'replied',
    time: '2 min ago',
  },
  {
    id: 2,
    page: 'My Business Page',
    commenter: 'ফাতেমা খান',
    comment: 'ডেলিভারি কতদিন লাগে?',
    reply: 'সাধারণত ২-৩ কার্যদিবসের মধ্যে ডেলিভারি হয়ে যায়...',
    status: 'replied',
    time: '5 min ago',
  },
  {
    id: 3,
    page: 'Second Page',
    commenter: 'করিম সাহেব',
    comment: 'খুব ভালো সার্ভিস!',
    reply: null,
    status: 'pending',
    time: '10 min ago',
  },
]

export default function Dashboard() {
  const { user, organization, subscription } = useAuthStore()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          স্বাগতম, {user?.first_name}! 👋
        </h1>
        <p className="text-gray-600 mt-1">
          আপনার Facebook পেজের সারসংক্ষেপ দেখুন
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div
            key={stat.title}
            className={cn('card p-5', colorClasses[stat.color].bg)}
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {stat.value}
                </p>
              </div>
              <div
                className={cn(
                  'w-10 h-10 rounded-lg flex items-center justify-center',
                  colorClasses[stat.color].icon
                )}
              >
                <stat.icon
                  className={cn('w-5 h-5', colorClasses[stat.color].text)}
                />
              </div>
            </div>
            <div className="flex items-center gap-1 mt-3">
              {stat.change > 0 ? (
                <ArrowUpRight className="w-4 h-4 text-green-500" />
              ) : (
                <ArrowDownRight className="w-4 h-4 text-red-500" />
              )}
              <span
                className={cn(
                  'text-sm font-medium',
                  stat.change > 0 ? 'text-green-600' : 'text-red-600'
                )}
              >
                {Math.abs(stat.change)}%
              </span>
              <span className="text-sm text-gray-500">{stat.changeLabel}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Comments */}
        <div className="lg:col-span-2 card">
          <div className="p-5 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-gray-900">সাম্প্রতিক মন্তব্য</h2>
              <a
                href="/comments"
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                সব দেখুন
              </a>
            </div>
          </div>
          <div className="divide-y divide-gray-100">
            {recentComments.map((item) => (
              <div key={item.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Facebook className="w-5 h-5 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 truncate">
                        {item.commenter}
                      </span>
                      <span className="text-xs text-gray-400">{item.time}</span>
                      {item.status === 'replied' ? (
                        <span className="badge-success">Replied</span>
                      ) : (
                        <span className="badge-warning">Pending</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 mt-1 font-bengali">
                      "{item.comment}"
                    </p>
                    {item.reply && (
                      <p className="text-sm text-gray-500 mt-2 pl-3 border-l-2 border-primary-200 font-bengali">
                        {item.reply}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions & Info */}
        <div className="space-y-6">
          {/* Connected Pages */}
          <div className="card p-5">
            <h2 className="font-semibold text-gray-900 mb-4">সংযুক্ত পেজ</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Facebook className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">My Business Page</p>
                  <p className="text-xs text-gray-500">12.5K followers</p>
                </div>
                <span className="w-2 h-2 bg-green-500 rounded-full" />
              </div>
            </div>
            <a
              href="/pages/connect"
              className="block mt-4 text-center text-sm text-primary-600 hover:text-primary-700"
            >
              + নতুন পেজ যুক্ত করুন
            </a>
          </div>

          {/* Plan Info */}
          {subscription && (
            <div className="card p-5 bg-gradient-to-br from-primary-50 to-accent-50">
              <h2 className="font-semibold text-gray-900 mb-3">আপনার প্ল্যান</h2>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-2xl font-bold text-primary-600">
                  {subscription.plan_name}
                </span>
                {subscription.status === 'trialing' && (
                  <span className="badge-info">Trial</span>
                )}
              </div>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Replies used</span>
                    <span>
                      {subscription.replies_used}/{subscription.replies_limit}
                    </span>
                  </div>
                  <div className="h-2 bg-white rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 rounded-full"
                      style={{
                        width: `${Math.min(
                          (subscription.replies_used /
                            subscription.replies_limit) *
                            100,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
              <a
                href="/billing"
                className="block mt-4 btn-primary text-center text-sm"
              >
                আপগ্রেড করুন
              </a>
            </div>
          )}

          {/* Tips */}
          <div className="card p-5">
            <h2 className="font-semibold text-gray-900 mb-3">💡 Quick Tips</h2>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex gap-2">
                <TrendingUp className="w-4 h-4 text-primary-500 flex-shrink-0 mt-0.5" />
                <span>Set up custom AI prompts for better replies</span>
              </li>
              <li className="flex gap-2">
                <TrendingUp className="w-4 h-4 text-primary-500 flex-shrink-0 mt-0.5" />
                <span>Configure reply rules to handle common questions</span>
              </li>
              <li className="flex gap-2">
                <TrendingUp className="w-4 h-4 text-primary-500 flex-shrink-0 mt-0.5" />
                <span>Monitor analytics to improve response quality</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
