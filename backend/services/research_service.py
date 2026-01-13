import httpx
from typing import List, Dict, Optional
from anthropic import Anthropic
from config import get_settings

settings = get_settings()
client = Anthropic(api_key=settings.anthropic_api_key)


async def search_dietary_research(dietary_context: str) -> str:
    """
    Perform web search for dietary research based on user context.
    This is a placeholder - in production, you'd use a real search API.
    For now, we'll use Claude to simulate research-based question generation.
    """
    # In production, you would use:
    # - Google Custom Search API
    # - Bing Search API
    # - Or web scraping of trusted nutrition sites

    # For MVP, we'll use Claude's knowledge + structured prompting
    prompt = f"""
Based on this dietary context: "{dietary_context}"

Research and identify:
1. The dietary type (vegetarian, vegan, pescatarian, omnivore, etc.)
2. Common nutritional deficiencies or risks for this diet
3. Important follow-up questions to ask for personalization
4. Recommended food sources for at-risk nutrients

Provide a structured analysis.
"""

    return prompt


async def generate_onboarding_questions(
    dietary_context: str,
    user_info: Optional[Dict] = None
) -> Dict:
    """
    Use Claude to generate personalized onboarding questions based on user's dietary context.
    This uses web research (simulated) to ask relevant questions.
    """

    # First, get research context
    research_prompt = await search_dietary_research(dietary_context)

    # Generate questions using Claude
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a nutrition expert helping to onboard a new user to a recipe app.

User's dietary context: "{dietary_context}"

Based on this context, generate 5-8 important follow-up questions to understand their needs better.

For each question:
1. Make it specific to their situation
2. Explain why you're asking (research-based reasoning)
3. Suggest the question type (yes_no, multiple_choice, text, number)
4. If multiple_choice, provide options

Format your response as JSON:
{{
  "detected_dietary_type": "vegetarian|vegan|pescatarian|omnivore|flexitarian",
  "nutritional_concerns": [
    {{
      "nutrient": "vitamin_b12",
      "risk_level": "high|medium|low",
      "reasoning": "why this is a concern",
      "food_sources": ["fortified cereals", "nutritional yeast", "dairy"]
    }}
  ],
  "questions": [
    {{
      "question_text": "Do you consume dairy products like milk, cheese, or yogurt?",
      "question_type": "yes_no",
      "options": [],
      "research_context": "Dairy is a key source of B12 and calcium for vegetarians"
    }},
    {{
      "question_text": "How would you describe your current activity level?",
      "question_type": "multiple_choice",
      "options": ["Sedentary", "Lightly active", "Moderately active", "Very active"],
      "research_context": "Activity level affects caloric and protein needs"
    }}
  ]
}}

Make questions conversational and friendly, not clinical."""
            }
        ]
    )

    # Parse Claude's response
    import json
    response_text = message.content[0].text

    # Extract JSON from response (Claude might add explanation text)
    try:
        # Try to find JSON in the response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        result = json.loads(json_str)
        return result
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "detected_dietary_type": "unknown",
            "nutritional_concerns": [],
            "questions": [
                {
                    "question_text": "Can you tell me more about your dietary preferences?",
                    "question_type": "text",
                    "options": [],
                    "research_context": "Understanding dietary needs"
                }
            ]
        }


async def analyze_onboarding_answers(
    dietary_context: str,
    questions_and_answers: List[Dict]
) -> Dict:
    """
    Analyze all onboarding answers to create a comprehensive user profile.
    """

    qa_text = "\n".join([
        f"Q: {qa['question']}\nA: {qa['answer']}"
        for qa in questions_and_answers
    ])

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""Based on this user's dietary context and answers, create a structured profile:

Dietary Context: "{dietary_context}"

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
