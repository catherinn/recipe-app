from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import MealPlanResponse
from models import User, UserProfile, DietaryRestriction, NutritionalConcern, MealPlan, Meal, Recipe
from routes.auth import get_current_user_dependency
from services.recipe_service import generate_weekly_meal_plan
from datetime import date, timedelta
from typing import Optional

router = APIRouter()


@router.post("/generate", response_model=dict)
async def generate_meal_plan(
    start_date: Optional[date] = Query(None, description="Week start date (defaults to next Monday)"),
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Generate a weekly meal plan with breakfast, lunch, dinner, snacks, and drinks.
    """
    # Get user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Complete onboarding first.")

    # Get dietary restrictions
    restrictions = db.query(DietaryRestriction).filter(
        DietaryRestriction.user_id == current_user.id
    ).all()

    # Get nutritional concerns
    concerns = db.query(NutritionalConcern).filter(
        NutritionalConcern.user_id == current_user.id
    ).all()

    # Build profile dict
    user_profile = {
        "dietary_type": profile.dietary_type,
        "dietary_restrictions": [
            {"type": r.restriction_type, "value": r.restriction_value, "severity": r.severity}
            for r in restrictions
        ],
        "nutritional_concerns": [
            {
                "nutrient": c.nutrient,
                "concern_level": c.concern_level,
                "recommended_sources": c.get_recommended_sources()
            }
            for c in concerns
        ],
        "cooking_preferences": {
            "time_preference": profile.cooking_time_preference or "medium",
            "skill_level": profile.skill_level or "intermediate",
            "people_count": profile.people_count or 1
        },
        "goals": [profile.primary_goal] if profile.primary_goal else []
    }

    # Default to next Monday if no start date provided
    if not start_date:
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        start_date = today + timedelta(days=days_until_monday if days_until_monday > 0 else 7)

    # Generate meal plan
    meal_plan_data = await generate_weekly_meal_plan(
        user_profile=user_profile,
        start_date=start_date
    )

    # Create meal plan record
    end_date = start_date + timedelta(days=6)
    meal_plan = MealPlan(
        user_id=current_user.id,
        week_start_date=start_date,
        week_end_date=end_date,
        status='active'
    )
    db.add(meal_plan)
    db.commit()
    db.refresh(meal_plan)

    # Create recipes and meals for each day
    for day_plan in meal_plan_data.get('daily_plans', []):
        day_date = date.fromisoformat(day_plan['date'])

        # Create breakfast
        breakfast_data = day_plan.get('breakfast', {})
        if breakfast_data:
            breakfast_recipe = _create_recipe_from_meal_data(
                breakfast_data, current_user.id, "breakfast", db
            )
            _create_meal(meal_plan.id, breakfast_recipe.id, day_date, "breakfast", 0, db)

        # Create lunch
        lunch_data = day_plan.get('lunch', {})
        if lunch_data:
            lunch_recipe = _create_recipe_from_meal_data(
                lunch_data, current_user.id, "lunch", db
            )
            _create_meal(meal_plan.id, lunch_recipe.id, day_date, "lunch", 0, db)

        # Create dinner
        dinner_data = day_plan.get('dinner', {})
        if dinner_data:
            dinner_recipe = _create_recipe_from_meal_data(
                dinner_data, current_user.id, "dinner", db
            )
            _create_meal(meal_plan.id, dinner_recipe.id, day_date, "dinner", 0, db)

        # Create snacks
        snacks = day_plan.get('snacks', [])
        for idx, snack_data in enumerate(snacks):
            if snack_data:
                snack_recipe = _create_recipe_from_meal_data(
                    snack_data, current_user.id, "snack", db
                )
                _create_meal(meal_plan.id, snack_recipe.id, day_date, "snack", idx, db)

        # Create drink
        drink_data = day_plan.get('drink', {})
        if drink_data:
            drink_recipe = _create_recipe_from_meal_data(
                drink_data, current_user.id, "drink", db
            )
            _create_meal(meal_plan.id, drink_recipe.id, day_date, "drink", 0, db)

    db.commit()

    return {
        "message": "Meal plan generated successfully",
        "meal_plan_id": meal_plan.id,
        "week_start_date": meal_plan.week_start_date,
        "week_end_date": meal_plan.week_end_date,
        "week_summary": meal_plan_data.get('week_summary', '')
    }


@router.get("/", response_model=list[dict])
async def list_meal_plans(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    List user's meal plans.
    """
    meal_plans = db.query(MealPlan).filter(
        MealPlan.user_id == current_user.id
    ).order_by(MealPlan.week_start_date.desc()).all()

    return [
        {
            "id": mp.id,
            "week_start_date": mp.week_start_date,
            "week_end_date": mp.week_end_date,
            "status": mp.status,
            "created_at": mp.created_at
        }
        for mp in meal_plans
    ]


@router.get("/{meal_plan_id}", response_model=dict)
async def get_meal_plan(
    meal_plan_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get a specific meal plan with all meals.
    """
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()

    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    # Get all meals for this plan
    meals = db.query(Meal).filter(
        Meal.meal_plan_id == meal_plan_id
    ).order_by(Meal.meal_date, Meal.meal_type, Meal.meal_order).all()

    # Group meals by date
    meals_by_date = {}
    for meal in meals:
        date_str = meal.meal_date.isoformat()
        if date_str not in meals_by_date:
            meals_by_date[date_str] = {
                "date": date_str,
                "breakfast": None,
                "lunch": None,
                "dinner": None,
                "snacks": [],
                "drinks": []
            }

        recipe = meal.recipe
        meal_data = {
            "id": meal.id,
            "recipe_id": recipe.id,
            "title": recipe.title,
            "description": recipe.description,
            "prep_time": recipe.prep_time,
            "cook_time": recipe.cook_time,
            "total_time": recipe.total_time,
            "servings": recipe.servings,
            "difficulty": recipe.difficulty,
            "ingredients": recipe.get_ingredients(),
            "instructions": recipe.get_instructions(),
            "calories_per_serving": recipe.calories_per_serving,
            "protein_g": recipe.protein_g,
            "carbs_g": recipe.carbs_g,
            "fat_g": recipe.fat_g,
            "completed": meal.completed
        }

        if meal.meal_type == "breakfast":
            meals_by_date[date_str]["breakfast"] = meal_data
        elif meal.meal_type == "lunch":
            meals_by_date[date_str]["lunch"] = meal_data
        elif meal.meal_type == "dinner":
            meals_by_date[date_str]["dinner"] = meal_data
        elif meal.meal_type == "snack":
            meals_by_date[date_str]["snacks"].append(meal_data)
        elif meal.meal_type == "drink":
            meals_by_date[date_str]["drinks"].append(meal_data)

    return {
        "id": meal_plan.id,
        "week_start_date": meal_plan.week_start_date,
        "week_end_date": meal_plan.week_end_date,
        "status": meal_plan.status,
        "created_at": meal_plan.created_at,
        "daily_meals": list(meals_by_date.values())
    }


def _create_recipe_from_meal_data(meal_data: dict, user_id: int, meal_type: str, db: Session) -> Recipe:
    """Helper to create recipe from meal plan data"""
    recipe = Recipe(
        user_id=user_id,
        title=meal_data.get('title', f'{meal_type.title()} Recipe'),
        description=meal_data.get('description', ''),
        cuisine_type=meal_data.get('cuisine_type'),
        prep_time=meal_data.get('prep_time', 0),
        cook_time=meal_data.get('cook_time', 0),
        total_time=meal_data.get('total_time', 0),
        servings=meal_data.get('servings', 1),
        difficulty=meal_data.get('difficulty', 'easy'),
        calories_per_serving=meal_data.get('calories', 0),
        protein_g=meal_data.get('protein_g'),
        carbs_g=meal_data.get('carbs_g'),
        fat_g=meal_data.get('fat_g'),
        fiber_g=meal_data.get('fiber_g'),
        generated_by='ai',
        generation_prompt=f'Weekly meal plan - {meal_type}'
    )

    recipe.set_ingredients(meal_data.get('ingredients', []))
    recipe.set_instructions(meal_data.get('instructions', []))
    recipe.set_nutritional_highlights(meal_data.get('nutritional_highlights', []))
    recipe.set_tags(meal_data.get('tags', []))

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def _create_meal(meal_plan_id: int, recipe_id: int, meal_date: date, meal_type: str, meal_order: int, db: Session):
    """Helper to create meal entry"""
    meal = Meal(
        meal_plan_id=meal_plan_id,
        recipe_id=recipe_id,
        meal_date=meal_date,
        meal_type=meal_type,
        meal_order=meal_order
    )
    db.add(meal)
