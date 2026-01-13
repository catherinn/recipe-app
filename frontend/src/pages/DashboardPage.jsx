import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { mealPlans, profile as profileApi } from '../lib/api'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [profile, setProfile] = useState(null)
  const [mealPlansList, setMealPlansList] = useState([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [profileRes, mealPlansRes] = await Promise.all([
        profileApi.getProfile().catch(() => null),
        mealPlans.list().catch(() => ({ data: [] }))
      ])

      if (profileRes) {
        setProfile(profileRes.data.profile)
      }
      setMealPlansList(mealPlansRes.data || [])
    } catch (err) {
      console.error('Error loading data:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateMealPlan = async () => {
    if (!profile) {
      navigate('/onboarding')
      return
    }

    setIsGenerating(true)
    setError('')

    try {
      const response = await mealPlans.generate()
      const newMealPlanId = response.data.meal_plan_id
      navigate(`/meal-plan/${newMealPlanId}`)
    } catch (err) {
      console.error('Error generating meal plan:', err)
      setError(err.response?.data?.detail || 'Failed to generate meal plan')
    } finally {
      setIsGenerating(false)
    }
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
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <img
                src={user?.picture_url}
                alt={user?.name}
                className="w-12 h-12 rounded-full ring-2 ring-primary-500"
              />
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  {user?.name}
                </h1>
                {profile && (
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    {profile.dietary_type || 'Omnivore'}
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={() => navigate('/profile')}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-colors"
            >
              <svg className="w-6 h-6 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* No Profile - Onboarding CTA */}
        {!profile && (
          <div className="glass dark:glass-dark rounded-3xl p-8 text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Complete your profile
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Tell us about your dietary preferences to get personalized meal plans
            </p>
            <button
              onClick={() => navigate('/onboarding')}
              className="bg-primary-500 hover:bg-primary-600 text-white font-semibold py-3 px-8 rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
            >
              Get Started
            </button>
          </div>
        )}

        {/* Generate Meal Plan CTA */}
        {profile && (
          <div className="glass dark:glass-dark rounded-3xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Weekly Meal Plan
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Generate a personalized weekly meal plan with breakfast, lunch, dinner, snacks, and drinks
            </p>

            {error && (
              <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
                <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              onClick={handleGenerateMealPlan}
              disabled={isGenerating}
              className="bg-primary-500 hover:bg-primary-600 text-white font-semibold py-4 px-8 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isGenerating ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Generating...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <span>Generate New Meal Plan</span>
                </>
              )}
            </button>
          </div>
        )}

        {/* Meal Plans List */}
        {mealPlansList.length > 0 && (
          <div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Your Meal Plans
            </h3>
            <div className="grid gap-4">
              {mealPlansList.map((plan) => (
                <button
                  key={plan.id}
                  onClick={() => navigate(`/meal-plan/${plan.id}`)}
                  className="glass dark:glass-dark rounded-2xl p-6 text-left hover:shadow-lg transition-all duration-200"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-lg font-semibold text-gray-900 dark:text-white">
                        Week of {new Date(plan.week_start_date).toLocaleDateString()}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        {new Date(plan.week_start_date).toLocaleDateString()} - {new Date(plan.week_end_date).toLocaleDateString()}
                      </p>
                    </div>
                    <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
