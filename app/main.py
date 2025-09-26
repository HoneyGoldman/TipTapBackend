import sys
from pathlib import Path

# Allow running this file directly: python app/main.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.routers import chat, auth, waiter, business, role, notification, report

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.models.base import Base, engine


def apply_bearer_openapi(app: FastAPI):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="WaiterJobs API",
            version="1.0.0",
            description="Hospitality job-matching backend",
            routes=app.routes,
        )
        openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
        openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
        openapi_schema["security"] = [{"BearerAuth": []}]
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    app.openapi = custom_openapi


app = FastAPI(title="WaiterJobs API")
apply_bearer_openapi(app)


@app.on_event("startup")
def on_startup():
    # Create tables if not exist (for quick start; in prod use Alembic)
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(waiter.router)
app.include_router(business.router)
app.include_router(role.router)
app.include_router(notification.router)
app.include_router(report.router)
app.include_router(chat.router)

# python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
