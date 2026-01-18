import axios from 'axios'

// In production, VITE_API_URL is empty string which means same origin (relative URLs)
// Only fall back to localhost if the env var is completely undefined (local dev without .env)
const API_BASE_URL = import.meta.env.VITE_API_URL !== undefined
  ? import.meta.env.VITE_API_URL
  : 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth APIs
export const auth = {
  googleLogin: (idToken) => api.post('/auth/google', { id_token: idToken }),
  devLogin: () => api.post('/auth/dev-login'),
  getCurrentUser: () => api.get('/auth/me'),
}

// Onboarding APIs
export const onboarding = {
  start: () => api.get('/onboarding/start'),
  submitBaseline: () => api.post('/onboarding/baseline'),
  answerQuestion: (questionId, answer) =>
    api.post('/onboarding/answer', { question_id: questionId, answer }),
  completeOnboarding: () => api.post('/onboarding/complete'),
  getQuestions: () => api.get('/onboarding/questions'),
}

// Profile APIs
export const profile = {
  getProfile: () => api.get('/profile'),
  updateProfile: (data) => api.put('/profile', data),
}

// Recipe APIs
export const recipes = {
  generate: (mealType, additionalRequirements) =>
    api.post('/recipes/generate', null, {
      params: { meal_type: mealType, additional_requirements: additionalRequirements },
    }),
  list: (skip = 0, limit = 20) => api.get('/recipes', { params: { skip, limit } }),
  get: (id) => api.get(`/recipes/${id}`),
}

// Meal Plan APIs
export const mealPlans = {
  generate: (startDate) => api.post('/meal-plans/generate', null, { params: { start_date: startDate } }),
  list: () => api.get('/meal-plans'),
  get: (id) => api.get(`/meal-plans/${id}`),
}

export default api
