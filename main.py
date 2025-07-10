
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dnd_gpt_api.models import LogEntry, SessionRequest
from dnd_gpt_api.session_store import save_log, get_logs, list_sessions
import uvicorn

app = FastAPI(
    title="D&D Log Keeper GPT",
    description="API for logging and retrieving D&D sessions. Custom GPT-ready.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/log")
async def log_entry(entry: LogEntry):
    try:
        save_log(entry.session_id, entry.dict())
        return {"message": "Log saved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs/{session_id}")
async def get_session_logs(session_id: str):
    try:
        logs = get_logs(session_id)
        return {"session_id": session_id, "logs": logs}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/sessions")
async def sessions():
    return {"sessions": list_sessions()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi.responses import JSONResponse
from datetime import datetime

@app.get("/")
async def root():
    return {
        "message": "👋 Welcome to the D&D Log Keeper API! Use /log (POST), /logs/{session}, or /save/{session}/{speaker}/{content}."
    }

@app.get("/save/{session_id}/{speaker}/{content}")
async def save_via_url(session_id: str, speaker: str, content: str):
    from dnd_gpt_api.session_store import save_log
    entry = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "speaker": speaker,
        "content": content,
        "tags": []
    }
    save_log(session_id, entry)
    return {"message": f"Entry saved to session '{session_id}'"}

@app.get("/get/{session_id}")
async def alias_get(session_id: str):
    from dnd_gpt_api.session_store import get_logs
    try:
        logs = get_logs(session_id)
        return {"session_id": session_id, "logs": logs}
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

from fastapi import Request

@app.get("/log")
async def log_get_fallback(request: Request):
    params = request.query_params
    session_id = params.get("session")
    speaker = params.get("speaker", "Narrator")
    content = params.get("content", "")
    if not session_id or not content:
        return JSONResponse(status_code=400, content={"error": "Missing session or content"})
    from dnd_gpt_api.session_store import save_log
    entry = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "speaker": speaker,
        "content": content,
        "tags": []
    }
    save_log(session_id, entry)
    return {"message": f"Logged via query into {session_id}"}

@app.get("/Save/{session_id}")
async def quick_save(session_id: str):
    from dnd_gpt_api.session_store import save_log
    entry = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "speaker": "System",
        "content": "New save created.",
        "tags": ["savepoint"]
    }
    save_log(session_id, entry)
    return {"message": f"Save '{session_id}' initialized."}

@app.get("/Load/{session_id}")
async def load_session(session_id: str):
    from dnd_gpt_api.session_store import get_logs
    try:
        logs = get_logs(session_id)
        return {"session_id": session_id, "logs": logs}
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Session not found"})
