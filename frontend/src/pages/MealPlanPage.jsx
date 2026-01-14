import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { mealPlans } from '../lib/api'

export default function MealPlanPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [mealPlan, setMealPlan] = useState(null)
  const [selectedDay, setSelectedDay] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadMealPlan()
  }, [id])

  const loadMealPlan = async () => {
    setIsLoading(true)
    setError('')

    try {
      const response = await mealPlans.get(id)
      setMealPlan(response.data)
      if (response.data.daily_meals.length > 0) {
        setSelectedDay(response.data.daily_meals[0])
      }
    } catch (err) {
      console.error('Error loading meal plan:', err)
      setError(err.response?.data?.detail || 'Failed to load meal plan')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error || !mealPlan) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="glass dark:glass-dark rounded-3xl p-8 text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error || 'Meal plan not found'}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-primary-500 hover:bg-primary-600 text-white font-semibold py-3 px-6 rounded-xl"
          >
            Back to Dashboard
          </button>
        </div>
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
            <div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Weekly Meal Plan
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-300">
                {new Date(mealPlan.week_start_date).toLocaleDateString()} - {new Date(mealPlan.week_end_date).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Day Selector */}
        <div className="mb-6 overflow-x-auto pb-2">
          <div className="flex gap-2 min-w-max">
            {mealPlan.daily_meals.map((day) => {
              const dayDate = new Date(day.date)
              const dayName = dayDate.toLocaleDateString('en-US', { weekday: 'short' })
              const dayNum = dayDate.getDate()
              const isSelected = selectedDay?.date === day.date

              return (
                <button
                  key={day.date}
                  onClick={() => setSelectedDay(day)}
                  className={`flex flex-col items-center justify-center px-4 py-3 rounded-xl transition-all duration-200 ${
                    isSelected
                      ? 'bg-primary-500 text-white shadow-lg'
                      : 'glass dark:glass-dark text-gray-900 dark:text-white hover:shadow-md'
                  }`}
                >
                  <span className="text-xs font-medium mb-1">{dayName}</span>
                  <span className="text-2xl font-bold">{dayNum}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Meals for Selected Day */}
        {selectedDay && (
          <div className="space-y-4">
            {/* Breakfast */}
            {selectedDay.breakfast && (
              <MealCard meal={selectedDay.breakfast} type="Breakfast" icon="☀️" />
            )}

            {/* Snack 1 */}
            {selectedDay.snacks[0] && (
              <MealCard meal={selectedDay.snacks[0]} type="Morning Snack" icon="🍎" />
            )}

            {/* Lunch */}
            {selectedDay.lunch && (
              <MealCard meal={selectedDay.lunch} type="Lunch" icon="🌮" />
            )}

            {/* Snack 2 */}
            {selectedDay.snacks[1] && (
              <MealCard meal={selectedDay.snacks[1]} type="Afternoon Snack" icon="🥜" />
            )}

            {/* Dinner */}
            {selectedDay.dinner && (
              <MealCard meal={selectedDay.dinner} type="Dinner" icon="🍽️" />
            )}

            {/* Drink */}
            {selectedDay.drinks[0] && (
              <MealCard meal={selectedDay.drinks[0]} type="Healthy Drink" icon="🥤" />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function MealCard({ meal, type, icon }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="glass dark:glass-dark rounded-2xl overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-6 text-left hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{icon}</span>
              <span className="text-sm font-medium text-gray-600 dark:text-gray-300">{type}</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              {meal.title}
            </h3>
            {meal.description && (
              <p className="text-gray-600 dark:text-gray-300 text-sm mb-3">
                {meal.description}
              </p>
            )}
            <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
              <span>⏱️ {meal.total_time || (meal.prep_time + meal.cook_time)}min</span>
              <span>🔥 {meal.calories_per_serving}cal</span>
              {meal.protein_g && <span>💪 {meal.protein_g}g protein</span>}
            </div>
          </div>
          <svg
            className={`w-6 h-6 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {isExpanded && (
        <div className="px-6 pb-6 border-t border-gray-200 dark:border-gray-700 pt-6">
          {/* Ingredients */}
          <div className="mb-6">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Ingredients</h4>
            <ul className="space-y-2">
              {meal.ingredients.map((ingredient, idx) => (
                <li key={idx} className="flex items-start gap-2 text-gray-700 dark:text-gray-300">
                  <span className="text-primary-500 mt-1">•</span>
                  <span>{ingredient}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Instructions */}
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Instructions</h4>
            <ol className="space-y-3">
              {meal.instructions.map((instruction, idx) => (
                <li key={idx} className="flex gap-3 text-gray-700 dark:text-gray-300">
                  <span className="flex-shrink-0 w-6 h-6 bg-primary-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    {idx + 1}
                  </span>
                  <span className="pt-0.5">{instruction}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  )
}
