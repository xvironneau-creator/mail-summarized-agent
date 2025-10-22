import os
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
APP_NAME = "gmail_summarizer"
USER_ID = "owner"
SESSION_ID = "session1"

# Agent : résumé + enrichissement web
summarizer_agent = Agent(
    name="summarizer_agent",
    model=GEMINI_MODEL,
    instruction=(
        "Tu es un assistant qui résume des emails Gmail en français. "
        "Liste les points clés, actions, deadlines et personnes citées. "
        "Si besoin, enrichis via Google Search."
    ),
    tools=[google_search],
)

_session_service = InMemorySessionService()
runner = Runner(agent=summarizer_agent, app_name=APP_NAME, session_service=_session_service)

async def run_summary_async(text: str) -> str:
    """Envoie le texte à l’agent Gemini et renvoie le résumé final."""
    content = types.Content(role="user", parts=[types.Part(text=text)])
    final = ""
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            final = event.content.parts[0].text.strip()
    return final or "Résumé vide."
