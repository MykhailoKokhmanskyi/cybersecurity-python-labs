from contextlib import asynccontextmanager
import os
import sys

from fastapi import FastAPI

from labs.lab03.config import DOMAIN_NAME, UNIT_NAME, VARIANT_NUMBER
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from shared import student


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title=f"Lab 03 Web API - {DOMAIN_NAME}",
    description=(
        f"FastAPI application for tracking communication channels load (Variant {VARIANT_NUMBER}).\n"
        f"Domain: {DOMAIN_NAME}.\n"
        f"Unit of measurement: {UNIT_NAME} (0 - 100 percent)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(records.router)


@app.get("/ping", tags=["Service"])
def ping():
    return {"status": "ok"}


@app.get("/student", tags=["Service"])
def get_student_info():
    return {
        "student_name": getattr(student, "STUDENT_NAME", "Unknown"),
        "group_name": getattr(student, "GROUP_NAME", "Unknown"),
        "variant_number": getattr(student, "variant_number", VARIANT_NUMBER),
    }
