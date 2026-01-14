from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    OnboardingQuestionResponse,
    OnboardingQuestionAnswer
)
from services.research_service import get_baseline_questions, generate_followup_questions, analyze_onboarding_answers
from models import User, OnboardingQuestion, UserProfile, DietaryRestriction, NutritionalConcern
from routes.auth import get_current_user_dependency
from datetime import datetime
from typing import Dict

router = APIRouter()


@router.get("/start", response_model=dict)
async def start_onboarding(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Start onboarding by getting baseline questions.
    These are the same for everyone - clear, focused questions.
    """
    # Clear any existing onboarding questions
    db.query(OnboardingQuestion).filter(OnboardingQuestion.user_id == current_user.id).delete()

    # Get baseline questions
    baseline_questions = get_baseline_questions()

    # Save to database
    questions = []
    for q_data in baseline_questions:
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

    db.commit()

    # Refresh to get IDs
    for q in questions:
        db.refresh(q)

    return {
        "message": "Onboarding started",
        "stage": "baseline",
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
        ]
    }


@router.post("/baseline", response_model=dict)
async def submit_baseline_answers(
    current_user: User = Depends(get_current_user_dependency),
    db: Session = Depends(get_db)
):
    """
    After baseline questions are answered, generate follow-up questions.
    This uses AI to create personalized questions based on their answers.
    """
    # Get baseline questions with answers
    questions = db.query(OnboardingQuestion).filter(
        OnboardingQuestion.user_id == current_user.id,
        OnboardingQuestion.answer.isnot(None)
    ).all()

    if len(questions) < 5:  # Should have at least the 5 baseline questions
        raise HTTPException(status_code=400, detail="Please answer all baseline questions first")

    # Build answer dict
    baseline_answers = {
        q.question_text: q.answer
        for q in questions[:5]  # First 5 are baseline
    }

    # Generate follow-up questions
    result = await generate_followup_questions(baseline_answers)

    # Save follow-up questions to database
    followup_questions = []
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
        followup_questions.append(question)

    # Create or update profile with detected info
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(
            user_id=current_user.id,
            dietary_type=result.get('detected_dietary_type', 'omnivore')
        )
        db.add(profile)
    else:
        profile.dietary_type = result.get('detected_dietary_type', 'omnivore')

    # Save nutritional concerns
    db.query(NutritionalConcern).filter(NutritionalConcern.user_id == current_user.id).delete()

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
    for q in followup_questions:
        db.refresh(q)

    return {
        "message": "Follow-up questions generated",
        "stage": "followup",
        "detected_dietary_type": result.get('detected_dietary_type'),
        "nutritional_concerns": [
            {
                "nutrient": c.get('nutrient', ''),
                "reasoning": c.get('reasoning', '')
            }
            for c in result.get('nutritional_concerns', [])
        ],
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
            for q in followup_questions
        ]
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
    # Get all answered questions
    questions = db.query(OnboardingQuestion).filter(
        OnboardingQuestion.user_id == current_user.id,
        OnboardingQuestion.answer.isnot(None)
    ).all()

    if not questions:
        raise HTTPException(status_code=400, detail="No questions answered yet")

    # Build answer dict
    all_answers = {
        q.question_text: q.answer
        for q in questions
    }

    # Analyze answers
    analysis = await analyze_onboarding_answers(all_answers)

    # Get or create profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update profile
    profile.dietary_type = analysis.get('dietary_type', 'omnivore')

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
