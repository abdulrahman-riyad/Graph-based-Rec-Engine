'use client'

import { useState } from 'react'
import { Bell, Mail, MessageSquare } from 'lucide-react'

export default function NotificationSettings() {
  const [emailNotifs, setEmailNotifs] = useState(true)
  const [inAppNotifs, setInAppNotifs] = useState(true)
  const [weeklyDigest, setWeeklyDigest] = useState(false)

  const Toggle = ({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) => (
    <button
      onClick={() => onChange(!checked)}
      className={`w-12 h-6 rounded-full transition ${checked ? 'bg-purple-600' : 'bg-gray-300'}`}
      aria-pressed={checked}
    >
      <span
        className={`block w-5 h-5 bg-white rounded-full shadow transform transition ${checked ? 'translate-x-6' : 'translate-x-1'}`}
      />
    </button>
  )

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Notifications</h2>
      <p className="text-sm text-gray-600">Select how you want to be notified</p>

      <div className="space-y-3 pt-2">
        <div className="flex items-center justify-between p-3 border rounded-lg">
          <div className="flex items-center space-x-3">
            <Mail className="w-5 h-5 text-gray-500" />
            <div>
              <p className="font-medium text-gray-900 text-sm">Email notifications</p>
              <p className="text-xs text-gray-600">Order summaries, reports, and alerts</p>
            </div>
          </div>
          <Toggle checked={emailNotifs} onChange={setEmailNotifs} />
        </div>

        <div className="flex items-center justify-between p-3 border rounded-lg">
          <div className="flex items-center space-x-3">
            <Bell className="w-5 h-5 text-gray-500" />
            <div>
              <p className="font-medium text-gray-900 text-sm">In-app notifications</p>
              <p className="text-xs text-gray-600">Real-time insights and recommendations</p>
            </div>
          </div>
          <Toggle checked={inAppNotifs} onChange={setInAppNotifs} />
        </div>

        <div className="flex items-center justify-between p-3 border rounded-lg">
          <div className="flex items-center space-x-3">
            <MessageSquare className="w-5 h-5 text-gray-500" />
            <div>
              <p className="font-medium text-gray-900 text-sm">Weekly digest</p>
              <p className="text-xs text-gray-600">Summary of key metrics and trends</p>
            </div>
          </div>
          <Toggle checked={weeklyDigest} onChange={setWeeklyDigest} />
        </div>
      </div>
    </div>
  )
}


