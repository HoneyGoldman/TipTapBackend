from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from typing import List
from app.core.deps import get_db, AuthUser
from app.models.business import Business
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessOut


router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post("/", response_model=BusinessOut, dependencies=[Depends(AuthUser)])
def create_business(payload: BusinessCreate, db: Session = Depends(get_db), user=Depends(AuthUser)):
    b = Business(
        manager_user_id=user.id,
        name=payload.name,
        location=payload.location,
        business_type=payload.business_type,
        menu_url=payload.menu_url,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return BusinessOut(
        id=b.id,
        manager_user_id=b.manager_user_id,
        name=b.name,
        location=b.location,
        business_type=b.business_type,
        menu_url=b.menu_url,
    )


@router.get("/", response_model=List[BusinessOut], dependencies=[Depends(AuthUser)])
def list_businesses(db: Session = Depends(get_db), user=Depends(AuthUser)):
    rows = db.execute(select(Business).where(Business.manager_user_id == user.id)).scalars().all()
    return [
        BusinessOut(
            id=r.id,
            manager_user_id=r.manager_user_id,
            name=r.name,
            location=r.location,
            business_type=r.business_type,
            menu_url=r.menu_url,
        ) for r in rows
    ]


@router.get("/{business_id}", response_model=BusinessOut, dependencies=[Depends(AuthUser)])
def get_business(business_id: int, db: Session = Depends(get_db), user=Depends(AuthUser)):
    b = db.execute(select(Business).where(Business.id == business_id, Business.manager_user_id == user.id)).scalar_one_or_none()
    if not b:
        raise HTTPException(404, "Not found")
    return BusinessOut(
        id=b.id, manager_user_id=b.manager_user_id, name=b.name, location=b.location,
        business_type=b.business_type, menu_url=b.menu_url
    )


@router.put("/{business_id}", response_model=BusinessOut, dependencies=[Depends(AuthUser)])
def update_business(business_id: int, payload: BusinessUpdate, db: Session = Depends(get_db), user=Depends(AuthUser)):
    b = db.execute(select(Business).where(Business.id == business_id, Business.manager_user_id == user.id)).scalar_one_or_none()
    if not b:
        raise HTTPException(404, "Not found")
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if updates:
        db.execute(update(Business).where(Business.id == business_id).values(**updates))
        db.commit()
    b = db.execute(select(Business).where(Business.id == business_id)).scalar_one()
    return BusinessOut(
        id=b.id, manager_user_id=b.manager_user_id, name=b.name, location=b.location,
        business_type=b.business_type, menu_url=b.menu_url
    )


@router.delete("/{business_id}", dependencies=[Depends(AuthUser)])
def delete_business(business_id: int, db: Session = Depends(get_db), user=Depends(AuthUser)):
    b = db.execute(select(Business).where(Business.id == business_id, Business.manager_user_id == user.id)).scalar_one_or_none()
    if not b:
        raise HTTPException(404, "Not found")
    db.execute(delete(Business).where(Business.id == business_id))
    db.commit()
    return {"ok": True}


