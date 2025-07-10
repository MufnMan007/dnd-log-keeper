from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dnd_gpt_api.models import LogEntry
from dnd_gpt_api.session_store import save_log, get_logs, list_sessions
from datetime import datetime
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/log")
def log_entry(entry: LogEntry):
    save_log(entry)
    return {"message": "Log saved successfully"}

@app.get("/logs/{session_id}")
def get_session_logs(session_id: str):
    logs = get_logs(session_id)
    return logs

@app.get("/sessions")
def get_all_sessions():
    return list_sessions()

@app.get("/save/{session_id}/{speaker}/{content}")
def quick_save(session_id: str, speaker: str, content: str):
    entry = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "speaker": speaker,
        "content": content,
        "tags": []
    }
    save_log(entry)
    return {"message": "Saved via /save route", "entry": entry}

@app.get("/load/{session_id}")
def load_session(session_id: str):
    logs = get_logs(session_id)
    return {"session_id": session_id, "logs": logs}

@app.delete("/clear/{session_id}")
def clear_session(session_id: str):
    path = os.path.join("session_logs", f"{session_id}.json")
    if os.path.exists(path):
        os.remove(path)
        return {"message": f"Session {session_id} cleared."}
    else:
        raise HTTPException(status_code=404, detail="Session not found")
