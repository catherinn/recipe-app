# Recipe App - AI-Powered Personalized Meal Planning

A mobile-responsive web application that creates personalized meal plans based on your dietary needs, preferences, and goals using AI.

## Features

- 🔐 **Google OAuth Authentication** - Secure sign-in
- 🤖 **AI-Powered Onboarding** - Dynamic question generation based on your dietary context
- 🥗 **Personalized Meal Plans** - Weekly plans with breakfast, lunch, dinner, snacks, and drinks
- 🔬 **Research-Based Nutrition** - Nutritional recommendations based on scientific research
- 📱 **Mobile-Responsive Design** - Beautiful UI inspired by Airbnb, Notion, and Headspace
- 🌙 **Dark Mode Support** - Comfortable viewing in any lighting

## Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - ORM for SQLite database
- **Anthropic Claude API** - AI-powered recipe generation and question generation
- **Google OAuth 2.0** - Authentication

### Frontend
- **React 18** - UI library
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS
- **Zustand** - State management
- **Axios** - HTTP client

### Deployment
- **Railway** - Auto-deploy from GitHub with CI/CD

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anthropic API key
- Google OAuth credentials

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Configure environment variables in `.env`:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET_KEY=generate_with_openssl_rand_hex_32
DATABASE_URL=sqlite:///./recipe_app.db
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

6. Initialize database:
```bash
python -c "from database import init_db; init_db()"
```

7. Run the server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Configure environment variables in `.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_google_client_id
```

5. Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Railway Deployment

### Prerequisites
- Railway account
- GitHub repository connected to Railway
- Environment variables set in Railway dashboard

### Environment Variables to Set in Railway

```
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URL=sqlite:////app/data/recipe_app.db
FRONTEND_URL=https://your-app.railway.app
BACKEND_URL=https://your-app.railway.app
PORT=8000
```

### Volume Setup in Railway
1. Create a volume named `data`
2. Mount point: `/app/data`
3. This persists your SQLite database across deployments

### Deployment
Railway will automatically:
1. Detect Python and Node.js
2. Install backend dependencies
3. Install and build frontend
4. Start the FastAPI server
5. Serve frontend from backend

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
recipe-app/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── onboarding.py
│   │   ├── profile.py
│   │   ├── recipes.py
│   │   └── meal_plans.py
│   └── services/            # Business logic
│       ├── auth_service.py
│       ├── research_service.py
│       └── recipe_service.py
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── lib/             # API client
│   │   ├── store/           # State management
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   ├── vite.config.js
│   └── tailwind.config.js
├── schema.sql               # Database schema
├── railway.json             # Railway config
└── README.md
```

## Usage Flow

1. **Sign In** - Use Google OAuth to authenticate
2. **Onboarding** - Share your dietary context (e.g., "I'm vegetarian and want to lose weight")
3. **Answer Questions** - AI generates personalized questions based on your context
4. **Generate Meal Plan** - Create a weekly meal plan tailored to your needs
5. **View Recipes** - Browse detailed recipes with ingredients and instructions
6. **Track Progress** - Mark meals as completed

## Design Inspiration

The UI design is inspired by:
- **Airbnb** - Large imagery, ample white space, smart filtering
- **Notion** - Minimalist approach, collapsible sections
- **Headspace/Calm** - Soothing colors, accessibility-first

## Key Features

### Dynamic Onboarding
- Uses Claude AI to analyze your dietary context
- Generates relevant follow-up questions based on research
- Identifies nutritional concerns (e.g., B12 for vegetarians)

### AI Recipe Generation
- Considers your dietary type, restrictions, and goals
- Addresses nutritional concerns through food choices
- Adjusts for cooking time preferences and skill level

### Weekly Meal Plans
- Complete 7-day plans with all meals
- Breakfast, lunch, dinner, 2 snacks, and a healthy drink per day
- Varied recipes with no repetition
- Nutritionally balanced

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
