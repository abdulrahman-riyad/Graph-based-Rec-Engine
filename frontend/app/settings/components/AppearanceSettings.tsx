'use client'

import { useState, useEffect } from 'react'
import { Sun, Moon, Monitor } from 'lucide-react'

export default function AppearanceSettings() {
  const [theme, setTheme] = useState<'system' | 'light' | 'dark'>('system')

  useEffect(() => {
    if (theme === 'system') {
      document.documentElement.classList.remove('dark')
      return
    }
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])

  const Option = ({ value, label, Icon }: any) => (
    <label className={`flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:bg-gray-50 ${theme === value ? 'border-purple-500' : ''}`}>
      <div className="flex items-center space-x-3">
        <Icon className="w-5 h-5 text-gray-500" />
        <span className="text-sm text-gray-800">{label}</span>
      </div>
      <input
        type="radio"
        name="theme"
        value={value}
        checked={theme === value}
        onChange={() => setTheme(value)}
      />
    </label>
  )

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Appearance</h2>
      <p className="text-sm text-gray-600">Customize how the dashboard looks</p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
        <Option value="system" label="System" Icon={Monitor} />
        <Option value="light" label="Light" Icon={Sun} />
        <Option value="dark" label="Dark" Icon={Moon} />
      </div>
    </div>
  )
}


