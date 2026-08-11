# 🏨 Hotel Booking Platform API

> Production-ready REST API for hotel reservation management —
> JWT auth, OAuth2, room availability tracking, and admin panel.

[![Python](https://img.shields.io/badge/Python-3.11-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-async-teal)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)]()
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green)]()

---

## Problem

Hotels lose direct bookings to third-party aggregators because they
lack their own API infrastructure. This API gives full control over
reservations — without platform fees.

---

## What's Built

- **JWT auth** — register / login / logout / token refresh;
  refresh tokens stored in DB, deleted on logout
- **OAuth2** — GitHub and Google via authlib
- **Hotels** — full CRUD; star rating, address, country FK
- **Rooms** — type (lux / single / double / family) +
  availability status (free / booked / busy)
- **Bookings** — create / update / cancel with
  confirmed / cancellation status
- **Reviews** — star rating + comment per hotel
- **Countries** — geographic directory, full CRUD
- **Admin panel** — sqladmin web UI for all 6 entities

---

## Tech Stack

| Category   | Technology                              |
|------------|-----------------------------------------|
| Language   | Python 3.11                             |
| Framework  | FastAPI, Uvicorn (ASGI)                 |
| ORM        | SQLAlchemy 2.x (Mapped / mapped_column) |
| Validation | Pydantic v2                             |
| Auth       | python-jose (JWT), passlib (bcrypt)     |
| OAuth2     | authlib (GitHub, Google)                |
| Database   | PostgreSQL                              |
| Admin      | sqladmin                                |
| Config     | python-dotenv                           |

---

## Architecture
```
fastapi_booking/
├── .gitignore
├── readme.md
└── fastapi_booking/
    ├── alembic.ini
    ├── booking/
    │   ├── .env.py
    │   ├── admin/
    │   │   ├── __init__.py
    │   │   ├── setup.py
    │   │   └── views.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── auth.py
    │   │   ├── booking.py
    │   │   ├── country.py
    │   │   ├── hotel.py
    │   │   ├── review.py
    │   │   ├── room.py
    │   │   └── social_auth.py
    │   ├── db/
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   ├── database.py
    │   │   ├── models.py
    │   │   └── schema.py
    │   ├── main.py
    │   └── requirements.txt
    └── migrations/
        ├── README
        ├── env.py
        ├── script.py.mako
        └── versions/
            └── ec7136e0cdb6_.py
```
---
