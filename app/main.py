import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.api.clients import router as clients_router
from app.api.client_contacts import router as client_contacts_router
from app.api.requirements import router as requirements_router
from app.api.candidates import router as candidates_router
from app.api.screenings import router as screenings_router
from app.api.submissions import router as submissions_router
from app.api.interviews import router as interviews_router
from app.api.offers import router as offers_router
from app.api.visa_processes import router as visa_processes_router
from app.api.deployments import router as deployments_router
from app.api.organizations import router as organization_router

load_dotenv()

app = FastAPI(title="Procodde CRM")

APP_URL = os.environ["APP_URL"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        APP_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root():
    return {
        "project": "Procodde CRM",
        "author": "Resty Alejo",
        "version": "1.0"
    }

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(clients_router)
app.include_router(client_contacts_router)
app.include_router(requirements_router)
app.include_router(candidates_router)
app.include_router(screenings_router)
app.include_router(submissions_router)
app.include_router(interviews_router)
app.include_router(offers_router)
app.include_router(visa_processes_router)
app.include_router(deployments_router)
app.include_router(organization_router)