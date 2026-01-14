from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, TIMESTAMP, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import json


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    picture_url = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    dietary_restrictions = relationship("DietaryRestriction", back_populates="user", cascade="all, delete-orphan")
    nutritional_concerns = relationship("NutritionalConcern", back_populates="user", cascade="all, delete-orphan")
    onboarding_questions = relationship("OnboardingQuestion", back_populates="user", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")
    recipes = relationship("Recipe", back_populates="user", cascade="all, delete-orphan")
    recipe_feedback = relationship("RecipeFeedback", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Cooking preferences
    cooking_time_preference = Column(String)  # 'quick', 'medium', 'long'
    skill_level = Column(String)  # 'beginner', 'intermediate', 'advanced'
    people_count = Column(Integer, default=1)

    # Goals and preferences
    primary_goal = Column(String)
    likes = Column(Text)  # JSON array
    dislikes = Column(Text)  # JSON array

    # Dietary context
    dietary_context = Column(Text)  # Original free-form context
    dietary_type = Column(String)  # 'omnivore', 'vegetarian', 'vegan', 'pescatarian', 'flexitarian'

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="profile")

    def set_likes(self, likes_list):
        self.likes = json.dumps(likes_list)

    def get_likes(self):
        return json.loads(self.likes) if self.likes else []

    def set_dislikes(self, dislikes_list):
        self.dislikes = json.dumps(dislikes_list)

    def get_dislikes(self):
        return json.loads(self.dislikes) if self.dislikes else []


class DietaryRestriction(Base):
    __tablename__ = "dietary_restrictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    restriction_type = Column(String, nullable=False)  # 'allergy', 'intolerance', 'preference', 'religious', 'ethical'
    restriction_value = Column(String, nullable=False)
    severity = Column(String)  # 'strict', 'moderate', 'flexible'
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="dietary_restrictions")


class NutritionalConcern(Base):
    __tablename__ = "nutritional_concerns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    nutrient = Column(String, nullable=False)
    concern_level = Column(String)  # 'at_risk', 'monitor', 'supplement'
    recommended_sources = Column(Text)  # JSON array
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="nutritional_concerns")

    def set_recommended_sources(self, sources_list):
        self.recommended_sources = json.dumps(sources_list)

    def get_recommended_sources(self):
        return json.loads(self.recommended_sources) if self.recommended_sources else []


class OnboardingQuestion(Base):
    __tablename__ = "onboarding_questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # 'yes_no', 'multiple_choice', 'text', 'number'
    options = Column(Text)  # JSON array for multiple choice
    answer = Column(Text)
    research_context = Column(Text)  # Why this question was asked
    asked_at = Column(TIMESTAMP, server_default=func.now())
    answered_at = Column(TIMESTAMP)

    # Relationships
    user = relationship("User", back_populates="onboarding_questions")

    def set_options(self, options_list):
        self.options = json.dumps(options_list)

    def get_options(self):
        return json.loads(self.options) if self.options else []


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    week_start_date = Column(Date, nullable=False, index=True)
    week_end_date = Column(Date, nullable=False, index=True)
    status = Column(String, default='active')  # 'active', 'completed', 'archived'
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="meal_plans")
    meals = relationship("Meal", back_populates="meal_plan", cascade="all, delete-orphan")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    cuisine_type = Column(String)
    prep_time = Column(Integer)  # minutes
    cook_time = Column(Integer)  # minutes
    total_time = Column(Integer)  # minutes
    servings = Column(Integer, default=1)
    difficulty = Column(String)  # 'easy', 'medium', 'hard'

    # Recipe content
    ingredients = Column(Text, nullable=False)  # JSON array
    instructions = Column(Text, nullable=False)  # JSON array of steps

    # Nutritional info
    calories_per_serving = Column(Integer)
    protein_g = Column(Float)
    carbs_g = Column(Float)
    fat_g = Column(Float)
    fiber_g = Column(Float)
    nutritional_highlights = Column(Text)  # JSON array

    # Source and generation
    source_url = Column(String)
    generated_by = Column(String, default='ai')  # 'ai', 'user', 'scraped'
    generation_prompt = Column(Text)

    image_url = Column(String)
    tags = Column(Text)  # JSON array

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="recipes")
    meals = relationship("Meal", back_populates="recipe", cascade="all, delete-orphan")
    feedback = relationship("RecipeFeedback", back_populates="recipe", cascade="all, delete-orphan")

    def set_ingredients(self, ingredients_list):
        self.ingredients = json.dumps(ingredients_list)

    def get_ingredients(self):
        return json.loads(self.ingredients) if self.ingredients else []

    def set_instructions(self, instructions_list):
        self.instructions = json.dumps(instructions_list)

    def get_instructions(self):
        return json.loads(self.instructions) if self.instructions else []

    def set_nutritional_highlights(self, highlights_list):
        self.nutritional_highlights = json.dumps(highlights_list)

    def get_nutritional_highlights(self):
        return json.loads(self.nutritional_highlights) if self.nutritional_highlights else []

    def set_tags(self, tags_list):
        self.tags = json.dumps(tags_list)

    def get_tags(self):
        return json.loads(self.tags) if self.tags else []


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    meal_date = Column(Date, nullable=False, index=True)
    meal_type = Column(String, nullable=False)  # 'breakfast', 'lunch', 'dinner', 'snack', 'drink'
    meal_order = Column(Integer, default=0)
    notes = Column(Text)
    completed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    meal_plan = relationship("MealPlan", back_populates="meals")
    recipe = relationship("Recipe", back_populates="meals")


class RecipeFeedback(Base):
    __tablename__ = "recipe_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer)  # 1-5
    liked = Column(Boolean)
    made_it = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="recipe_feedback")
    recipe = relationship("Recipe", back_populates="feedback")
