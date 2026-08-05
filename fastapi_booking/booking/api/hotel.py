from fastapi import Depends, HTTPException, APIRouter
from booking.db.models import Hotel
from booking.db.schema import HotelSchema, HotelCreateSchema
from booking.db.database import SessionLocal
from typing import List
from sqlalchemy.orm import Session

hotel_router = APIRouter(prefix='/hotel', tags=['Hotel'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@hotel_router.post('/', response_model=HotelSchema)
async def hotel_create(hotel: HotelCreateSchema, db: Session = Depends(get_db)):
    db_hotel = Hotel(**hotel.dict())
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel


@hotel_router.get('/', response_model=List[HotelSchema])
async def hotel_list(db: Session = Depends(get_db)):
    return db.query(Hotel).all()

@hotel_router.get('/{hotel_id}/', response_model=HotelSchema)
async def hotel_detail(hotel_id: int, db: Session = Depends(get_db)):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel Not Found")
    return db_hotel

@hotel_router.put('/{hotel_id}/', response_model=dict)
async def hotel_update(hotel_id: int, hotel: HotelCreateSchema, db: Session = Depends(get_db)):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel Not Found")
    for key, value in hotel.dict().items():
        setattr(db_hotel, key, value)
    db.commit()
    db.refresh(db_hotel)
    return {"message": "Updated"}

@hotel_router.delete('/{hotel_id}/', response_model=dict)
async def hotel_delete(hotel_id: int, db: Session = Depends(get_db)):
    db_hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not db_hotel:
        raise HTTPException(status_code=404, detail="Hotel Not Found")
    db.delete(db_hotel)
    db.commit()
    return {"message": "Deleted"}
