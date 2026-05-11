/**
 * Settings Page
 * Created by: Karim (Frontend Lead)
 */

import { Link } from 'react-router-dom'
import {
  Building2,
  User,
  Bell,
  Key,
  Wand2,
  GitBranch,
  Globe,
  Palette,
} from 'lucide-react'

const settingsCategories = [
  {
    title: 'Organization',
    description: 'Manage your organization details',
    icon: Building2,
    href: '/settings/organization',
  },
  {
    title: 'Profile',
    description: 'Update your personal information',
    icon: User,
    href: '/settings/profile',
  },
  {
    title: 'AI Prompts',
    description: 'Customize AI reply behavior',
    icon: Wand2,
    href: '/settings/prompts',
  },
  {
    title: 'Reply Rules',
    description: 'Set up automated reply rules',
    icon: GitBranch,
    href: '/settings/rules',
  },
  {
    title: 'Notifications',
    description: 'Manage notification preferences',
    icon: Bell,
    href: '/settings/notifications',
  },
  {
    title: 'Security',
    description: 'Password and security settings',
    icon: Key,
    href: '/settings/security',
  },
  {
    title: 'Language',
    description: 'Language and regional settings',
    icon: Globe,
    href: '/settings/language',
  },
  {
    title: 'Appearance',
    description: 'Theme and display preferences',
    icon: Palette,
    href: '/settings/appearance',
  },
]

export default function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">
          Manage your account and application settings
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {settingsCategories.map((category) => (
          <Link
            key={category.title}
            to={category.href}
            className="card p-5 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 bg-primary-50 rounded-lg flex items-center justify-center flex-shrink-0">
                <category.icon className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{category.title}</h3>
                <p className="text-sm text-gray-500 mt-0.5">
                  {category.description}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
