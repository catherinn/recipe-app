from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    google_id: str
    picture_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    google_id: str
    picture_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# User Profile Schemas
class UserProfileBase(BaseModel):
    cooking_time_preference: Optional[str] = None
    skill_level: Optional[str] = None
    people_count: Optional[int] = 1
    primary_goal: Optional[str] = None
    likes: Optional[List[str]] = []
    dislikes: Optional[List[str]] = []
    dietary_context: Optional[str] = None
    dietary_type: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Dietary Restriction Schemas
class DietaryRestrictionBase(BaseModel):
    restriction_type: str
    restriction_value: str
    severity: Optional[str] = None


class DietaryRestrictionCreate(DietaryRestrictionBase):
    pass


class DietaryRestrictionResponse(DietaryRestrictionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Nutritional Concern Schemas
class NutritionalConcernBase(BaseModel):
    nutrient: str
    concern_level: Optional[str] = None
    recommended_sources: Optional[List[str]] = []
    notes: Optional[str] = None


class NutritionalConcernResponse(NutritionalConcernBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Onboarding Question Schemas
class OnboardingQuestionBase(BaseModel):
    question_text: str
    question_type: str
    options: Optional[List[str]] = []
    research_context: Optional[str] = None


class OnboardingQuestionCreate(OnboardingQuestionBase):
    pass


class OnboardingQuestionAnswer(BaseModel):
    question_id: int
    answer: str


class OnboardingQuestionResponse(OnboardingQuestionBase):
    id: int
    user_id: int
    answer: Optional[str] = None
    asked_at: datetime
    answered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Recipe Schemas
class RecipeBase(BaseModel):
    title: str
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    servings: int = 1
    difficulty: Optional[str] = None
    ingredients: List[str]
    instructions: List[str]
    calories_per_serving: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    fiber_g: Optional[float] = None
    nutritional_highlights: Optional[List[str]] = []
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = []


class RecipeCreate(RecipeBase):
    generation_prompt: Optional[str] = None


class RecipeResponse(RecipeBase):
    id: int
    user_id: Optional[int] = None
    generated_by: str
    created_at: datetime

    class Config:
        from_attributes = True


# Meal Plan Schemas
class MealBase(BaseModel):
    recipe_id: int
    meal_date: date
    meal_type: str
    meal_order: int = 0
    notes: Optional[str] = None


class MealResponse(MealBase):
    id: int
    meal_plan_id: int
    completed: bool
    recipe: RecipeResponse

    class Config:
        from_attributes = True


class MealPlanBase(BaseModel):
    week_start_date: date
    week_end_date: date


class MealPlanCreate(MealPlanBase):
    pass


class MealPlanResponse(MealPlanBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    meals: List[MealResponse] = []

    class Config:
        from_attributes = True


# Recipe Feedback Schemas
class RecipeFeedbackBase(BaseModel):
    recipe_id: int
    rating: Optional[int] = None
    liked: Optional[bool] = None
    made_it: bool = False
    notes: Optional[str] = None


class RecipeFeedbackCreate(RecipeFeedbackBase):
    pass


class RecipeFeedbackResponse(RecipeFeedbackBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Onboarding Schemas
class OnboardingContextRequest(BaseModel):
    context: str  # Free-form text from user


class OnboardingContextResponse(BaseModel):
    questions: List[OnboardingQuestionResponse]
    detected_dietary_type: Optional[str] = None
    detected_concerns: List[str] = []


# Auth Schemas
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class GoogleAuthRequest(BaseModel):
    id_token: str
