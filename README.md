# D&D Log Keeper GPT Plugin

A custom GPT-compatible API to log and retrieve Dungeons & Dragons sessions. Designed to work with OpenAI's GPT Actions.

## Features

- Add timestamped entries
- Organize by sessions
- Query and list logs
- Compatible with ChatGPT Actions
- Simple file-based backend

## Deployment

1. Deploy this repo to [Render](https://render.com).
2. Use the provided OpenAPI schema and manifest file to configure in GPT.
3. Your endpoint will be `https://<your-subdomain>.onrender.com`.

## Usage

### Log an entry
POST `/log`

```json
{
  "session_id": "descent_avernus",
  "timestamp": "2025-07-10T12:34:56Z",
  "speaker": "DM",
  "content": "You enter the hellish gate...",
  "tags": ["combat", "intro"]
}
```

### Retrieve logs
GET `/logs/descent_avernus`

### List sessions
GET `/sessions`