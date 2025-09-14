'use client'

import AccountSettings from './components/AccountSettings'
import AppearanceSettings from './components/AppearanceSettings'
import NotificationSettings from './components/NotificationSettings'
import IntegrationSettings from './components/IntegrationSettings'
import { Card } from '@/components/ui/card'

export default function SettingsPage() {
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">Manage your account, preferences, and integrations</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-6">
            <AccountSettings />
          </Card>

          <Card className="p-6">
            <AppearanceSettings />
          </Card>

          <Card className="p-6">
            <NotificationSettings />
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="p-6">
            <IntegrationSettings />
          </Card>
        </div>
      </div>
    </div>
  )
}


