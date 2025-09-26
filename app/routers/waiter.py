from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete, update
from passlib.hash import pbkdf2_sha256
from typing import List
from app.core.deps import get_db, AuthUser
from app.models.user import UserAccount
from app.models.user import ManagerLikeWaiter
from app.models.waiter import WaiterProfile, WaiterHours, WaiterExperience, WaiterPeopleSay, WaiterSkills, WaiterLookingFor
from app.schemas.waiter import WaiterCreate, WaiterOut, WaiterUpdate, HourTag, ExpTag, SayTag, SkillTag, LookingFor


router = APIRouter(prefix="/waiters", tags=["waiters"])


def _set_multiselects(db: Session, user_id: int, hours: List[HourTag], experience: List[ExpTag], people_say: List[SayTag], skills: List[SkillTag], looking_for: List[LookingFor]):
    db.execute(delete(WaiterHours).where(WaiterHours.user_id == user_id))
    for tag in hours:
        db.add(WaiterHours(user_id=user_id, hour_tag=tag))
    db.execute(delete(WaiterExperience).where(WaiterExperience.user_id == user_id))
    for tag in experience:
        db.add(WaiterExperience(user_id=user_id, exp_tag=tag))
    db.execute(delete(WaiterPeopleSay).where(WaiterPeopleSay.user_id == user_id))
    for tag in people_say:
        db.add(WaiterPeopleSay(user_id=user_id, say_tag=tag))
    db.execute(delete(WaiterSkills).where(WaiterSkills.user_id == user_id))
    for tag in skills:
        db.add(WaiterSkills(user_id=user_id, skill_tag=tag))
    db.execute(delete(WaiterLookingFor).where(WaiterLookingFor.user_id == user_id))
    for tag in looking_for:
        db.add(WaiterLookingFor(user_id=user_id, looking_for=tag))


def _aggregate_waiter(db: Session, user: UserAccount) -> WaiterOut:
    prof = db.execute(select(WaiterProfile).where(WaiterProfile.user_id == user.id)).scalar_one_or_none()
    if not prof:
        raise HTTPException(404, "Waiter profile not found")
    hours = [r[0] for r in db.execute(select(WaiterHours.hour_tag).where(WaiterHours.user_id == user.id)).all()]
    exp = [r[0] for r in db.execute(select(WaiterExperience.exp_tag).where(WaiterExperience.user_id == user.id)).all()]
    say = [r[0] for r in db.execute(select(WaiterPeopleSay.say_tag).where(WaiterPeopleSay.user_id == user.id)).all()]
    skl = [r[0] for r in db.execute(select(WaiterSkills.skill_tag).where(WaiterSkills.user_id == user.id)).all()]
    lf = [r[0] for r in db.execute(select(WaiterLookingFor.looking_for).where(WaiterLookingFor.user_id == user.id)).all()]
    return WaiterOut(
        user_id=user.id,
        display_name=user.display_name,
        email=user.email,
        status=prof.status,
        looking_for=lf,
        about_me=prof.about_me,
        distance_km=prof.distance_km,
        min_hourly_wage=float(prof.min_hourly_wage) if prof.min_hourly_wage is not None else None,
        shifts_per_week=prof.shifts_per_week,
        hours=hours,
        experience=exp,
        people_say=say,
        skills=skl
    )


@router.post("/", response_model=WaiterOut, dependencies=[Depends(AuthUser)])
def create_waiter(data: WaiterCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(UserAccount).where(UserAccount.email == data.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(400, "Email already registered")
    user = UserAccount(
        email=data.email,
        password_hash=pbkdf2_sha256.hash(data.password),
        display_name=data.display_name,
        user_type="waiter",
    )
    db.add(user)
    db.flush()

    profile = WaiterProfile(
        user_id=user.id,
        status=data.status,
        about_me=data.about_me,
        distance_km=data.distance_km,
        min_hourly_wage=data.min_hourly_wage,
        shifts_per_week=data.shifts_per_week,
    )
    db.add(profile)
    _set_multiselects(db, user.id, data.hours, data.experience, data.people_say, data.skills, data.looking_for)
    db.commit()
    db.refresh(user)
    return _aggregate_waiter(db, user)


@router.get("/{user_id}", response_model=WaiterOut, dependencies=[Depends(AuthUser)])
def get_waiter(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(UserAccount).where(UserAccount.id == user_id, UserAccount.user_type == "waiter")).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Not found")
    return _aggregate_waiter(db, user)


@router.put("/{user_id}", response_model=WaiterOut, dependencies=[Depends(AuthUser)])
def update_waiter(user_id: int, data: WaiterUpdate, db: Session = Depends(get_db)):
    user = db.execute(select(UserAccount).where(UserAccount.id == user_id, UserAccount.user_type == "waiter")).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Not found")
    if data.display_name is not None:
        db.execute(update(UserAccount).where(UserAccount.id == user_id).values(display_name=data.display_name))
    prof = db.execute(select(WaiterProfile).where(WaiterProfile.user_id == user_id)).scalar_one_or_none()
    if not prof:
        raise HTTPException(404, "Waiter profile not found")
    updates = {}
    for field in ["status", "about_me", "distance_km", "min_hourly_wage", "shifts_per_week"]:
        value = getattr(data, field)
        if value is not None and not (isinstance(value, list)):
            updates[field] = value
    if updates:
        db.execute(update(WaiterProfile).where(WaiterProfile.user_id == user_id).values(**updates))
    if any([data.hours, data.experience, data.people_say, data.skills, data.looking_for]):
        _set_multiselects(
            db,
            user_id,
            data.hours or [],
            data.experience or [],
            data.people_say or [],
            data.skills or [],
            data.looking_for or []
        )
    db.commit()
    user = db.execute(select(UserAccount).where(UserAccount.id == user_id)).scalar_one()
    return _aggregate_waiter(db, user)


@router.delete("/{user_id}", dependencies=[Depends(AuthUser)])
def delete_waiter(user_id: int, db: Session = Depends(get_db)):
    user = db.execute(select(UserAccount).where(UserAccount.id == user_id, UserAccount.user_type == "waiter")).scalar_one_or_none()
    if not user:
        raise HTTPException(404, "Not found")
    db.execute(delete(UserAccount).where(UserAccount.id == user_id))
    db.commit()
    return {"ok": True}


@router.post("/{waiter_user_id}/like", dependencies=[Depends(AuthUser)])
def like_waiter(waiter_user_id: int, db: Session = Depends(get_db), user=Depends(AuthUser)):
    # only business managers can like waiter profiles
    if user.user_type != "business_manager":
        raise HTTPException(403, "Only managers can like waiters")
    exists = db.execute(select(ManagerLikeWaiter).where(ManagerLikeWaiter.manager_user_id == user.id, ManagerLikeWaiter.waiter_user_id == waiter_user_id)).scalar_one_or_none()
    if not exists:
        db.add(ManagerLikeWaiter(manager_user_id=user.id, waiter_user_id=waiter_user_id))
        db.commit()
    # check mutual like (waiter liked any role of this manager's businesses)
    from app.models.role import Role, RoleLike
    from app.models.business import Business
    role_ids = [r.id for r in db.execute(select(Role).join(Business, Role.business_id == Business.id).where(Business.manager_user_id == user.id)).scalars().all()]
    if role_ids:
        mutual = db.execute(select(RoleLike).where(RoleLike.user_id == waiter_user_id, RoleLike.role_id.in_(role_ids))).first()
    else:
        mutual = None
    if mutual:
        from app.models.notification import Notification
        db.add(Notification(user_id=waiter_user_id, type="new_match", payload={"manager_user_id": user.id}))
        db.add(Notification(user_id=user.id, type="new_match", payload={"waiter_user_id": waiter_user_id}))
        db.commit()
        return {"liked": True, "mutual_match": True}
    return {"liked": True, "mutual_match": False}

