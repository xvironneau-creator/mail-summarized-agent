import os
import base64
from typing import List, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def build_gmail_service():
    """Crée le client Gmail à partir des variables Render (OAuth)."""
    client_id = os.getenv("GMAIL_CLIENT_ID")
    client_secret = os.getenv("GMAIL_CLIENT_SECRET")
    refresh_token = os.getenv("GMAIL_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise RuntimeError("⚠️ Variables OAuth Gmail manquantes.")

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)

def fetch_messages_by_label(label: str, max_results: int = 10) -> List[Dict]:
    """Récupère les emails depuis un label Gmail."""
    service = build_gmail_service()
    results = service.users().messages().list(userId="me", q=label, maxResults=max_results).execute()
    ids = [m["id"] for m in results.get("messages", [])]
    out = []
    for mid in ids:
        full = service.users().messages().get(userId="me", id=mid, format="full").execute()
        out.append(full)
    return out

def message_to_text(msg: Dict) -> str:
    """Convertit un message Gmail en texte lisible."""
    headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
    subject = headers.get("subject", "")
    snippet = msg.get("snippet", "")
    body = ""

    def extract_parts(parts):
        nonlocal body
        for p in parts:
            if p.get("mimeType") == "text/plain" and p.get("body", {}).get("data"):
                body += base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8", errors="ignore")
            if p.get("parts"):
                extract_parts(p["parts"])

    payload = msg.get("payload", {})
    if payload.get("parts"):
        extract_parts(payload["parts"])

    return f"Subject: {subject}\n\nSnippet: {snippet}\n\nBody:\n{body}"

def concat_messages_text(msgs: List[Dict]) -> str:
    """Concatène plusieurs messages en un seul texte brut."""
    return "\n\n---\n\n".join(message_to_text(m) for m in msgs)
