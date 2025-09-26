Waiter Job Search – Backend (FastAPI + MySQL)
Overview

A simple, production-lean backend for a hospitality job-matching app.

Tech: FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic (optional), MySQL 8, Uvicorn, Nginx

Auth: JWT (access_token, refresh_token, timeout_token)

Token enforcement: Depends checks token_table (user_id, token, modification_time) on each request

Reports: Generic /reports/run executes configured stored procedures with validated parameters

Deploy: Dockerized multi-instance on EC2, Nginx on port 80, Git push to CodeCommit → CodePipeline → CodeDeploy

Configs: settings.json (always loaded) + environment overrides (settings-stage.json, settings-prod.json) picked by after-install script

Data Model
Users

We’ll keep two user categories with shared base fields and separate tables for domain specifics:

Waiter (job seeker)

BusinessManager (employer) → manages Business records and job Roles

Enumerations

waiter_status: pre_army | post_army | student | other

looking_for: waiter | bartender | barista | hostess | shift_manager | manager

hours: multiple choice: part_time | full_time | morning | evening | weekends

experience_tags: multi-select: waiter | barman | barista | shift_manager | host

people_say: multi-select: best_coffee_maker | good_vibe | best_cocktails | customers_love_me

skills: multi-select: customer_service | basic_computer | coffee_making | teamwork | food_service | working_under_pressure | table_management

business_type: bar | restaurant | cafe | hotel

role_position: waiter | bartender | barista | hostess | shift_manager

experience_required: no_experience | some_experience | experience_only

when_need: this_week | always_looking

shift_when: multi-select: morning | evening | weekends | full_time | part_time

We store multi-selects as junction tables for queryability.

MySQL DDL
-- Database and charset
CREATE DATABASE IF NOT EXISTS waiter_jobs DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE waiter_jobs;

-- Users (base auth)
CREATE TABLE user_account (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  display_name VARCHAR(255) NOT NULL,
  user_type ENUM('waiter','business_manager') NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Token table (checked via Depends on each request)
CREATE TABLE token_table (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  token VARCHAR(512) NOT NULL,
  modification_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_token_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_token_user (user_id),
  KEY idx_token (token(191))
) ENGINE=InnoDB;

-- Waiter profile
CREATE TABLE waiter_profile (
  user_id BIGINT UNSIGNED PRIMARY KEY,
  status ENUM('pre_army','post_army','student','other') NOT NULL,
  looking_for ENUM('waiter','bartender','barista','hostess','shift_manager','manager') NOT NULL,
  about_me TEXT NULL,
  distance_km INT NULL,
  min_hourly_wage DECIMAL(10,2) NULL,
  shifts_per_week INT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_waiter_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Multi-selects for waiter
CREATE TABLE waiter_hours (
  user_id BIGINT UNSIGNED NOT NULL,
  hour_tag ENUM('part_time','full_time','morning','evening','weekends') NOT NULL,
  PRIMARY KEY (user_id, hour_tag),
  CONSTRAINT fk_waiter_hours_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE waiter_experience (
  user_id BIGINT UNSIGNED NOT NULL,
  exp_tag ENUM('waiter','barman','barista','shift_manager','host') NOT NULL,
  PRIMARY KEY (user_id, exp_tag),
  CONSTRAINT fk_waiter_exp_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE waiter_people_say (
  user_id BIGINT UNSIGNED NOT NULL,
  say_tag ENUM('best_coffee_maker','good_vibe','best_cocktails','customers_love_me') NOT NULL,
  PRIMARY KEY (user_id, say_tag),
  CONSTRAINT fk_waiter_say_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE waiter_skills (
  user_id BIGINT UNSIGNED NOT NULL,
  skill_tag ENUM('customer_service','basic_computer','coffee_making','teamwork','food_service','working_under_pressure','table_management') NOT NULL,
  PRIMARY KEY (user_id, skill_tag),
  CONSTRAINT fk_waiter_skill_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Businesses
CREATE TABLE business (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  manager_user_id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(255) NOT NULL,
  location VARCHAR(255) NOT NULL,
  menu_url VARCHAR(500) NULL,
  business_type ENUM('bar','restaurant','cafe','hotel') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_business_manager FOREIGN KEY (manager_user_id) REFERENCES user_account(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Roles (job postings)
CREATE TABLE role (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  business_id BIGINT UNSIGNED NOT NULL,
  position ENUM('waiter','bartender','barista','hostess','shift_manager') NOT NULL,
  payment_per_hour DECIMAL(10,2) NOT NULL,
  location VARCHAR(255) NOT NULL,
  when_need ENUM('this_week','always_looking') NOT NULL,
  experience_required ENUM('no_experience','some_experience','experience_only') NOT NULL,
  shift_morning TINYINT(1) NOT NULL DEFAULT 0,
  shift_evening TINYINT(1) NOT NULL DEFAULT 0,
  shift_weekends TINYINT(1) NOT NULL DEFAULT 0,
  shift_full_time TINYINT(1) NOT NULL DEFAULT 0,
  shift_part_time TINYINT(1) NOT NULL DEFAULT 0,
  about_job TEXT NULL,
  min_hourly_wage DECIMAL(10,2) NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_role_business FOREIGN KEY (business_id) REFERENCES business(id) ON DELETE CASCADE,
  KEY idx_role_active (is_active, position)
) ENGINE=InnoDB;

-- Notifications
CREATE TABLE notification (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT UNSIGNED NOT NULL,
  type ENUM(
    'upcoming_interview',
    'new_match',
    'business_liked_you',
    'interview_succeeded',
    'arriving_for_shift',
    'new_message'
  ) NOT NULL,
  payload JSON NULL,
  scheduled_at DATETIME NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  read_at DATETIME NULL,
  CONSTRAINT fk_notification_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_notification_user (user_id, created_at)
) ENGINE=InnoDB;

-- Reports config
CREATE TABLE report_configuration (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  report_name VARCHAR(255) NOT NULL UNIQUE,
  parameters JSON NOT NULL, -- [{ "parameter_name": "...", "is_mandatory": true/false, "default_value": ... }]
  procedure_name VARCHAR(255) NOT NULL, -- e.g., "sp_roles_by_position"
  is_active TINYINT(1) NOT NULL DEFAULT 1,
  creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  modification_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Example stored procedure (report)
DELIMITER $$
CREATE PROCEDURE sp_roles_by_position(IN p_position VARCHAR(32))
BEGIN
  SELECT r.*, b.name AS business_name
  FROM role r
  JOIN business b ON b.id = r.business_id
  WHERE r.position = p_position AND r.is_active = 1
  ORDER BY r.created_at DESC
  LIMIT 200;
END$$
DELIMITER ;

FastAPI Structure
app/
  core/
    config.py
    security.py
    deps.py
  models/
    base.py
    user.py
    waiter.py
    business.py
    role.py
    notification.py
    report.py
    token.py
  schemas/
    auth.py
    waiter.py
    business.py
    role.py
    notification.py
    report.py
    common.py
  routers/
    auth.py
    waiter.py
    business.py
    role.py
    notification.py
    report.py
  main.py
settings.json
settings-stage.json
settings-prod.json
Dockerfile
docker-compose.yml
nginx.conf
after_install.sh

core/config.py

Loads settings.json first, then merges env-specific overrides (the after-install script copies the chosen env file over settings.json prior to container start).

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

core/security.py

JWT utilities.

from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import settings

def _encode(payload: dict, exp_minutes: int):
    to_encode = payload.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)

def create_tokens(user_id: int):
    access_token = _encode({"sub": str(user_id), "typ": "access"}, settings.access_minutes)
    refresh_token = _encode({"sub": str(user_id), "typ": "refresh"}, settings.refresh_days * 24 * 60)
    timeout_token = _encode({"sub": str(user_id), "typ": "timeout"}, settings.timeout_minutes)
    return access_token, refresh_token, timeout_token

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])

core/deps.py

DB session + token check (checks token_table via Depends for every protected endpoint).

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.models.base import SessionLocal
from app.core.security import decode_token
from app.models.token import TokenRecord
from app.models.user import UserAccount

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_token(token: str, db: Session) -> UserAccount:
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = int(payload.get("sub", 0))
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid subject")

    # Enforce presence in token_table
    rec = db.execute(
        select(TokenRecord).where(TokenRecord.user_id == user_id, TokenRecord.token == token)
    ).scalar_one_or_none()

    if not rec:
        raise HTTPException(status_code=401, detail="Token not registered")

    user = db.execute(select(UserAccount).where(UserAccount.id == user_id)).scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive user")
    return user

def AuthUser(token: str = Depends(lambda authorization: authorization), db: Session = Depends(get_db)):
    # Expect "Authorization: Bearer <token>"
    # We depend on the raw header being forwarded into this lambda by FastAPI; for simplicity in Cursor:
    import os
    import starlette.requests
    # fallback: read from environ for local testing (set by middleware) – you can replace with request headers
    token_hdr = os.environ.get("AUTH_BEARER", "")
    if token_hdr.startswith("Bearer "):
        token = token_hdr.split(" ", 1)[1]
    elif token_hdr:
        token = token_hdr
    else:
        # If using a real app, you’d extract from request headers via a custom dependency/middleware.
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    return require_token(token, db)


In a real app, parse Authorization header directly from the request object. Cursor simplification above shows the logic clearly.

SQLAlchemy Base (models/base.py)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(settings.mysql_dsn, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

Example Models (snippets)

models/user.py

from sqlalchemy import Column, BigInteger, String, Enum, Boolean, TIMESTAMP, func
from app.models.base import Base

class UserAccount(Base):
    __tablename__ = "user_account"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    user_type = Column(Enum("waiter","business_manager", name="user_type_enum"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)


models/token.py

from sqlalchemy import Column, BigInteger, String, TIMESTAMP, func, ForeignKey
from app.models.base import Base

class TokenRecord(Base):
    __tablename__ = "token_table"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(512), nullable=False)
    modification_time = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)


(Analogous models for waiter/business/role/notification with columns matching the DDL.)

Pydantic Schemas (snippets)

schemas/auth.py

from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    timeout_token: str


schemas/waiter.py – demonstrates enums & lists

from pydantic import BaseModel, Field
from typing import List, Optional, Literal

Status = Literal['pre_army','post_army','student','other']
LookingFor = Literal['waiter','bartender','barista','hostess','shift_manager','manager']
HourTag = Literal['part_time','full_time','morning','evening','weekends']
ExpTag = Literal['waiter','barman','barista','shift_manager','host']
SayTag = Literal['best_coffee_maker','good_vibe','best_cocktails','customers_love_me']
SkillTag = Literal['customer_service','basic_computer','coffee_making','teamwork','food_service','working_under_pressure','table_management']

class WaiterCreate(BaseModel):
    display_name: str
    email: str
    password: str
    status: Status
    looking_for: LookingFor
    about_me: Optional[str] = None
    distance_km: Optional[int] = None
    min_hourly_wage: Optional[float] = None
    shifts_per_week: Optional[int] = None
    hours: List[HourTag] = Field(default_factory=list)
    experience: List[ExpTag] = Field(default_factory=list)
    people_say: List[SayTag] = Field(default_factory=list)
    skills: List[SkillTag] = Field(default_factory=list)


(Analogous schemas for Business, Role, Notification.)

Routers (endpoints)
Auth (/auth)

POST /auth/login → returns {access_token, refresh_token, timeout_token} and inserts access_token into token_table.

POST /auth/refresh → returns new access_token (and optionally rotates).

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from passlib.hash import bcrypt
from app.schemas.auth import LoginRequest, LoginResponse
from app.models.user import UserAccount
from app.models.token import TokenRecord
from app.core.security import create_tokens
from app.core.deps import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(select(UserAccount).where(UserAccount.email == payload.email)).scalar_one_or_none()
    if not user or not bcrypt.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    a, r, t = create_tokens(user.id)
    db.execute(insert(TokenRecord).values(user_id=user.id, token=a))
    db.commit()
    return LoginResponse(access_token=a, refresh_token=r, timeout_token=t)

Waiters (/waiters)

CRUD with Depends(AuthUser) to enforce token check via token_table.

Similar routers for /businesses, /roles, /notifications.

Example create waiter:

@router.post("/", response_model=WaiterOut, dependencies=[Depends(AuthUser)])
def create_waiter(data: WaiterCreate, db: Session = Depends(get_db)):
    # create user_account, waiter_profile, and insert multiselect rows
    ...

Reports (/reports)

Generic report runner that validates parameters based on report_configuration.parameters JSON and calls the stored procedure.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, select
from app.core.deps import get_db, AuthUser
from app.models.report import ReportConfiguration
import json

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/run", dependencies=[Depends(AuthUser)])
def run_report(body: dict, db: Session = Depends(get_db)):
    report_name = body.get("report_name")
    params = body.get("parameters", {})

    cfg = db.execute(
        select(ReportConfiguration).where(ReportConfiguration.report_name == report_name, ReportConfiguration.is_active == 1)
    ).scalar_one_or_none()
    if not cfg:
        raise HTTPException(status_code=404, detail="Report not found")

    schema = json.loads(cfg.parameters)
    # Validate params, apply defaults
    call_args = []
    for p in schema:
        name = p["parameter_name"]
        mandatory = bool(p.get("is_mandatory"))
        if name in params:
            call_args.append(params[name])
        elif not mandatory:
            call_args.append(p.get("default_value"))
        else:
            raise HTTPException(status_code=400, detail=f"Missing parameter: {name}")

    # Build CALL statement with placeholders
    placeholders = ",".join(["%s"] * len(call_args))
    sql = text(f"CALL {cfg.procedure_name}({placeholders})")

    res = db.execute(sql, tuple(call_args))
    rows = [dict(r._mapping) for r in res]
    # Some MySQL drivers require fetching next result sets for CALL; keep simple here.
    return {"report_name": report_name, "rows": rows}

Example Endpoints Summary

POST /auth/login → {access_token, refresh_token, timeout_token}

POST /auth/refresh

CRUD /waiters

CRUD /businesses

CRUD /roles

GET /notifications (all / unread), POST /notifications (for system ops), PATCH /notifications/{id}/read

POST /reports/run → {report_name, rows:[...]}

Docker & Nginx
Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y build-essential default-mysql-client && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY . .

# Expose app port
EXPOSE 8000

# Entrypoint
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]

requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
pydantic==2.9.2
SQLAlchemy==2.0.36
pymysql==1.1.1
passlib[bcrypt]==1.7.4
pyjwt==2.9.0

nginx.conf

Balances across multiple app instances.

worker_processes auto;
events { worker_connections 1024; }

http {
  upstream app_cluster {
    server app1:8000;
    server app2:8000;
    server app3:8000;
  }

  server {
    listen 80;
    server_name _;

    client_max_body_size 20m;

    location / {
      proxy_pass http://app_cluster;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
    }
  }
}

docker-compose.yml

Runs 3 app instances + Nginx + MySQL.

version: "3.9"
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root
      MYSQL_DATABASE: waiter_jobs
    ports: ["3306:3306"]
    volumes:
      - db_data:/var/lib/mysql

  app1: &app
    build: .
    environment:
      # after_install.sh will ensure settings.json is correct
    depends_on: [mysql]
  app2:
    <<: *app
  app3:
    <<: *app

  nginx:
    image: nginx:1.27
    ports: ["80:80"]
    depends_on: [app1, app2, app3]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro

volumes:
  db_data:

Settings

Always use settings.json at runtime. The after-install script copies the relevant env file onto it.

settings.json (base shape)
{
  "app_name": "WaiterJobs",
  "jwt_secret": "CHANGE_ME",
  "jwt_alg": "HS256",
  "access_minutes": 30,
  "refresh_days": 30,
  "timeout_minutes": 5,
  "mysql_dsn": "mysql+pymysql://root:root@mysql:3306/waiter_jobs"
}

settings-stage.json
{
  "jwt_secret": "CHANGE_STAGE_SECRET",
  "mysql_dsn": "mysql+pymysql://root:root@mysql:3306/waiter_jobs"
}

settings-prod.json
{
  "jwt_secret": "CHANGE_PROD_SECRET",
  "mysql_dsn": "mysql+pymysql://appuser:STRONGPASS@mysql:3306/waiter_jobs"
}

After-Install Script

after_install.sh – picks config by deployment tag and starts Docker.

#!/usr/bin/env bash
set -euo pipefail

DEPLOY_TAG="${DEPLOY_TAG:-stage}"  # export DEPLOY_TAG=prod|stage|dev before running

echo "[after_install] Using DEPLOY_TAG=${DEPLOY_TAG}"

case "$DEPLOY_TAG" in
  prod)
    cp settings-prod.json settings.json
    ;;
  stage)
    cp settings-stage.json settings.json
    ;;
  *)
    echo "Unknown DEPLOY_TAG '${DEPLOY_TAG}', defaulting to stage"
    cp settings-stage.json settings.json
    ;;
esac

echo "[after_install] Building and starting containers..."
docker compose down || true
docker compose build --no-cache
docker compose up -d

echo "[after_install] Done."

AWS CI/CD (CodeCommit → CodePipeline → CodeDeploy → EC2)
High-level

Repo: Push this project to CodeCommit.

EC2: Amazon Linux 2 instance with:

Docker & docker-compose plugin installed

IAM role permitting CodeDeploy

Security group open on 80 (and 22 for SSH)

CodeDeploy App/Deployment Group: Tag your EC2 (e.g., Role=WaiterJobsStage).

CodePipeline: Source (CodeCommit) → Deploy (CodeDeploy).

appspec.yml (for CodeDeploy on EC2)
version: 0.0
os: linux
files:
  - source: /
    destination: /opt/waiterjobs
permissions:
  - object: /opt/waiterjobs
    owner: root
    group: root
    mode: 755
hooks:
  AfterInstall:
    - location: after_install.sh
      timeout: 900
      runas: root


Ensure after_install.sh is executable (chmod +x after_install.sh) and that DEPLOY_TAG is passed via CodeDeploy environment or pulled from an instance tag (you can read it in the script via aws ec2 describe-tags if needed).

Example Usage Flow

Business Manager registers & logs in.

Creates a Business and then creates Role postings.

Waiter registers & logs in; fills preferences (hours, skills, experience, wage expectation).

Matching can be implemented later (e.g., endpoint to suggest roles based on skills/hours/wage/distance).

Notifications added for:

“Upcoming Interview” → payload: { "business_name": "...", "day": "YYYY-MM-DD", "time": "HH:MM" }

“New match!” / “Bar liked your profile”

“Interview succeeded”

“Arriving for shift …”

“New message”

What’s Included vs. Next Steps

Included now

Schema & DDL for all listed fields (no guessing; exact names).

Auth with access_token, refresh_token, timeout_token.

token_table enforcement via Depends.

Generic reports infra with config + stored procedure example.

CRUD scaffolding (patterns + example).

Docker + multi-instance + Nginx LB.

Config files & after-install script.

CI/CD blueprint for EC2.

Recommended next steps (optional)

Add Alembic migrations.

Proper header parsing middleware for Authorization: Bearer <token>.

Background scheduler for notifications (e.g., APScheduler / Celery).

Matching engine endpoint (/matches/suggest).

Rate limiting / request logging.

Email/SMS integration (interview reminders).

S3 for media (menus) if needed.


Add-On: In-App Messaging (Conversations & Messages)

USE waiter_jobs;

-- Conversation container (N participants)
CREATE TABLE conversation (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Which users are in a conversation
CREATE TABLE conversation_participant (
  conversation_id BIGINT UNSIGNED NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (conversation_id, user_id),
  CONSTRAINT fk_conv_participant_conv FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE,
  CONSTRAINT fk_conv_participant_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_conv_part_user (user_id, conversation_id)
) ENGINE=InnoDB;

-- Messages
CREATE TABLE message (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  conversation_id BIGINT UNSIGNED NOT NULL,
  sender_user_id BIGINT UNSIGNED NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  read_at DATETIME NULL,
  CONSTRAINT fk_msg_conv FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE,
  CONSTRAINT fk_msg_sender FOREIGN KEY (sender_user_id) REFERENCES user_account(id) ON DELETE CASCADE,
  KEY idx_msg_conv_created (conversation_id, created_at),
  KEY idx_msg_unread (conversation_id, read_at)
) ENGINE=InnoDB;


ALTER TABLE waiter_profile
  ADD COLUMN latitude DECIMAL(9,6) NULL,
  ADD COLUMN longitude DECIMAL(9,6) NULL,
  ADD COLUMN location_point POINT SRID 4326 NULL,
  ADD SPATIAL INDEX spx_waiter_location (location_point);

ALTER TABLE business
  ADD COLUMN latitude DECIMAL(9,6) NULL,
  ADD COLUMN longitude DECIMAL(9,6) NULL,
  ADD COLUMN location_point POINT SRID 4326 NULL,
  ADD SPATIAL INDEX spx_business_location (location_point);

ALTER TABLE role
  ADD COLUMN latitude DECIMAL(9,6) NULL,
  ADD COLUMN longitude DECIMAL(9,6) NULL,
  ADD COLUMN location_point POINT SRID 4326 NULL,
  ADD SPATIAL INDEX spx_role_location (location_point);

-- Ensure POINT is set consistently with lon,lat order
-- Example for role:
UPDATE role
SET location_point = IF(latitude IS NULL OR longitude IS NULL, NULL, ST_SRID(POINT(longitude, latitude), 4326))
WHERE id = :role_id;

Distance Query (Haversine / sphere)

MySQL 8 has ST_Distance_Sphere(a,b) (meters). Example: find roles within 10 km from a given (lat, lon):

SET @lat := 32.08088;   -- Tel Aviv example
SET @lon := 34.78057;
SET @pt := ST_SRID(POINT(@lon, @lat), 4326);

SELECT
  r.*,
  b.name AS business_name,
  ST_Distance_Sphere(r.location_point, @pt) / 1000 AS distance_km
FROM role r
JOIN business b ON b.id = r.business_id
WHERE r.location_point IS NOT NULL
  AND ST_Distance_Sphere(r.location_point, @pt) <= 10000  -- 10km
ORDER BY distance_km ASC
LIMIT 200;


For performance: pre-filter with a bounding box using MBRContains or lat/lon ranges, then apply ST_Distance_Sphere precisely.
