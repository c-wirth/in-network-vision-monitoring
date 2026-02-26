from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from user_access.database import engine, Base, get_db
from user_access import models, schemas
from user_access.auth import hash_password

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/api/status")
def get_status():
    return {"ok": True}


@app.post("/api/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # Check if user already exists
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = hash_password(user.password)

    # Create new user
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# uvicorn main:app --reload