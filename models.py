from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field

from database import Base


# ============================================================================
# 1. SQLALCHEMY ORM MODELS (Database Schema)
# ============================================================================

class UserDB(Base):
    """
    SQLAlchemy model representing the 'users' table.
    Stores patient information, contact details, and authentication credentials.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    role = Column(String(30), default="user", nullable=False)  # 'user', 'patient'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    appointments = relationship(
        "AppointmentDB",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class DoctorDB(Base):
    """
    SQLAlchemy model representing the 'doctors' table.
    Stores doctor profile, specialization, availability hours, and credentials.
    """
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    specialization = Column(String(100), nullable=False, index=True)
    phone = Column(String(30), nullable=True)
    availability = Column(String(120), default="Mon - Fri: 09:00 AM - 05:00 PM")
    experience = Column(Integer, default=5)
    qualification = Column(String(120), default="MBBS, MD")
    consultation_fee = Column(Float, default=500.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    appointments = relationship(
        "AppointmentDB",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )


class AppointmentDB(Base):
    """
    SQLAlchemy model representing the 'appointments' table.
    Links patient and doctor for an appointment booking.
    Avoids conflicts via unique constraint on (doctor_id, date, time).
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    date = Column(String(30), nullable=False)  # Format: YYYY-MM-DD
    time = Column(String(30), nullable=False)  # Format: "09:00 AM" or "14:30"
    status = Column(String(30), default="Pending", nullable=False)  # Pending, Confirmed, Rejected, Cancelled, Completed
    symptoms = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("UserDB", back_populates="appointments")
    doctor = relationship("DoctorDB", back_populates="appointments")

    # Constraint to prevent double-booking the same doctor at the same slot
    __table_args__ = (
        UniqueConstraint("doctor_id", "date", "time", name="uq_doctor_date_time"),
    )


class AdminDB(Base):
    """
    SQLAlchemy model representing the 'admin' table.
    Stores administrative credentials for hospital administrators.
    """
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(160), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    full_name = Column(String(120), default="Administrator")
    created_at = Column(DateTime, default=datetime.utcnow)


class HealthArticleDB(Base):
    """
    SQLAlchemy model representing the 'health_articles' table.
    Stores first aid guides, health tips, and emergency procedures.
    """
    __tablename__ = "health_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="First Aid", index=True, nullable=False)
    content = Column(Text, nullable=False)
    emergency_contact = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# 2. PYDANTIC SCHEMAS (Data Validation & Serialization)
# ============================================================================

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    name: str = Field(..., example="John Doe")
    email: EmailStr = Field(..., example="patient@lifeline.com")
    phone: Optional[str] = Field(None, example="+91 98765 43210")

class UserCreate(UserBase):
    password: str = Field(..., min_length=4, example="password123")

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: int
    role: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- DOCTOR SCHEMAS ---
class DoctorBase(BaseModel):
    name: str = Field(..., example="Dr. Rajesh Sharma")
    email: EmailStr = Field(..., example="doctor.sharma@lifeline.com")
    specialization: str = Field(..., example="Cardiologist")
    phone: Optional[str] = Field(None, example="+91 98765 00001")
    availability: Optional[str] = Field("Mon - Fri: 09:00 AM - 01:00 PM")
    experience: Optional[int] = Field(5, example=12)
    qualification: Optional[str] = Field("MBBS, MD", example="MBBS, MD (Cardiology)")
    consultation_fee: Optional[float] = Field(500.0, example=600.0)

class DoctorCreate(DoctorBase):
    password: str = Field("password123", min_length=4)

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None
    availability: Optional[str] = None
    experience: Optional[int] = None
    qualification: Optional[str] = None
    consultation_fee: Optional[float] = None

class DoctorResponse(DoctorBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- APPOINTMENT SCHEMAS ---
class AppointmentCreate(BaseModel):
    doctor_id: int = Field(..., example=1)
    date: str = Field(..., example="2026-11-10")
    time: str = Field(..., example="10:00 AM")
    symptoms: Optional[str] = Field(None, example="Mild chest discomfort and fatigue")

class AppointmentStatusUpdate(BaseModel):
    status: str = Field(..., example="Confirmed")  # 'Confirmed', 'Rejected', 'Cancelled', 'Completed'
    notes: Optional[str] = Field(None, example="Doctor accepted. Please bring prior ECG report.")

class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    doctor_id: int
    date: str
    time: str
    status: str
    symptoms: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    user: Optional[UserResponse] = None
    doctor: Optional[DoctorResponse] = None

    class Config:
        from_attributes = True


# --- ADMIN SCHEMAS ---
class AdminBase(BaseModel):
    username: str = Field(..., example="admin")
    email: EmailStr = Field(..., example="admin@lifeline.com")
    full_name: Optional[str] = Field("Hospital Administrator")

class AdminCreate(AdminBase):
    password: str = Field(..., min_length=4)

class AdminResponse(AdminBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- HEALTH ARTICLE SCHEMAS ---
class HealthArticleBase(BaseModel):
    title: str = Field(..., example="CPR Guidelines")
    category: str = Field("First Aid", example="Cardio Health")
    content: str = Field(..., example="Step 1: Check responsiveness. Step 2: Call emergency 108...")
    emergency_contact: Optional[str] = Field(None, example="108")

class HealthArticleCreate(HealthArticleBase):
    pass

class HealthArticleResponse(HealthArticleBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- AUTH & TESTING SCHEMAS ---
class LoginRequest(BaseModel):
    email: str = Field(..., example="patient@lifeline.com")  # Accepts email or admin username
    password: str = Field(..., example="password123")
    role: Optional[str] = Field(None, example="user")  # 'user', 'doctor', 'admin', or autodetect

class LoginResponse(BaseModel):
    success: bool
    role: str  # 'user', 'doctor', 'admin'
    user_id: int
    name: str
    email: str
    token: str
    message: str

class TestAccountInfo(BaseModel):
    role: str
    label: str
    email: str
    password: str
    details: str

class BMICalculatorRequest(BaseModel):
    weight_kg: float = Field(..., gt=0, example=70.0)
    height_cm: float = Field(..., gt=0, example=175.0)

class BMICalculatorResponse(BaseModel):
    bmi: float
    category: str
    risk_level: str
    recommendation: str
