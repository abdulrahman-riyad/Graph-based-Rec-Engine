export default function TestPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-pink-600 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">Tailwind CSS Test</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6 hover:scale-105 transition-transform">
            <div className="w-12 h-12 bg-blue-500 rounded-full mb-4"></div>
            <h2 className="text-xl font-semibold mb-2">Blue Card</h2>
            <p className="text-gray-600">If you see this styled, Tailwind is working!</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6 hover:scale-105 transition-transform">
            <div className="w-12 h-12 bg-green-500 rounded-full mb-4"></div>
            <h2 className="text-xl font-semibold mb-2">Green Card</h2>
            <p className="text-gray-600">Hover effects should work too!</p>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6 hover:scale-105 transition-transform">
            <div className="w-12 h-12 bg-red-500 rounded-full mb-4"></div>
            <h2 className="text-xl font-semibold mb-2">Red Card</h2>
            <p className="text-gray-600">Responsive grid layout!</p>
          </div>
        </div>
        
        <button className="mt-8 px-6 py-3 bg-white text-purple-600 font-semibold rounded-lg shadow-lg hover:shadow-xl transition-shadow">
          Test Button
        </button>
      </div>
    </div>
  )
}