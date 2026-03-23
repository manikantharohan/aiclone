# Deployment Guide — AI Chatbot

## Local development

- **Backend:** `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`  
  (Set `HF_TOKEN` in `.env` at project root or in `backend/`.)

- **Frontend:** `cd frontend && npm install && npm run dev`  
  App: http://localhost:5173. WebSocket connects to `ws://localhost:8000` in dev.

- **Docker:** From project root, run `docker compose up --build`.  
  Backend: http://localhost:8000. Frontend: http://localhost:3000.  
  Set `HF_TOKEN` in `.env` (and optionally `VITE_WS_URL=http://localhost:8000` for frontend build).

---

## Render (backend)

1. New **Web Service**. Connect repo; root directory: project root.
2. **Build:**  
   - Build command: `pip install -r backend/requirements.txt`  
   - Start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Environment:** Add `HF_TOKEN`, `HF_BASE_URL` (optional), `HF_MODEL` (optional).  
   Add `CORS_ORIGINS` with your frontend URL (e.g. `https://your-app.vercel.app`).
4. Deploy. Note the backend URL (e.g. `https://your-backend.onrender.com`).

---

## Vercel (frontend)

1. Import the repo. Set **Root Directory** to `frontend`.
2. **Build:**  
   - Build command: `npm run build`  
   - Output directory: `dist`.
3. **Environment variables:**  
   - `VITE_WS_URL` = your backend base URL (e.g. `https://your-backend.onrender.com`).  
   The app will use `ws://` or `wss://` from that (e.g. `wss://your-backend.onrender.com` for WebSocket).
4. Deploy. Then set the same URL in the backend’s `CORS_ORIGINS` (e.g. `https://your-app.vercel.app`).

---

## Railway

1. **Backend:** New project → Deploy from repo.  
   - Root: project root.  
   - Build: `pip install -r backend/requirements.txt`  
   - Start: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`  
   - Env: `HF_TOKEN`, `CORS_ORIGINS` (frontend URL).
2. **Frontend:** New service from same repo.  
   - Root: `frontend`.  
   - Build: `npm install && npm run build`.  
   - Start: e.g. use `npx serve -s dist` or a static server; or add a small Node server that serves `dist` and set start command.  
   - Env: `VITE_WS_URL` = backend URL (e.g. `https://your-backend.railway.app`).
3. Set backend `CORS_ORIGINS` to the Railway frontend URL.

---

## Hugging Face Spaces (optional UI hosting)

- **Backend:** Not typical on Spaces; use Render/Railway/Fly.io for the FastAPI backend.
- **Frontend only on Spaces:**  
  - Create a **Static** Space.  
  - Build frontend locally with `VITE_WS_URL` set to your deployed backend URL:  
    `npm run build` in `frontend/`.  
  - Upload contents of `frontend/dist` to the Space.  
  - Set backend `CORS_ORIGINS` to include the Space URL (e.g. `https://your-username-your-space.hf.space`).

---

## Security checklist

- Never put `HF_TOKEN` in frontend code or in frontend env that is exposed to the client.
- Keep `CORS_ORIGINS` limited to your real frontend origin(s).
- Use `wss://` in production when the backend is served over HTTPS.
