from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import RecipeResponse, RecipeCreate
from models import User, UserProfile, DietaryRestriction, NutritionalConcern, Recipe
from routes.auth import get_current_user_dependency
from services.recipe_service import generate_recipe
from typing import Optional

router = APIRouter()


@router.post("/generate", response_model=RecipeResponse)
async def generate_new_recipe(
    meal_type: str = Query(..., description="breakfast, lunch, dinner, snack, drink"),
    additional_requirements: Optional[str] = Query(None, description="Additional requirements"),
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Generate a new recipe based on user profile and meal type.
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
            {"nutrient": c.nutrient, "concern_level": c.concern_level}
            for c in concerns
        ],
        "cooking_preferences": {
            "time_preference": profile.cooking_time_preference or "medium",
            "skill_level": profile.skill_level or "intermediate",
            "people_count": profile.people_count or 1
        },
        "goals": [profile.primary_goal] if profile.primary_goal else []
    }

    # Generate recipe
    recipe_data = await generate_recipe(
        user_profile=user_profile,
        meal_type=meal_type,
        additional_requirements=additional_requirements
    )

    # Save recipe to database
    recipe = Recipe(
        user_id=current_user.id,
        title=recipe_data.get('title', 'Generated Recipe'),
        description=recipe_data.get('description'),
        cuisine_type=recipe_data.get('cuisine_type'),
        prep_time=recipe_data.get('prep_time'),
        cook_time=recipe_data.get('cook_time'),
        total_time=recipe_data.get('total_time'),
        servings=recipe_data.get('servings', 1),
        difficulty=recipe_data.get('difficulty'),
        calories_per_serving=recipe_data.get('calories_per_serving'),
        protein_g=recipe_data.get('protein_g'),
        carbs_g=recipe_data.get('carbs_g'),
        fat_g=recipe_data.get('fat_g'),
        fiber_g=recipe_data.get('fiber_g'),
        image_url=recipe_data.get('image_url'),
        generated_by='ai',
        generation_prompt=f"{meal_type}: {additional_requirements or 'based on profile'}"
    )

    recipe.set_ingredients(recipe_data.get('ingredients', []))
    recipe.set_instructions(recipe_data.get('instructions', []))
    recipe.set_nutritional_highlights(recipe_data.get('nutritional_highlights', []))
    recipe.set_tags(recipe_data.get('tags', []))

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return {
        "id": recipe.id,
        "user_id": recipe.user_id,
        "title": recipe.title,
        "description": recipe.description,
        "cuisine_type": recipe.cuisine_type,
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
        "fiber_g": recipe.fiber_g,
        "nutritional_highlights": recipe.get_nutritional_highlights(),
        "source_url": recipe.source_url,
        "image_url": recipe.image_url,
        "tags": recipe.get_tags(),
        "generated_by": recipe.generated_by,
        "created_at": recipe.created_at
    }


@router.get("/", response_model=list[RecipeResponse])
async def list_recipes(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    List user's recipes.
    """
    recipes = db.query(Recipe).filter(
        Recipe.user_id == current_user.id
    ).order_by(Recipe.created_at.desc()).offset(skip).limit(limit).all()

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "title": r.title,
            "description": r.description,
            "cuisine_type": r.cuisine_type,
            "prep_time": r.prep_time,
            "cook_time": r.cook_time,
            "total_time": r.total_time,
            "servings": r.servings,
            "difficulty": r.difficulty,
            "ingredients": r.get_ingredients(),
            "instructions": r.get_instructions(),
            "calories_per_serving": r.calories_per_serving,
            "protein_g": r.protein_g,
            "carbs_g": r.carbs_g,
            "fat_g": r.fat_g,
            "fiber_g": r.fiber_g,
            "nutritional_highlights": r.get_nutritional_highlights(),
            "source_url": r.source_url,
            "image_url": r.image_url,
            "tags": r.get_tags(),
            "generated_by": r.generated_by,
            "created_at": r.created_at
        }
        for r in recipes
    ]


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get a specific recipe.
    """
    recipe = db.query(Recipe).filter(
        Recipe.id == recipe_id,
        Recipe.user_id == current_user.id
    ).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {
        "id": recipe.id,
        "user_id": recipe.user_id,
        "title": recipe.title,
        "description": recipe.description,
        "cuisine_type": recipe.cuisine_type,
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
        "fiber_g": recipe.fiber_g,
        "nutritional_highlights": recipe.get_nutritional_highlights(),
        "source_url": recipe.source_url,
        "image_url": recipe.image_url,
        "tags": recipe.get_tags(),
        "generated_by": recipe.generated_by,
        "created_at": recipe.created_at
    }
