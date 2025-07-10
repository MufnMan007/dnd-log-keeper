
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
