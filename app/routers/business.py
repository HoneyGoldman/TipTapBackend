from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, update, delete
from typing import List
import cloudinary
import cloudinary.uploader
from app.core.deps import get_db, AuthUser
from app.models.business import Business, BusinessManager
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessOut, AddManagerRequest
from app.core.config import settings


router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post("/", response_model=BusinessOut, dependencies=[Depends(AuthUser)])
def create_business(payload: BusinessCreate, db: Session = Depends(get_db), user=Depends(AuthUser)):
    b = Business(
        name=payload.name,
        location=payload.location,
        business_type=payload.business_type,
        menu_url=payload.menu_url,
        images=payload.images or [],
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    # assign managers: current user + any provided
    manager_ids = set([user.id])
    if payload.manager_user_ids:
        manager_ids.update(payload.manager_user_ids)
    for mid in manager_ids:
        db.add(BusinessManager(business_id=b.id, manager_user_id=mid))
    db.commit()
    # load manager ids
    mids = [r[0] for r in db.execute(select(BusinessManager.manager_user_id).where(BusinessManager.business_id == b.id)).all()]
    return BusinessOut(
        id=b.id,
        manager_user_ids=mids,
        name=b.name,
        location=b.location,
        business_type=b.business_type,
        menu_url=b.menu_url,
        images=b.images,
    )


@router.get("/", response_model=List[BusinessOut], dependencies=[Depends(AuthUser)])
def list_businesses(db: Session = Depends(get_db), user=Depends(AuthUser)):
    biz_ids = [r[0] for r in db.execute(select(BusinessManager.business_id).where(BusinessManager.manager_user_id == user.id)).all()]
    if not biz_ids:
        return []
    rows = db.execute(select(Business).where(Business.id.in_(biz_ids))).scalars().all()
    result: List[BusinessOut] = []
    for r in rows:
        mids = [x[0] for x in db.execute(select(BusinessManager.manager_user_id).where(BusinessManager.business_id == r.id)).all()]
        result.append(BusinessOut(
            id=r.id,
            manager_user_ids=mids,
            name=r.name,
            location=r.location,
            business_type=r.business_type,
            menu_url=r.menu_url,
            images=r.images,
        ))
    return result


@router.get("/{business_id}", response_model=BusinessOut, dependencies=[Depends(AuthUser)])
def get_business(business_id: int, db: Session = Depends(get_db), user=Depends(AuthUser)):
    owned = db.execute(select(BusinessManager).where(BusinessManager.business_id == business_id, BusinessManager.manager_user_id == user.id)).first()
    if not owned:
        raise HTTPException(404, "Not found")
    b = db.execute(select(Business).where(Business.id == business_id)).scalar_one_or_none()
    if not b:
        raise HTTPException(404, "Not found")
    mids = [x[0] for x in db.execute(select(BusinessManager.manager_user_id).where(BusinessManager.business_id == b.id)).all()]
    return BusinessOut(
        id=b.id, manager_user_ids=mids, name=b.name, location=b.location,
        business_type=b.business_type, menu_url=b.menu_url, images=b.images
    )


@router.put("/{business_id}", response_model=BusinessOut, dependencies=[Depends(AuthUser)])
def update_business(business_id: int, payload: BusinessUpdate, db: Session = Depends(get_db), user=Depends(AuthUser)):
    owned = db.execute(select(BusinessManager).where(BusinessManager.business_id == business_id, BusinessManager.manager_user_id == user.id)).first()
    if not owned:
        raise HTTPException(404, "Not found")
    b = db.execute(select(Business).where(Business.id == business_id)).scalar_one_or_none()
    if not b:
        raise HTTPException(404, "Not found")
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if updates:
        db.execute(update(Business).where(Business.id == business_id).values(**updates))
        db.commit()
    b = db.execute(select(Business).where(Business.id == business_id)).scalar_one()
    mids = [x[0] for x in db.execute(select(BusinessManager.manager_user_id).where(BusinessManager.business_id == b.id)).all()]
    return BusinessOut(
        id=b.id, manager_user_ids=mids, name=b.name, location=b.location,
        business_type=b.business_type, menu_url=b.menu_url, images=b.images
    )


@router.delete("/{business_id}", dependencies=[Depends(AuthUser)])
def delete_business(business_id: int, db: Session = Depends(get_db), user=Depends(AuthUser)):
    owned = db.execute(select(BusinessManager).where(BusinessManager.business_id == business_id, BusinessManager.manager_user_id == user.id)).first()
    if not owned:
        raise HTTPException(404, "Not found")
    db.execute(delete(Business).where(Business.id == business_id))
    db.commit()
    return {"ok": True}


@router.post("/{business_id}/images", response_model=BusinessOut, dependencies=[Depends(AuthUser)])
def upload_business_images(business_id: int, files: List[UploadFile] = File(...), db: Session = Depends(get_db), user=Depends(AuthUser)):
    # verify ownership
    owned = db.execute(select(BusinessManager).where(BusinessManager.business_id == business_id, BusinessManager.manager_user_id == user.id)).first()
    if not owned:
        raise HTTPException(404, "Not found")
    b = db.execute(select(Business).where(Business.id == business_id)).scalar_one_or_none()
    if not b:
        raise HTTPException(404, "Not found")
    # configure cloudinary
    if settings.cloudinary:
        cloudinary.config(
            cloud_name=settings.cloudinary.cloud_name,
            api_key=settings.cloudinary.api_key,
            api_secret=settings.cloudinary.api_secret,
            secure=True,
        )
    else:
        raise HTTPException(500, "Cloudinary not configured")
    urls: List[str] = []
    for f in files:
        res = cloudinary.uploader.upload(f.file, folder=f"businesses/{business_id}")
        url = res.get("secure_url") or res.get("url")
        if url:
            urls.append(url)
    current = b.images or []
    new_images = current + urls
    db.execute(update(Business).where(Business.id == business_id).values(images=new_images))
    db.commit()
    b = db.execute(select(Business).where(Business.id == business_id)).scalar_one()
    mids = [x[0] for x in db.execute(select(BusinessManager.manager_user_id).where(BusinessManager.business_id == b.id)).all()]
    return BusinessOut(
        id=b.id, manager_user_ids=mids, name=b.name, location=b.location,
        business_type=b.business_type, menu_url=b.menu_url, images=b.images
    )


@router.post("/{business_id}/managers", response_model=BusinessOut, dependencies=[Depends(AuthUser)])
def add_business_manager(business_id: int, payload: AddManagerRequest, db: Session = Depends(get_db), user=Depends(AuthUser)):
    # verify ownership
    owned = db.execute(select(BusinessManager).where(BusinessManager.business_id == business_id, BusinessManager.manager_user_id == user.id)).first()
    if not owned:
        raise HTTPException(404, "Not found")
    b = db.execute(select(Business).where(Business.id == business_id)).scalar_one_or_none()
    if not b:
        raise HTTPException(404, "Not found")
    # find user by email (phone not yet supported)
    if payload.email:
        from app.models.user import UserAccount
        candidate = db.execute(select(UserAccount).where(UserAccount.email == payload.email)).scalar_one_or_none()
        if not candidate:
            raise HTTPException(404, "User with this email not found")
        if candidate.user_type != "business_manager":
            raise HTTPException(400, "User is not a business manager")
        exists = db.execute(select(BusinessManager).where(BusinessManager.business_id == business_id, BusinessManager.manager_user_id == candidate.id)).first()
        if not exists:
            db.add(BusinessManager(business_id=business_id, manager_user_id=candidate.id))
            db.commit()
    elif payload.phone:
        raise HTTPException(400, "Adding by phone is not supported yet")
    else:
        raise HTTPException(400, "Provide email or phone")
    # return updated business
    b = db.execute(select(Business).where(Business.id == business_id)).scalar_one()
    mids = [x[0] for x in db.execute(select(BusinessManager.manager_user_id).where(BusinessManager.business_id == b.id)).all()]
    return BusinessOut(
        id=b.id, manager_user_ids=mids, name=b.name, location=b.location,
        business_type=b.business_type, menu_url=b.menu_url, images=b.images
    )


