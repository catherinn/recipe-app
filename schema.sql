-- Recipe App Database Schema

-- Users table (from Google OAuth)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    picture_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User profiles (extended preferences)
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    -- Cooking preferences
    cooking_time_preference TEXT, -- 'quick' (15-30min), 'medium' (30-60min), 'long' (60+ min)
    skill_level TEXT, -- 'beginner', 'intermediate', 'advanced'
    people_count INTEGER DEFAULT 1,

    -- Goals and preferences
    primary_goal TEXT, -- e.g., 'weight_loss', 'muscle_gain', 'health', 'convenience'
    likes TEXT, -- JSON array of liked ingredients/cuisines
    dislikes TEXT, -- JSON array of disliked ingredients/cuisines

    -- Dietary context (free-form + structured)
    dietary_context TEXT, -- Original free-form context from user
    dietary_type TEXT, -- 'omnivore', 'vegetarian', 'vegan', 'pescatarian', 'flexitarian'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User dietary restrictions (structured from questions)
CREATE TABLE dietary_restrictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    restriction_type TEXT NOT NULL, -- 'allergy', 'intolerance', 'preference', 'religious', 'ethical'
    restriction_value TEXT NOT NULL, -- e.g., 'gluten', 'dairy', 'pork', 'beef'
    severity TEXT, -- 'strict', 'moderate', 'flexible'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Nutritional concerns (auto-detected from context)
CREATE TABLE nutritional_concerns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nutrient TEXT NOT NULL, -- e.g., 'vitamin_b12', 'iron', 'protein', 'omega3'
    concern_level TEXT, -- 'at_risk', 'monitor', 'supplement'
    recommended_sources TEXT, -- JSON array of food sources
    notes TEXT, -- Research-based recommendations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Dynamic onboarding questions (generated from research)
CREATE TABLE onboarding_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL, -- 'yes_no', 'multiple_choice', 'text', 'number'
    options TEXT, -- JSON array for multiple choice
    answer TEXT,
    research_context TEXT, -- Why this question was asked
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answered_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Meal plans (weekly)
CREATE TABLE meal_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    status TEXT DEFAULT 'active', -- 'active', 'completed', 'archived'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Recipes
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, -- NULL if it's a template recipe
    title TEXT NOT NULL,
    description TEXT,
    cuisine_type TEXT,
    prep_time INTEGER, -- minutes
    cook_time INTEGER, -- minutes
    total_time INTEGER, -- minutes
    servings INTEGER DEFAULT 1,
    difficulty TEXT, -- 'easy', 'medium', 'hard'

    -- Recipe content
    ingredients TEXT NOT NULL, -- JSON array
    instructions TEXT NOT NULL, -- JSON array of steps

    -- Nutritional info
    calories_per_serving INTEGER,
    protein_g REAL,
    carbs_g REAL,
    fat_g REAL,
    fiber_g REAL,
    nutritional_highlights TEXT, -- JSON array (e.g., ['high_protein', 'vitamin_b12_rich'])

    -- Source and generation
    source_url TEXT, -- If scraped from website
    generated_by TEXT DEFAULT 'ai', -- 'ai', 'user', 'scraped'
    generation_prompt TEXT, -- Original prompt used to generate

    image_url TEXT,
    tags TEXT, -- JSON array

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Meals (individual entries in meal plans)
CREATE TABLE meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_plan_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    meal_date DATE NOT NULL,
    meal_type TEXT NOT NULL, -- 'breakfast', 'lunch', 'dinner', 'snack', 'drink'
    meal_order INTEGER DEFAULT 0, -- For multiple snacks/drinks
    notes TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (meal_plan_id) REFERENCES meal_plans(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

-- User feedback on recipes (to improve future recommendations)
CREATE TABLE recipe_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recipe_id INTEGER NOT NULL,
    rating INTEGER CHECK(rating >= 1 AND rating <= 5),
    liked BOOLEAN,
    made_it BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
    UNIQUE(user_id, recipe_id)
);

-- Indexes for performance
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_dietary_restrictions_user_id ON dietary_restrictions(user_id);
CREATE INDEX idx_nutritional_concerns_user_id ON nutritional_concerns(user_id);
CREATE INDEX idx_meal_plans_user_id ON meal_plans(user_id);
CREATE INDEX idx_meal_plans_dates ON meal_plans(week_start_date, week_end_date);
CREATE INDEX idx_recipes_user_id ON recipes(user_id);
CREATE INDEX idx_meals_meal_plan_id ON meals(meal_plan_id);
CREATE INDEX idx_meals_date ON meals(meal_date);
CREATE INDEX idx_recipe_feedback_user_id ON recipe_feedback(user_id);
