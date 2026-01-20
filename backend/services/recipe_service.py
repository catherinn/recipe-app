from anthropic import Anthropic
from typing import List, Dict, Optional
from datetime import date, timedelta
import json
import logging
from config import get_settings
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)
settings = get_settings()

# Lazy initialization of Anthropic client
_client = None

def get_anthropic_client():
    """Get or create Anthropic client with validation"""
    global _client
    if not settings.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI features are not configured. Please set ANTHROPIC_API_KEY environment variable."
        )
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


async def generate_recipe(
    user_profile: Dict,
    meal_type: str,
    additional_requirements: Optional[str] = None
) -> Dict:
    """
    Generate a single recipe using Claude based on user profile.
    """

    # Build context from user profile
    dietary_info = f"Dietary type: {user_profile.get('dietary_type', 'omnivore')}"

    restrictions = user_profile.get('dietary_restrictions', [])
    if restrictions:
        restrictions_text = ", ".join([r['value'] for r in restrictions])
        dietary_info += f"\nRestrictions: {restrictions_text}"

    concerns = user_profile.get('nutritional_concerns', [])
    if concerns:
        nutrients_text = ", ".join([c['nutrient'] for c in concerns])
        dietary_info += f"\nNutritional focus: {nutrients_text}"

    cooking_prefs = user_profile.get('cooking_preferences', {})
    time_pref = cooking_prefs.get('time_preference', 'medium')
    skill_level = cooking_prefs.get('skill_level', 'intermediate')
    people_count = cooking_prefs.get('people_count', 1)

    time_mapping = {
        'quick': '15-30 minutes',
        'medium': '30-60 minutes',
        'long': '60+ minutes'
    }

    prompt = f"""Create a {meal_type} recipe with these requirements:

{dietary_info}
Cooking time: {time_mapping.get(time_pref, '30-60 minutes')}
Skill level: {skill_level}
Servings: {people_count}

{f"Additional: {additional_requirements}" if additional_requirements else ""}

Provide a detailed recipe in JSON format:
{{
  "title": "Recipe name",
  "description": "Brief appetizing description",
  "cuisine_type": "Italian, Asian, Mediterranean, etc.",
  "prep_time": 15,
  "cook_time": 20,
  "total_time": 35,
  "servings": {people_count},
  "difficulty": "easy|medium|hard",
  "ingredients": [
    "2 cups rice",
    "1 tablespoon olive oil"
  ],
  "instructions": [
    "Rinse rice thoroughly",
    "Heat oil in a pan"
  ],
  "calories_per_serving": 350,
  "protein_g": 12.5,
  "carbs_g": 45.0,
  "fat_g": 10.0,
  "fiber_g": 5.0,
  "nutritional_highlights": ["high_protein", "vitamin_b12_rich", "iron_rich"],
  "tags": ["vegetarian", "quick", "healthy"]
}}

Make it delicious, nutritionally balanced, and address their specific needs."""

    client = get_anthropic_client()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        recipe_data = json.loads(json_str)
        return recipe_data
    except json.JSONDecodeError:
        # Fallback recipe
        return {
            "title": "Simple Meal",
            "description": "A nutritious meal",
            "cuisine_type": "International",
            "prep_time": 10,
            "cook_time": 20,
            "total_time": 30,
            "servings": people_count,
            "difficulty": "easy",
            "ingredients": ["Ingredients to be determined"],
            "instructions": ["Instructions to be determined"],
            "calories_per_serving": 300,
            "protein_g": 15.0,
            "carbs_g": 40.0,
            "fat_g": 10.0,
            "fiber_g": 5.0,
            "nutritional_highlights": [],
            "tags": []
        }


async def generate_weekly_meal_plan(
    user_profile: Dict,
    start_date: date
) -> Dict:
    """
    Generate a complete weekly meal plan with breakfast, lunch, dinner, snacks, and drinks.
    """

    # Build comprehensive context
    dietary_info = f"Dietary type: {user_profile.get('dietary_type', 'omnivore')}"

    restrictions = user_profile.get('dietary_restrictions', [])
    if restrictions:
        restrictions_text = ", ".join([r['value'] for r in restrictions])
        dietary_info += f"\nRestrictions: {restrictions_text}"

    concerns = user_profile.get('nutritional_concerns', [])
    concern_notes = []
    if concerns:
        for c in concerns:
            nutrient = c['nutrient'].replace('_', ' ').title()
            sources = ", ".join(c.get('recommended_sources', [])[:3])
            concern_notes.append(f"{nutrient} (sources: {sources})")
        dietary_info += f"\nNutritional focus: {'; '.join(concern_notes)}"

    cooking_prefs = user_profile.get('cooking_preferences', {})
    people_count = cooking_prefs.get('people_count', 1)
    goals = user_profile.get('goals', [])

    prompt = f"""Create a complete 7-day meal plan with:
- Breakfast
- Lunch
- Dinner
- 2 snacks (mid-morning and afternoon)
- 1 healthy drink/smoothie per day

User Profile:
{dietary_info}
Servings per meal: {people_count}
Goals: {', '.join(goals) if goals else 'balanced nutrition'}

Requirements:
1. Ensure variety - no repetitive meals
2. Address nutritional concerns through food choices
3. Include prep/cook times
4. Balance macros across the day
5. Make it realistic and achievable

Provide response in JSON format:
{{
  "week_summary": "Overview of the meal plan approach",
  "daily_plans": [
    {{
      "day": "Monday",
      "date": "{start_date.isoformat()}",
      "breakfast": {{
        "title": "Overnight Oats with Berries",
        "prep_time": 5,
        "cook_time": 0,
        "calories": 350,
        "protein_g": 12,
        "ingredients": ["1 cup oats", "..."],
        "instructions": ["Mix ingredients", "..."],
        "nutritional_highlights": ["high_fiber", "vitamin_b12_rich"]
      }},
      "lunch": {{}},
      "dinner": {{}},
      "snacks": [
        {{
          "title": "Apple with Almond Butter",
          "calories": 200
        }},
        {{}}
      ],
      "drink": {{
        "title": "Green Smoothie",
        "ingredients": ["..."]
      }}
    }}
  ]
}}

Make it delicious, nutritionally complete, and varied!"""

    client = get_anthropic_client()
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        meal_plan_data = json.loads(json_str)
        return meal_plan_data
    except json.JSONDecodeError as e:
        # Fallback - generate simple plan
        daily_plans = []
        for i in range(7):
            day_date = start_date + timedelta(days=i)
            daily_plans.append({
                "day": day_date.strftime("%A"),
                "date": day_date.isoformat(),
                "breakfast": {
                    "title": f"Breakfast for {day_date.strftime('%A')}",
                    "prep_time": 10,
                    "cook_time": 10,
                    "calories": 350,
                    "ingredients": ["To be generated"],
                    "instructions": ["To be generated"]
                },
                "lunch": {
                    "title": f"Lunch for {day_date.strftime('%A')}",
                    "prep_time": 15,
                    "cook_time": 20,
                    "calories": 500,
                    "ingredients": ["To be generated"],
                    "instructions": ["To be generated"]
                },
                "dinner": {
                    "title": f"Dinner for {day_date.strftime('%A')}",
                    "prep_time": 20,
                    "cook_time": 30,
                    "calories": 600,
                    "ingredients": ["To be generated"],
                    "instructions": ["To be generated"]
                },
                "snacks": [
                    {"title": "Morning snack", "calories": 150},
                    {"title": "Afternoon snack", "calories": 150}
                ],
                "drink": {"title": "Healthy drink", "ingredients": ["To be generated"]}
            })

        return {
            "week_summary": "Customized meal plan",
            "daily_plans": daily_plans
        }
