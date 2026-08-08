import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

CURRICULUM_PATH = os.path.join(os.path.dirname(__file__), "data", "curriculum.json")

def load_curriculum():
    if os.path.exists(CURRICULUM_PATH):
        try:
            with open(CURRICULUM_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

CURRICULUM = load_curriculum()

def process_interview_turn(session: dict, user_message: str = None) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {
            "done": False,
            "reply": "Error: GROQ_API_KEY environment variable is not configured."
        }

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )

    if user_message:
        session["history"].append({"role": "user", "content": user_message})

    candidate = session.get("candidate", {})
    turn_count = session.get("turn_count", 0)

    system_prompt = f"""You are a senior technical AI Engineering Interviewer.
Conduct a dynamic multi-turn interview based on the candidate profile and curriculum.

Candidate Profile:
{json.dumps(candidate, indent=2)}

Curriculum Data:
{json.dumps(CURRICULUM, indent=2)}

Current Turns Completed: {turn_count}

Output strictly in JSON format.

If ONGOING:
{{
  "done": false,
  "reply": "<your next question or follow-up>"
}}

If FINISHED (after asking at least 8 questions across 4+ days):
{{
  "done": true,
  "reply": "Interview complete.",
  "feedback": {{
    "summary": "<summary>",
    "strengths": ["<strength1>"],
    "gaps": ["<gap1>"],
    "next": ["<next_step1>"]
  }}
}}
"""

    messages = [{"role": "system", "content": system_prompt}] + session.get("history", [])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.7
    )

    parsed_response = json.loads(response.choices[0].message.content)
    session["history"].append({"role": "assistant", "content": parsed_response.get("reply", "")})
    session["turn_count"] += 1

    return parsed_response