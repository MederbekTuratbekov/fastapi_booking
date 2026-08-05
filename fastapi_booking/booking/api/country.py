from fastapi import Depends, HTTPException, APIRouter
from booking.db.models import Country
from booking.db.schema import CountrySchema, CountryCreateSchema
from booking.db.database import SessionLocal
from typing import List
from sqlalchemy.orm import Session


country_router = APIRouter(prefix='/country', tags=['Country'])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@country_router.post('/', response_model=CountrySchema)
async def country_create(country: CountryCreateSchema, db: Session = Depends(get_db)):
    db_country = Country(country_name=country.country_name)
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country

@country_router.get('/', response_model=List[CountrySchema])
def list_countries(db: Session = Depends(get_db)):
    return db.query(Country).all()

@country_router.get('/{country_id}/', response_model=CountrySchema)
def get_country(country_id: int, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.id == country_id).first()
    if country is None:
        raise HTTPException(status_code=404, detail='Country Not Found')
    return country

@country_router.put('/{country_id}/', response_model=dict)
def update_country(country_id: int, country: CountryCreateSchema, db: Session = Depends(get_db)):
    db_country = db.query(Country).filter(Country.id == country_id).first()
    if db_country is None:
        raise HTTPException(status_code=404, detail='Country Not Found')
    db_country.country_name = country.country_name
    db.commit()
    return {'message': 'Updated'}

@country_router.delete('/{country_id}/', response_model=dict)
def delete_country(country_id: int, db: Session = Depends(get_db)):
    db_country = db.query(Country).filter(Country.id == country_id).first()
    if db_country is None:
        raise HTTPException(status_code=404, detail='Country Not Found')
    db.delete(db_country)
    db.commit()
    return {'message': 'Deleted'}
