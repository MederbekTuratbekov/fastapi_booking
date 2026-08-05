from booking.db.database import Base
from sqlalchemy import ForeignKey, String, Integer, DateTime, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum as PyEnum


class ROLE_CHOICES(str, PyEnum):
    client = "client"
    owner = "owner"

class STATUS_CHOICES(str, PyEnum):
    free = 'free'
    booked = 'booked'
    busy = 'busy'

class TYPE_CHOICE(str, PyEnum):
    lux = 'lux'
    single = 'single'
    double = 'double'
    family = 'family'

class STATUS_BOOK_CHOICES(str, PyEnum):
    cancellation = 'cancellation'
    confirmed = 'confirmed'


class UserProfile(Base):
    __tablename__ = 'userprofile'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(32))
    lastname: Mapped[str] = mapped_column(String(32))
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[ROLE_CHOICES] = mapped_column(Enum(ROLE_CHOICES), default=ROLE_CHOICES.client)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    country_user: Mapped[List['Country']] = relationship('Country', back_populates='user', cascade='all, delete-orphan')
    owner_hotel: Mapped[List['Hotel']] = relationship('Hotel', back_populates='owner')
    author_review: Mapped[List['Review']] = relationship('Review', back_populates='author', cascade='all, delete-orphan')
    user_booking: Mapped[List['Booking']] = relationship('Booking', back_populates='user', cascade='all, delete-orphan')
    user_token: Mapped[List['RefreshToken']] = relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'{self.first_name} {self.lastname} ({self.username})'


class RefreshToken(Base):
    __tablename__ = 'refresh_token'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    token: Mapped[str] = mapped_column(String, nullable=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    user: Mapped['UserProfile'] = relationship('UserProfile', back_populates='user_token')

    def __str__(self):
        return f'{self.token}'


class Country(Base):
    __tablename__ = 'country'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    country_name: Mapped[str] = mapped_column(String(64), unique=True)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('userprofile.id'), nullable=True)
    user: Mapped['UserProfile'] = relationship('UserProfile', back_populates='country_user')
    hotel_country: Mapped[List['Hotel']] = relationship('Hotel', back_populates='country')

    def __repr__(self):
        return f'{self.country_name}'


class Hotel(Base):
    __tablename__ = 'hotel'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    hotel_name: Mapped[str] = mapped_column(String(64), unique=True)
    hotel_address: Mapped[str] = mapped_column(String(64))
    hotel_description: Mapped[str] = mapped_column(Text)
    hotel_stars: Mapped[int] = mapped_column(Integer)

    owner_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    owner: Mapped['UserProfile'] = relationship('UserProfile', back_populates='owner_hotel')
    country_id: Mapped[int] = mapped_column(ForeignKey('country.id'))
    country: Mapped['Country'] = relationship('Country', back_populates='hotel_country')
    room_hotel: Mapped[List['Room']] = relationship('Room', back_populates='hotel', cascade='all, delete-orphan')
    booking_room: Mapped[List['Booking']] = relationship('Booking', back_populates='hotel', cascade='all, delete-orphan')
    review_hotel: Mapped[List['Review']] = relationship('Review', back_populates='hotel', cascade='all, delete-orphan')

    def __repr__(self):
        return f'{self.hotel_name}'


class Room(Base):
    __tablename__ = 'room'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    room_description: Mapped[str] = mapped_column(Text)
    room_status: Mapped[STATUS_CHOICES] = mapped_column(Enum(STATUS_CHOICES), default=STATUS_CHOICES.free)
    room_type: Mapped[TYPE_CHOICE] = mapped_column(Enum(TYPE_CHOICE), default=TYPE_CHOICE.single)

    hotel_id: Mapped[int] = mapped_column(ForeignKey('hotel.id'))
    hotel: Mapped['Hotel'] = relationship('Hotel', back_populates='room_hotel')
    booking_room: Mapped[List['Booking']] = relationship('Booking', back_populates='room', cascade='all, delete-orphan')

    def __str__(self):
        return f'{self.room_description} - {self.room_status}'


class Booking(Base):
    __tablename__ = 'booking'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    status_book: Mapped[STATUS_BOOK_CHOICES] = mapped_column(Enum(STATUS_BOOK_CHOICES))
    created_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    user: Mapped['UserProfile'] = relationship('UserProfile', back_populates='user_booking')
    hotel_id: Mapped[int] = mapped_column(ForeignKey('hotel.id'))
    hotel: Mapped['Hotel'] = relationship('Hotel', back_populates='booking_room')
    room_id: Mapped[int] = mapped_column(ForeignKey('room.id'))
    room: Mapped['Room'] = relationship('Room', back_populates='booking_room')

    def __str__(self):
        return f'{self.created_date} - {self.status_book}'


class Review(Base):
    __tablename__ = 'review'
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(Text)
    created_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    author_id: Mapped[int] = mapped_column(ForeignKey('userprofile.id'))
    author: Mapped['UserProfile'] = relationship('UserProfile', back_populates='author_review')
    hotel_id: Mapped[int] = mapped_column(ForeignKey('hotel.id'))
    hotel: Mapped['Hotel'] = relationship('Hotel', back_populates='review_hotel')

    def __str__(self):
        return f'{self.comment} - {self.rating}'
