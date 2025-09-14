'use client'

import { useState } from 'react'
import { User, Mail, Save } from 'lucide-react'

export default function AccountSettings() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Account</h2>
      <p className="text-sm text-gray-600">Update your personal information</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
        <div>
          <label className="block text-sm text-gray-600 mb-1">Name</label>
          <div className="flex items-center border rounded-lg px-3">
            <User className="w-4 h-4 text-gray-400 mr-2" />
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
              className="w-full py-2 outline-none"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Email</label>
          <div className="flex items-center border rounded-lg px-3">
            <Mail className="w-4 h-4 text-gray-400 mr-2" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="w-full py-2 outline-none"
            />
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-2">
        <button className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:shadow-lg transition">
          <Save className="w-4 h-4 mr-2" />
          Save changes
        </button>
      </div>
    </div>
  )
}


