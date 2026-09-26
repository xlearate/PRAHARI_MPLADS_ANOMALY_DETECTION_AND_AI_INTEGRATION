"""
PRAHARI Backend — main.py
------------------------------------
Entrypoint only. All actual route logic now lives in routes/ —
this file just creates the app and plugs each router in.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import projects, anomalies, risk, feedback, mp

app = FastAPI(
    title="PRAHARI API",
    description="AI-powered monitoring system for MPLAD Scheme implementation."
)

# Allow the frontend (a separate file/port) to call this API during development.
# Tighten allow_origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(anomalies.router)
app.include_router(risk.router)
app.include_router(feedback.router)
app.include_router(mp.router)


@app.get("/")
def read_root():
    return {"project": "PRAHARI", "status": "backend running", "docs": "/docs"}