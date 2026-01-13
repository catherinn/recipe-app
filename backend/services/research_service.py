import httpx
from typing import List, Dict, Optional
from anthropic import Anthropic
from config import get_settings

settings = get_settings()
client = Anthropic(api_key=settings.anthropic_api_key)


def get_baseline_questions() -> List[Dict]:
    """
    Get the baseline onboarding questions that everyone answers.
    These are clear, focused questions to establish the foundation.
    """
    return [
        {
            "question_text": "What's your main goal with meal planning?",
            "question_type": "multiple_choice",
            "options": [
                "Eat healthier",
                "Save time",
                "Lose weight",
                "Build muscle",
                "Discover new recipes",
                "Manage a health condition"
            ],
            "research_context": "Understanding your primary goal helps us tailor recipes and portions"
        },
        {
            "question_text": "How many people are you typically cooking for?",
            "question_type": "number",
            "options": [],
            "research_context": "We'll adjust all recipe servings to match your household"
        },
        {
            "question_text": "How much time do you want to spend cooking on a typical day?",
            "question_type": "multiple_choice",
            "options": [
                "15-30 minutes (quick meals)",
                "30-60 minutes (balanced)",
                "60+ minutes (I enjoy cooking)"
            ],
            "research_context": "Time constraints affect recipe complexity and cooking methods"
        },
        {
            "question_text": "How would you describe your cooking skill level?",
            "question_type": "multiple_choice",
            "options": [
                "Beginner (simple recipes please)",
                "Intermediate (comfortable with basics)",
                "Advanced (bring on the challenge)"
            ],
            "research_context": "We'll match recipe difficulty to your comfort level"
        },
        {
            "question_text": "Which best describes your diet?",
            "question_type": "multiple_choice",
            "options": [
                "I eat everything (omnivore)",
                "Vegetarian",
                "Vegan",
                "Pescatarian (vegetarian + fish)",
                "Flexitarian (mostly plant-based)",
                "Other/specific diet"
            ],
            "research_context": "Your dietary type is the foundation for all recipe recommendations"
        }
    ]


async def generate_followup_questions(
    baseline_answers: Dict[str, str]
) -> Dict:
    """
    Use Claude to generate smart follow-up questions based on baseline answers.
    This adapts to the user's specific situation.
    """

    # Build context from baseline answers
    answers_text = "\n".join([f"- {q}: {a}" for q, a in baseline_answers.items()])

    # Generate follow-up questions using Claude
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a nutrition expert creating a personalized onboarding flow.

The user has answered these baseline questions:
{answers_text}

Based on their answers, generate 3-5 smart follow-up questions to understand:
1. Specific dietary restrictions or allergies
2. Nutritional concerns based on their diet type
3. Food preferences and dislikes
4. Any other relevant details

For each question:
- Make it conversational and friendly
- Explain why you're asking (be transparent)
- Keep it focused and not overwhelming

Format your response as JSON:
{{
  "detected_dietary_type": "vegetarian|vegan|pescatarian|omnivore|flexitarian",
  "nutritional_concerns": [
    {{
      "nutrient": "vitamin_b12",
      "risk_level": "at_risk|monitor",
      "reasoning": "Vegetarians need to ensure adequate B12 intake",
      "food_sources": ["fortified cereals", "nutritional yeast", "dairy", "eggs"]
    }}
  ],
  "questions": [
    {{
      "question_text": "Do you consume dairy products (milk, cheese, yogurt)?",
      "question_type": "yes_no",
      "options": [],
      "research_context": "Dairy is a key source of B12, calcium, and protein for vegetarians"
    }},
    {{
      "question_text": "Are there any foods you're allergic to or can't eat?",
      "question_type": "text",
      "options": [],
      "research_context": "We'll make sure to exclude these from all recipes"
    }}
  ]
}}

Important:
- If they're vegetarian, ask about dairy, eggs, and fish to understand exactly what they eat
- If they selected "lose weight", ask about their approach (calorie counting, portion control, etc.)
- If they selected "manage health condition", ask what condition
- Keep questions relevant to THEIR specific answers
- Limit to 3-5 questions maximum - don't overwhelm them"""
            }
        ]
    )

    # Parse Claude's response
    import json
    response_text = message.content[0].text

    # Extract JSON from response (Claude might add explanation text)
    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "detected_dietary_type": baseline_answers.get("Which best describes your diet?", "omnivore").lower(),
            "nutritional_concerns": [],
            "questions": []
        }


async def analyze_onboarding_answers(
    all_answers: Dict[str, str]
) -> Dict:
    """
    Analyze all onboarding answers to create a comprehensive user profile.
    """

    qa_text = "\n".join([
        f"Q: {q}\nA: {a}"
        for q, a in all_answers.items()
    ])

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""Based on the user's answers, create a structured profile:

Questions & Answers:
{qa_text}

Provide a JSON response:
{{
  "dietary_type": "vegetarian|vegan|pescatarian|omnivore|flexitarian",
  "dietary_restrictions": [
    {{
      "type": "allergy|intolerance|preference|religious|ethical",
      "value": "dairy",
      "severity": "strict|moderate|flexible"
    }}
  ],
  "nutritional_concerns": [
    {{
      "nutrient": "vitamin_b12",
      "concern_level": "at_risk|monitor|supplement",
      "recommended_sources": ["fortified cereals", "nutritional yeast"],
      "notes": "Consider B12 supplementation"
    }}
  ],
  "cooking_preferences": {{
    "time_preference": "quick|medium|long",
    "skill_level": "beginner|intermediate|advanced",
    "people_count": 1
  }},
  "goals": ["health", "convenience", "weight_loss", "muscle_gain"]
}}"""
            }
        ]
    )

    import json
    response_text = message.content[0].text

    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {
            "dietary_type": "omnivore",
            "dietary_restrictions": [],
            "nutritional_concerns": [],
            "cooking_preferences": {},
            "goals": []
        }
