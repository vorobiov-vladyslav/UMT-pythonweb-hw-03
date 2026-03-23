# HW3 — Simple HTTP Server

A minimal Python HTTP server built with `http.server` and Jinja2.

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)

```bash
uv pip install -r requirements.txt
```

## Run locally

```bash
python main.py
```

Open http://localhost:3000

## Run with Docker

```bash
docker build -t hw3 .
docker run -v $(pwd)/storage:/app/storage -p 3000:3000 hw3
```

## Routes

| Route | Description |
|---|---|
| `GET /` | Home page |
| `GET /message.html` | Message form |
| `POST /message` | Submit a message (redirects to `/`) |
| `GET /read` | View all saved messages |
| anything else | 404 error page |

## Testing

1. Open http://localhost:3000 — home page loads
2. Click **Send message**, fill the form, submit — redirects to home
3. Open http://localhost:3000/read — submitted messages are listed
4. Open http://localhost:3000/nonexistent — 404 error page appears
5. Check `storage/data.json` — messages are saved with timestamps as keys
