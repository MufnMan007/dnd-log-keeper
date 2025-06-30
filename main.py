from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# --- Configuration ---
SESSION_LOG_DIR = "session_logs"

# --- Utilities ---

def load_logs(session_id=None):
    if session_id:
        file_path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
        print(f"Looking for log file at: {file_path}")  # Debug print
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []
    else:
        logs = []
        if os.path.exists(SESSION_LOG_DIR):
            for filename in os.listdir(SESSION_LOG_DIR):
                if filename.endswith(".json"):
                    with open(os.path.join(SESSION_LOG_DIR, filename), "r") as f:
                        try:
                            logs.extend(json.load(f))
                        except json.JSONDecodeError:
                            continue
        return logs

def save_log_for_session(session_id, entry):
    os.makedirs(SESSION_LOG_DIR, exist_ok=True)
    file_path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
    print(f"Saving log to: {file_path}")  # Debug print
    logs = []
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    logs.append(entry)
    with open(file_path, "w") as f:
        json.dump(logs, f, indent=2)

# --- Auto-Logging Engine ---

def log_event(session_id, content, tags=None, npcs_involved=None, relationship_changes=None):
    if not session_id or not content:
        return

    entry = {
        "session_id": session_id,
        "content": content,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tags": tags or [],
        "npcs_involved": npcs_involved or [],
        "relationship_changes": relationship_changes or {}
    }

    save_log_for_session(session_id, entry)

def auto_log_passive_world(session_id, event_description):
    log_event(session_id, event_description, tags=["passive world event", "ambient pressure"])

def log_tactical_decision(session_id, tactical_info):
    log_event(session_id, tactical_info, tags=["tactical", "quick action"])

# --- API Endpoints ---

@app.route("/log", methods=["GET", "POST"])
@app.route("/Log", methods=["GET", "POST"])
def log_handler():
    if request.method == "POST":
        data = request.get_json()
        session_id = data.get("session_id")
        content = data.get("content")
        tags = data.get("tags", [])
        npcs_involved = data.get("npcs_involved", [])
        relationship_changes = data.get("relationship_changes", {})

        if not session_id or not content:
            return jsonify({"error": "Missing session_id or content"}), 400

        entry = {
            "session_id": session_id,
            "content": content,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tags": tags,
            "npcs_involved": npcs_involved,
            "relationship_changes": relationship_changes
        }

        save_log_for_session(session_id, entry)

        return jsonify({"message": "Log entry created", "entry": entry}), 200

    else:
        session_id = request.args.get("session_id")
        logs = load_logs(session_id)

        return jsonify({
            "log_count": len(logs),
            "logs": logs
        }), 200

@app.route("/log/auto", methods=["POST"])
def auto_log_handler():
    data = request.get_json()
    session_id = data.get("session_id")
    content = data.get("content")
    tags = data.get("tags", [])
    npcs_involved = data.get("npcs_involved", [])
    relationship_changes = data.get("relationship_changes", {})

    if not session_id or not content:
        return jsonify({"error": "Missing session_id or content"}), 400

    log_event(session_id, content, tags, npcs_involved, relationship_changes)

    return jsonify({"message": "Auto log entry created successfully."}), 200

@app.route("/Reset", methods=["GET"])
@app.route("/reset", methods=["GET"])
def reset_logs():
    if os.path.exists(SESSION_LOG_DIR):
        for filename in os.listdir(SESSION_LOG_DIR):
            file_path = os.path.join(SESSION_LOG_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    return jsonify({"message": "All logs cleared."}), 200

@app.route("/reset/<session_id>", methods=["GET"])
def reset_session(session_id):
    file_path = os.path.join(SESSION_LOG_DIR, f"{session_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({"message": f"Session {session_id} logs cleared."}), 200
    else:
        return jsonify({"message": f"Session {session_id} not found."}), 404

@app.route("/", methods=["GET"])
def index():
    logs = load_logs()
    return jsonify({
        "message": "D&D Log API is running.",
        "log_count": len(logs),
        "recent_logs": logs[-3:]
    })

@app.route("/privacy", methods=["GET"])
def serve_privacy_policy():
    return send_file("privacy.html", mimetype="text/html")

@app.route("/.well-known/ai-plugin.json", methods=["GET"])
def serve_manifest():
    return send_file(".well-known/ai-plugin.json", mimetype="application/json")

@app.route("/openapi.yaml", methods=["GET"])
def serve_openapi():
    return send_file("openapi.yaml", mimetype="application/x-yaml")

# --- Run App ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
