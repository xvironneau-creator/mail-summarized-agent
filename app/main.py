from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.gmail_client import fetch_messages_by_label, concat_messages_text
from app.agents import run_summary_async

app = FastAPI(title="Gmail Summarizer API")
_last_summary_cache = {"summary": ""}

class SumReq(BaseModel):
    label: str = "label:inbox newer_than:7d"
    max_results: int = 10

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/sum")
async def summarize(req: SumReq):
    """Récupère les mails Gmail d’un label et renvoie un résumé."""
    try:
        msgs = fetch_messages_by_label(req.label, max_results=req.max_results)
        if not msgs:
            return {"summary": "Aucun mail trouvé.", "count": 0}
        text = concat_messages_text(msgs)
        summary = await run_summary_async(
            f"Résume clairement les emails suivants :\n\n{text}"
        )
        _last_summary_cache["summary"] = summary
        return {"summary": summary, "count": len(msgs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/last")
def last_summary():
    """Renvoie le dernier résumé stocké en mémoire."""
    return {"summary": _last_summary_cache.get("summary", "")}
