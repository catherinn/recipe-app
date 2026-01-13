import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { onboarding } from '../lib/api'

export default function OnboardingPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [context, setContext] = useState('')
  const [questions, setQuestions] = useState([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleContextSubmit = async (e) => {
    e.preventDefault()
    if (!context.trim()) return

    setIsLoading(true)
    setError('')

    try {
      const response = await onboarding.submitContext(context)
      setQuestions(response.data.questions)
      setStep(2)
    } catch (err) {
      console.error('Error submitting context:', err)
      setError(err.response?.data?.detail || 'Failed to process your information')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAnswerQuestion = async (answer) => {
    const currentQuestion = questions[currentQuestionIndex]

    setIsLoading(true)
    setError('')

    try {
      await onboarding.answerQuestion(currentQuestion.id, answer)
      setAnswers({ ...answers, [currentQuestion.id]: answer })

      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1)
      } else {
        // All questions answered, complete onboarding
        await onboarding.completeOnboarding()
        setStep(3)
        setTimeout(() => navigate('/dashboard'), 2000)
      }
    } catch (err) {
      console.error('Error answering question:', err)
      setError(err.response?.data?.detail || 'Failed to save your answer')
    } finally {
      setIsLoading(false)
    }
  }

  const currentQuestion = questions[currentQuestionIndex]

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl fade-in">
        {/* Step 1: Context Input */}
        {step === 1 && (
          <div className="glass dark:glass-dark rounded-3xl p-8 shadow-2xl">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Tell us about yourself
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-8">
              Share your dietary preferences, restrictions, goals, or anything else that's important to you.
              We'll use AI to ask the right follow-up questions.
            </p>

            <form onSubmit={handleContextSubmit}>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="Example: I'm vegetarian and trying to eat healthier. I don't have much time to cook during weekdays..."
                className="w-full h-48 p-4 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 dark:text-white resize-none"
                disabled={isLoading}
              />

              {error && (
                <div className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
                  <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={!context.trim() || isLoading}
                className="mt-6 w-full bg-primary-500 hover:bg-primary-600 text-white font-semibold py-4 px-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Analyzing...</span>
                  </div>
                ) : (
                  'Continue'
                )}
              </button>
            </form>
          </div>
        )}

        {/* Step 2: Questions */}
        {step === 2 && currentQuestion && (
          <div className="glass dark:glass-dark rounded-3xl p-8 shadow-2xl">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                  Question {currentQuestionIndex + 1} of {questions.length}
                </span>
                <div className="flex gap-1">
                  {questions.map((_, idx) => (
                    <div
                      key={idx}
                      className={`h-1 w-8 rounded-full ${
                        idx <= currentQuestionIndex ? 'bg-primary-500' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    />
                  ))}
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {currentQuestion.question_text}
              </h3>
              {currentQuestion.research_context && (
                <p className="text-sm text-gray-500 dark:text-gray-400 italic">
                  {currentQuestion.research_context}
                </p>
              )}
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
                <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
              </div>
            )}

            <div className="space-y-4">
              {currentQuestion.question_type === 'yes_no' && (
                <div className="grid grid-cols-2 gap-4">
                  <button
                    onClick={() => handleAnswerQuestion('yes')}
                    disabled={isLoading}
                    className="py-4 px-6 bg-white dark:bg-gray-800 hover:bg-primary-50 dark:hover:bg-primary-900/20 border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 rounded-xl font-semibold text-gray-900 dark:text-white transition-all duration-200 disabled:opacity-50"
                  >
                    Yes
                  </button>
                  <button
                    onClick={() => handleAnswerQuestion('no')}
                    disabled={isLoading}
                    className="py-4 px-6 bg-white dark:bg-gray-800 hover:bg-primary-50 dark:hover:bg-primary-900/20 border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 rounded-xl font-semibold text-gray-900 dark:text-white transition-all duration-200 disabled:opacity-50"
                  >
                    No
                  </button>
                </div>
              )}

              {currentQuestion.question_type === 'multiple_choice' && (
                <div className="space-y-3">
                  {currentQuestion.options.map((option) => (
                    <button
                      key={option}
                      onClick={() => handleAnswerQuestion(option)}
                      disabled={isLoading}
                      className="w-full py-4 px-6 bg-white dark:bg-gray-800 hover:bg-primary-50 dark:hover:bg-primary-900/20 border-2 border-gray-200 dark:border-gray-700 hover:border-primary-500 rounded-xl font-semibold text-gray-900 dark:text-white text-left transition-all duration-200 disabled:opacity-50"
                    >
                      {option}
                    </button>
                  ))}
                </div>
              )}

              {(currentQuestion.question_type === 'text' || currentQuestion.question_type === 'number') && (
                <form
                  onSubmit={(e) => {
                    e.preventDefault()
                    const answer = e.target.answer.value
                    if (answer.trim()) handleAnswerQuestion(answer)
                  }}
                >
                  <input
                    type={currentQuestion.question_type === 'number' ? 'number' : 'text'}
                    name="answer"
                    placeholder="Your answer..."
                    className="w-full p-4 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 dark:text-white mb-4"
                    disabled={isLoading}
                  />
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-primary-500 hover:bg-primary-600 text-white font-semibold py-4 px-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? 'Saving...' : 'Continue'}
                  </button>
                </form>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Completion */}
        {step === 3 && (
          <div className="glass dark:glass-dark rounded-3xl p-8 shadow-2xl text-center">
            <div className="inline-block p-4 bg-primary-500 rounded-full mb-6">
              <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              All set!
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-8">
              We're creating your personalized meal plan...
            </p>
            <div className="flex justify-center">
              <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
