from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from typing import List
from app.core.deps import get_db, AuthUser
from app.models.role import Role, RoleLike
from app.models.business import Business, BusinessManager
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut


router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RoleOut, dependencies=[Depends(AuthUser)])
def create_role(payload: RoleCreate, db: Session = Depends(get_db), user=Depends(AuthUser)):
    owned = db.execute(select(BusinessManager).where(BusinessManager.business_id == payload.business_id, BusinessManager.manager_user_id == user.id)).first()
    if not owned:
        raise HTTPException(403, "Not your business")
    r = Role(**payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return RoleOut(**{
        "id": r.id,
        "business_id": r.business_id,
        "position": r.position,
        "payment_per_hour": float(r.payment_per_hour),
        "location": r.location,
        "latitude": r.latitude,
        "longitude": r.longitude,
        "when_need": r.when_need,
        "experience_required": r.experience_required,
        "shift_morning": r.shift_morning,
        "shift_evening": r.shift_evening,
        "shift_weekends": r.shift_weekends,
        "shift_full_time": r.shift_full_time,
        "shift_part_time": r.shift_part_time,
        "about_job": r.about_job,
        "min_hourly_wage": float(r.min_hourly_wage) if r.min_hourly_wage is not None else None,
        "is_active": r.is_active,
    })


@router.get("", response_model=List[RoleOut], dependencies=[Depends(AuthUser)])
@router.get("/", response_model=List[RoleOut], dependencies=[Depends(AuthUser)])
def list_roles(db: Session = Depends(get_db), user=Depends(AuthUser)):
    # Auth listing: return active roles not yet liked by user
    subq = select(RoleLike.role_id).where(RoleLike.user_id == user.id)
    rows = db.execute(select(Role).where(Role.is_active == True, Role.id.not_in(subq))).scalars().all()
    out = []
    for r in rows:
        out.append(RoleOut(**{
            "id": r.id,
            "business_id": r.business_id,
            "position": r.position,
            "payment_per_hour": float(r.payment_per_hour),
            "location": r.location,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "when_need": r.when_need,
            "experience_required": r.experience_required,
            "shift_morning": r.shift_morning,
            "shift_evening": r.shift_evening,
            "shift_weekends": r.shift_weekends,
            "shift_full_time": r.shift_full_time,
            "shift_part_time": r.shift_part_time,
            "about_job": r.about_job,
            "min_hourly_wage": float(r.min_hourly_wage) if r.min_hourly_wage is not None else None,
            "is_active": r.is_active,
        }))
    return out


@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: int, db: Session = Depends(get_db)):
    r = db.execute(select(Role).where(Role.id == role_id)).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Not found")
    return RoleOut(**{
        "id": r.id,
        "business_id": r.business_id,
        "position": r.position,
        "payment_per_hour": float(r.payment_per_hour),
        "location": r.location,
        "latitude": r.latitude,
        "longitude": r.longitude,
        "when_need": r.when_need,
        "experience_required": r.experience_required,
        "shift_morning": r.shift_morning,
        "shift_evening": r.shift_evening,
        "shift_weekends": r.shift_weekends,
        "shift_full_time": r.shift_full_time,
        "shift_part_time": r.shift_part_time,
        "about_job": r.about_job,
        "min_hourly_wage": float(r.min_hourly_wage) if r.min_hourly_wage is not None else None,
        "is_active": r.is_active,
    })


@router.put("/{role_id}", response_model=RoleOut, dependencies=[Depends(AuthUser)])
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db), user=Depends(AuthUser)):
    r = db.execute(select(Role).where(Role.id == role_id)).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Not found")
    # Only manager of the business can update
    owned = db.execute(select(BusinessManager).where(BusinessManager.business_id == r.business_id, BusinessManager.manager_user_id == user.id)).first()
    if not owned:
        raise HTTPException(403, "Not your business")
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if updates:
        db.execute(update(Role).where(Role.id == role_id).values(**updates))
        db.commit()
    r = db.execute(select(Role).where(Role.id == role_id)).scalar_one()
    return RoleOut(**{
        "id": r.id,
        "business_id": r.business_id,
        "position": r.position,
        "payment_per_hour": float(r.payment_per_hour),
        "location": r.location,
        "when_need": r.when_need,
        "experience_required": r.experience_required,
        "shift_morning": r.shift_morning,
        "shift_evening": r.shift_evening,
        "shift_weekends": r.shift_weekends,
        "shift_full_time": r.shift_full_time,
        "shift_part_time": r.shift_part_time,
        "about_job": r.about_job,
        "min_hourly_wage": float(r.min_hourly_wage) if r.min_hourly_wage is not None else None,
        "is_active": r.is_active,
    })


@router.delete("/{role_id}", dependencies=[Depends(AuthUser)])
def delete_role(role_id: int, db: Session = Depends(get_db), user=Depends(AuthUser)):
    r = db.execute(select(Role).where(Role.id == role_id)).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Not found")
    owned = db.execute(select(BusinessManager).where(BusinessManager.business_id == r.business_id, BusinessManager.manager_user_id == user.id)).first()
    if not owned:
        raise HTTPException(403, "Not your business")
    db.execute(delete(Role).where(Role.id == role_id))
    db.commit()
    return {"ok": True}


@router.post("/{role_id}/like", dependencies=[Depends(AuthUser)])
def like_role(role_id: int, db: Session = Depends(get_db), user=Depends(AuthUser)):
    # user likes a role
    r = db.execute(select(Role).where(Role.id == role_id, Role.is_active == True)).scalar_one_or_none()
    if not r:
        raise HTTPException(404, "Role not found")
    # record like
    exists = db.execute(select(RoleLike).where(RoleLike.role_id == role_id, RoleLike.user_id == user.id)).scalar_one_or_none()
    if not exists:
        db.add(RoleLike(role_id=role_id, user_id=user.id))
        db.commit()
    # check if manager liked waiter (mutual)
    from app.models.user import ManagerLikeWaiter
    # Any manager of this business liked this waiter?
    manager_ids = [x[0] for x in db.execute(select(BusinessManager.manager_user_id).where(BusinessManager.business_id == r.business_id)).all()]
    liked = None
    if manager_ids:
        liked = db.execute(
            select(ManagerLikeWaiter).where(
                ManagerLikeWaiter.manager_user_id.in_(manager_ids),
                ManagerLikeWaiter.waiter_user_id == user.id
            )
        ).scalar_one_or_none()
    if liked:
        # create notification for mutual match
        from app.models.notification import Notification
        db.add(Notification(user_id=user.id, type="new_match", payload={"role_id": role_id}))
        db.commit()
        return {"liked": True, "mutual_match": True}
    return {"liked": True, "mutual_match": False}





