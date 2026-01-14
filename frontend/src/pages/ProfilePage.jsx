import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { profile as profileApi } from '../lib/api'

export default function ProfilePage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [profile, setProfile] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const response = await profileApi.getProfile()
      setProfile(response.data)
    } catch (err) {
      console.error('Error loading profile:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="min-h-screen pb-20">
      {/* Header */}
      <div className="glass dark:glass-dark sticky top-0 z-10 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors"
            >
              <svg className="w-6 h-6 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Profile</h1>
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-4 py-8">
        {/* User Info */}
        <div className="glass dark:glass-dark rounded-3xl p-8 mb-6">
          <div className="flex items-center gap-4 mb-6">
            <img
              src={user?.picture_url}
              alt={user?.name}
              className="w-20 h-20 rounded-full ring-4 ring-primary-500"
            />
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {user?.name}
              </h2>
              <p className="text-gray-600 dark:text-gray-300">{user?.email}</p>
            </div>
          </div>
        </div>

        {/* Profile Details */}
        {profile?.profile && (
          <div className="glass dark:glass-dark rounded-3xl p-8 mb-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
              Dietary Profile
            </h3>

            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Dietary Type</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                  {profile.profile.dietary_type || 'Not set'}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Cooking Time Preference</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                  {profile.profile.cooking_time_preference || 'Not set'}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Skill Level</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                  {profile.profile.skill_level || 'Not set'}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Cooking For</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {profile.profile.people_count || 1} {profile.profile.people_count === 1 ? 'person' : 'people'}
                </p>
              </div>

              {profile.profile.primary_goal && (
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Primary Goal</p>
                  <p className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
                    {profile.profile.primary_goal.replace('_', ' ')}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Dietary Restrictions */}
        {profile?.dietary_restrictions && profile.dietary_restrictions.length > 0 && (
          <div className="glass dark:glass-dark rounded-3xl p-8 mb-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Dietary Restrictions
            </h3>
            <div className="flex flex-wrap gap-2">
              {profile.dietary_restrictions.map((restriction) => (
                <span
                  key={restriction.id}
                  className="px-4 py-2 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded-xl font-medium"
                >
                  {restriction.restriction_value}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Nutritional Concerns */}
        {profile?.nutritional_concerns && profile.nutritional_concerns.length > 0 && (
          <div className="glass dark:glass-dark rounded-3xl p-8 mb-6">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Nutritional Focus
            </h3>
            <div className="space-y-4">
              {profile.nutritional_concerns.map((concern) => (
                <div key={concern.id} className="border-l-4 border-primary-500 pl-4">
                  <p className="font-semibold text-gray-900 dark:text-white capitalize">
                    {concern.nutrient.replace('_', ' ')}
                  </p>
                  {concern.notes && (
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      {concern.notes}
                    </p>
                  )}
                  {concern.recommended_sources && concern.recommended_sources.length > 0 && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                      Good sources: {concern.recommended_sources.join(', ')}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="space-y-3">
          <button
            onClick={() => navigate('/onboarding')}
            className="w-full glass dark:glass-dark hover:bg-gray-50 dark:hover:bg-gray-800/50 text-gray-900 dark:text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200"
          >
            Update Profile
          </button>

          <button
            onClick={handleLogout}
            className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-200"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}
