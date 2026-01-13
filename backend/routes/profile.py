from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserProfileResponse, UserProfileUpdate
from models import User, UserProfile, DietaryRestriction, NutritionalConcern
from routes.auth import get_current_user_dependency

router = APIRouter()


@router.get("/", response_model=dict)
async def get_profile(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get complete user profile including restrictions and nutritional concerns.
    """
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

    return {
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "cooking_time_preference": profile.cooking_time_preference,
            "skill_level": profile.skill_level,
            "people_count": profile.people_count,
            "primary_goal": profile.primary_goal,
            "likes": profile.get_likes(),
            "dislikes": profile.get_dislikes(),
            "dietary_context": profile.dietary_context,
            "dietary_type": profile.dietary_type,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        },
        "dietary_restrictions": [
            {
                "id": r.id,
                "restriction_type": r.restriction_type,
                "restriction_value": r.restriction_value,
                "severity": r.severity
            }
            for r in restrictions
        ],
        "nutritional_concerns": [
            {
                "id": c.id,
                "nutrient": c.nutrient,
                "concern_level": c.concern_level,
                "recommended_sources": c.get_recommended_sources(),
                "notes": c.notes
            }
            for c in concerns
        ]
    }


@router.put("/", response_model=dict)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Update user profile.
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Update fields if provided
    if profile_update.cooking_time_preference is not None:
        profile.cooking_time_preference = profile_update.cooking_time_preference
    if profile_update.skill_level is not None:
        profile.skill_level = profile_update.skill_level
    if profile_update.people_count is not None:
        profile.people_count = profile_update.people_count
    if profile_update.primary_goal is not None:
        profile.primary_goal = profile_update.primary_goal
    if profile_update.likes is not None:
        profile.set_likes(profile_update.likes)
    if profile_update.dislikes is not None:
        profile.set_dislikes(profile_update.dislikes)
    if profile_update.dietary_context is not None:
        profile.dietary_context = profile_update.dietary_context
    if profile_update.dietary_type is not None:
        profile.dietary_type = profile_update.dietary_type

    db.commit()
    db.refresh(profile)

    return {
        "message": "Profile updated successfully",
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "cooking_time_preference": profile.cooking_time_preference,
            "skill_level": profile.skill_level,
            "people_count": profile.people_count,
            "primary_goal": profile.primary_goal,
            "likes": profile.get_likes(),
            "dislikes": profile.get_dislikes(),
            "dietary_context": profile.dietary_context,
            "dietary_type": profile.dietary_type,
            "updated_at": profile.updated_at
        }
    }
