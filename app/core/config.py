import json, os
from pydantic import BaseModel

class Settings(BaseModel):
    app_name: str = "WaiterJobs"
    jwt_secret: str
    jwt_alg: str = "HS256"
    access_minutes: int = 30
    refresh_days: int = 30
    timeout_minutes: int = 5
    mysql_dsn: str  # e.g. mysql+pymysql://user:pass@mysql:3306/waiter_jobs

def load_settings() -> Settings:
    # always read settings.json (after_install.sh ensures it points to correct env values)
    with open("settings.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return Settings(**data)

settings = load_settings()