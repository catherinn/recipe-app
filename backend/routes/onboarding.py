from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    OnboardingContextRequest,
    OnboardingContextResponse,
    OnboardingQuestionResponse,
    OnboardingQuestionAnswer
)
from services.research_service import generate_onboarding_questions, analyze_onboarding_answers
from models import User, OnboardingQuestion, UserProfile, DietaryRestriction, NutritionalConcern
from routes.auth import get_current_user_dependency
from datetime import datetime

router = APIRouter()


@router.post("/context", response_model=OnboardingContextResponse)
async def submit_dietary_context(
    context_request: OnboardingContextRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Submit dietary context and get personalized onboarding questions.
    This uses web research (via Claude) to generate relevant questions.
    """
    # Generate questions based on context
    result = await generate_onboarding_questions(
        dietary_context=context_request.context,
        user_info={"name": current_user.name}
    )

    # Save questions to database
    questions = []
    for q_data in result.get('questions', []):
        question = OnboardingQuestion(
            user_id=current_user.id,
            question_text=q_data['question_text'],
            question_type=q_data['question_type'],
            research_context=q_data.get('research_context', '')
        )

        if q_data.get('options'):
            question.set_options(q_data['options'])

        db.add(question)
        questions.append(question)

    # Save or update user profile with initial context
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(
            user_id=current_user.id,
            dietary_context=context_request.context,
            dietary_type=result.get('detected_dietary_type', 'unknown')
        )
        db.add(profile)
    else:
        profile.dietary_context = context_request.context
        profile.dietary_type = result.get('detected_dietary_type', 'unknown')

    # Save nutritional concerns
    for concern_data in result.get('nutritional_concerns', []):
        concern = NutritionalConcern(
            user_id=current_user.id,
            nutrient=concern_data.get('nutrient', ''),
            concern_level=concern_data.get('risk_level', 'monitor'),
            notes=concern_data.get('reasoning', '')
        )
        if concern_data.get('food_sources'):
            concern.set_recommended_sources(concern_data['food_sources'])
        db.add(concern)

    db.commit()

    # Refresh to get IDs
    for q in questions:
        db.refresh(q)

    # Build response
    return {
        "questions": [
            {
                "id": q.id,
                "user_id": q.user_id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": q.get_options(),
                "research_context": q.research_context,
                "answer": q.answer,
                "asked_at": q.asked_at,
                "answered_at": q.answered_at
            }
            for q in questions
        ],
        "detected_dietary_type": result.get('detected_dietary_type'),
        "detected_concerns": [c.get('nutrient', '') for c in result.get('nutritional_concerns', [])]
    }


@router.post("/answer")
async def answer_question(
    answer: OnboardingQuestionAnswer,
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Submit answer to an onboarding question.
    """
    question = db.query(OnboardingQuestion).filter(
        OnboardingQuestion.id == answer.question_id,
        OnboardingQuestion.user_id == current_user.id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    question.answer = answer.answer
    question.answered_at = datetime.utcnow()
    db.commit()

    return {"message": "Answer recorded", "question_id": question.id}


@router.post("/complete")
async def complete_onboarding(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Complete onboarding by analyzing all answers and creating comprehensive profile.
    """
    # Get profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Submit context first.")

    # Get all answered questions
    questions = db.query(OnboardingQuestion).filter(
        OnboardingQuestion.user_id == current_user.id,
        OnboardingQuestion.answer.isnot(None)
    ).all()

    if not questions:
        raise HTTPException(status_code=400, detail="No questions answered yet")

    # Prepare Q&A for analysis
    qa_list = [
        {"question": q.question_text, "answer": q.answer}
        for q in questions
    ]

    # Analyze answers
    analysis = await analyze_onboarding_answers(
        dietary_context=profile.dietary_context,
        questions_and_answers=qa_list
    )

    # Update profile
    profile.dietary_type = analysis.get('dietary_type', profile.dietary_type)

    cooking_prefs = analysis.get('cooking_preferences', {})
    profile.cooking_time_preference = cooking_prefs.get('time_preference')
    profile.skill_level = cooking_prefs.get('skill_level')
    profile.people_count = cooking_prefs.get('people_count', 1)

    goals = analysis.get('goals', [])
    if goals:
        profile.primary_goal = goals[0]

    # Clear and re-add dietary restrictions
    db.query(DietaryRestriction).filter(DietaryRestriction.user_id == current_user.id).delete()

    for restriction_data in analysis.get('dietary_restrictions', []):
        restriction = DietaryRestriction(
            user_id=current_user.id,
            restriction_type=restriction_data.get('type', 'preference'),
            restriction_value=restriction_data.get('value', ''),
            severity=restriction_data.get('severity', 'moderate')
        )
        db.add(restriction)

    # Clear and re-add nutritional concerns
    db.query(NutritionalConcern).filter(NutritionalConcern.user_id == current_user.id).delete()

    for concern_data in analysis.get('nutritional_concerns', []):
        concern = NutritionalConcern(
            user_id=current_user.id,
            nutrient=concern_data.get('nutrient', ''),
            concern_level=concern_data.get('concern_level', 'monitor'),
            notes=concern_data.get('notes', '')
        )
        if concern_data.get('recommended_sources'):
            concern.set_recommended_sources(concern_data['recommended_sources'])
        db.add(concern)

    db.commit()

    return {
        "message": "Onboarding completed successfully",
        "profile_summary": {
            "dietary_type": profile.dietary_type,
            "cooking_time_preference": profile.cooking_time_preference,
            "skill_level": profile.skill_level,
            "people_count": profile.people_count,
            "primary_goal": profile.primary_goal
        }
    }


@router.get("/questions", response_model=list[OnboardingQuestionResponse])
async def get_onboarding_questions(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Get all onboarding questions for current user.
    """
    questions = db.query(OnboardingQuestion).filter(
        OnboardingQuestion.user_id == current_user.id
    ).order_by(OnboardingQuestion.asked_at).all()

    return [
        {
            "id": q.id,
            "user_id": q.user_id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": q.get_options(),
            "research_context": q.research_context,
            "answer": q.answer,
            "asked_at": q.asked_at,
            "answered_at": q.answered_at
        }
        for q in questions
    ]
