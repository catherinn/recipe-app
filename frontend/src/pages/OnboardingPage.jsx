import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { onboarding } from '../lib/api'

export default function OnboardingPage() {
  const navigate = useNavigate()
  const [stage, setStage] = useState('baseline') // 'baseline', 'followup', 'complete'
  const [questions, setQuestions] = useState([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [followupInfo, setFollowupInfo] = useState(null)

  useEffect(() => {
    startOnboarding()
  }, [])

  const startOnboarding = async () => {
    setIsLoading(true)
    setError('')

    try {
      const response = await onboarding.start()
      setQuestions(response.data.questions)
      setStage('baseline')
      setCurrentQuestionIndex(0)
    } catch (err) {
      console.error('Error starting onboarding:', err)
      setError(err.response?.data?.detail || 'Failed to start onboarding')
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

      // Check if we've answered all questions in current stage
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1)
      } else {
        // Finished current stage
        if (stage === 'baseline') {
          // Submit baseline and get follow-up questions
          const followupResponse = await onboarding.submitBaseline()
          setQuestions(followupResponse.data.questions)
          setFollowupInfo({
            dietary_type: followupResponse.data.detected_dietary_type,
            concerns: followupResponse.data.nutritional_concerns
          })
          setStage('followup')
          setCurrentQuestionIndex(0)
        } else if (stage === 'followup') {
          // Complete onboarding
          await onboarding.completeOnboarding()
          setStage('complete')
          setTimeout(() => navigate('/dashboard'), 2000)
        }
      }
    } catch (err) {
      console.error('Error answering question:', err)
      setError(err.response?.data?.detail || 'Failed to save your answer')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading && questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const currentQuestion = questions[currentQuestionIndex]

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl fade-in">
        {/* Baseline or Follow-up Questions */}
        {(stage === 'baseline' || stage === 'followup') && currentQuestion && (
          <div className="glass dark:glass-dark rounded-3xl p-8 shadow-2xl">
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium text-gray-600 dark:text-gray-300">
                  {stage === 'baseline' ? 'Getting Started' : 'A Few More Things'}
                  {' • '}
                  {currentQuestionIndex + 1} of {questions.length}
                </span>
                <div className="flex gap-1">
                  {questions.map((_, idx) => (
                    <div
                      key={idx}
                      className={`h-1 w-8 rounded-full transition-all ${
                        idx <= currentQuestionIndex ? 'bg-primary-500' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    />
                  ))}
                </div>
              </div>

              {/* Show detected info after baseline */}
              {stage === 'followup' && currentQuestionIndex === 0 && followupInfo && (
                <div className="mb-6 p-4 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-xl">
                  <p className="text-sm text-primary-900 dark:text-primary-100 font-medium mb-2">
                    Based on your answers, you're <span className="capitalize">{followupInfo.dietary_type}</span>
                  </p>
                  {followupInfo.concerns && followupInfo.concerns.length > 0 && (
                    <p className="text-xs text-primary-700 dark:text-primary-300">
                      We'll help you focus on: {followupInfo.concerns.map(c => c.nutrient.replace('_', ' ')).join(', ')}
                    </p>
                  )}
                </div>
              )}

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
                    placeholder={currentQuestion.question_type === 'number' ? 'Enter a number...' : 'Your answer...'}
                    className="w-full p-4 bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 dark:text-white mb-4"
                    disabled={isLoading}
                    min={currentQuestion.question_type === 'number' ? '1' : undefined}
                    required
                  />
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-primary-500 hover:bg-primary-600 text-white font-semibold py-4 px-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {isLoading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>Saving...</span>
                      </>
                    ) : (
                      'Continue'
                    )}
                  </button>
                </form>
              )}
            </div>
          </div>
        )}

        {/* Completion */}
        {stage === 'complete' && (
          <div className="glass dark:glass-dark rounded-3xl p-8 shadow-2xl text-center">
            <div className="inline-block p-4 bg-primary-500 rounded-full mb-6">
              <svg className="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              You're all set!
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-8">
              Creating your personalized meal plan...
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
