from fastapi import Depends, HTTPException, APIRouter
from typing import List
from sqlalchemy.orm import Session
from booking.db.models import Room
from booking.db.schema import RoomSchema, RoomCreateSchema
from booking.db.database import SessionLocal


room_router = APIRouter(prefix='/room', tags=['Room'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@room_router.post('/', response_model=RoomSchema)
async def room_create(room: RoomCreateSchema, db: Session = Depends(get_db)):
    db_room = Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@room_router.get('/', response_model=List[RoomSchema])
async def room_list(db: Session = Depends(get_db)):
    return db.query(Room).all()

@room_router.get('/{room_id}/', response_model=RoomSchema)
async def room_detail(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="room Not Found")
    return db_room

@room_router.put('/{room_id}/', response_model=dict)
async def room_update(room_id: int, room: RoomCreateSchema, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room Not Found")
    for key, value in room.dict().items():
        setattr(db_room, key, value)
    db.commit()
    db.refresh(db_room)
    return {"message": "Updated"}

@room_router.delete('/{room_id}/', response_model=dict)
async def room_delete(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if not db_room:
        raise HTTPException(status_code=404, detail="Room Not Found")
    db.delete(db_room)
    db.commit()
    return {"message": "Deleted"}
