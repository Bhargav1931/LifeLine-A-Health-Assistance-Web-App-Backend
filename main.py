import os
import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import engine, Base, get_db
import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DATABASE INITIALIZATION & SEED DATA (Testing users for all roles)
# ============================================================================

def seed_initial_data(db: Session):
    """
    Seeds initial test data into the PostgreSQL database for testing & viva presentation.
    Includes predefined test accounts for Patient, Doctor, and Admin.
    """
    try:
        # 1. Seed Admin
        admin_count = db.query(models.AdminDB).count()
        if admin_count == 0:
            logger.info("Seeding Admin account...")
            admin = models.AdminDB(
                username="admin",
                email="admin@lifeline.com",
                password="admin123",
                full_name="Super Administrator"
            )
            db.add(admin)

        # 2. Seed Test Users (Patients)
        user_count = db.query(models.UserDB).count()
        if user_count == 0:
            logger.info("Seeding Patient accounts...")
            patients = [
                models.UserDB(
                    name="John Doe",
                    email="patient@lifeline.com",
                    password="password123",
                    phone="+91 98765 43210",
                    role="user"
                ),
                models.UserDB(
                    name="Sarah Jenkins",
                    email="sarah@lifeline.com",
                    password="password123",
                    phone="+91 98765 43211",
                    role="user"
                ),
                models.UserDB(
                    name="Rahul Sharma",
                    email="rahul@lifeline.com",
                    password="password123",
                    phone="+91 98765 43212",
                    role="user"
                )
            ]
            db.add_all(patients)

        # 3. Seed Doctors
        doc_count = db.query(models.DoctorDB).count()
        if doc_count == 0:
            logger.info("Seeding Doctor accounts across multiple specializations...")
            doctors = [
                models.DoctorDB(
                    name="Dr. Rajesh Sharma",
                    email="doctor.sharma@lifeline.com",
                    password="password123",
                    specialization="Cardiologist",
                    phone="+91 98765 00001",
                    availability="Mon - Fri: 09:00 AM - 01:00 PM",
                    experience=15,
                    qualification="MBBS, MD, DM (Cardiology)",
                    consultation_fee=700.0
                ),
                models.DoctorDB(
                    name="Dr. Priya Patel",
                    email="doctor.patel@lifeline.com",
                    password="password123",
                    specialization="Pediatrician",
                    phone="+91 98765 00002",
                    availability="Mon - Sat: 10:00 AM - 04:00 PM",
                    experience=10,
                    qualification="MBBS, DCH, MD (Pediatrics)",
                    consultation_fee=500.0
                ),
                models.DoctorDB(
                    name="Dr. Amit Verma",
                    email="doctor.verma@lifeline.com",
                    password="password123",
                    specialization="Orthopedic",
                    phone="+91 98765 00003",
                    availability="Tue - Sat: 02:00 PM - 07:00 PM",
                    experience=12,
                    qualification="MBBS, MS (Orthopedics)",
                    consultation_fee=650.0
                ),
                models.DoctorDB(
                    name="Dr. Sneha Reddy",
                    email="doctor.reddy@lifeline.com",
                    password="password123",
                    specialization="Dermatologist",
                    phone="+91 98765 00004",
                    availability="Mon - Fri: 11:00 AM - 05:00 PM",
                    experience=8,
                    qualification="MBBS, MD (Dermatology)",
                    consultation_fee=600.0
                ),
                models.DoctorDB(
                    name="Dr. Vikram Rao",
                    email="doctor.rao@lifeline.com",
                    password="password123",
                    specialization="General Physician",
                    phone="+91 98765 00005",
                    availability="Mon - Sat: 09:00 AM - 06:00 PM",
                    experience=14,
                    qualification="MBBS, MD (Internal Medicine)",
                    consultation_fee=400.0
                ),
                models.DoctorDB(
                    name="Dr. Ananya Sen",
                    email="doctor.sen@lifeline.com",
                    password="password123",
                    specialization="Neurologist",
                    phone="+91 98765 00006",
                    availability="Mon - Thu: 01:00 PM - 06:00 PM",
                    experience=16,
                    qualification="MBBS, DM (Neurology)",
                    consultation_fee=850.0
                )
            ]
            db.add_all(doctors)

        # 4. Seed Health Articles & First-Aid Guides
        article_count = db.query(models.HealthArticleDB).count()
        if article_count == 0:
            logger.info("Seeding Health Articles & First-Aid guides...")
            articles = [
                models.HealthArticleDB(
                    title="CPR (Cardiopulmonary Resuscitation) Life-Saving Steps",
                    category="First Aid",
                    emergency_contact="108",
                    content=(
                        "1. Call Emergency (108) immediately.\n"
                        "2. Place patient on a firm, flat surface.\n"
                        "3. Position hands in the center of the chest.\n"
                        "4. Push hard and fast at a rate of 100-120 compressions per minute.\n"
                        "5. Allow chest to fully recoil between compressions.\n"
                        "6. Continue until emergency medical service arrives or patient starts breathing."
                    )
                ),
                models.HealthArticleDB(
                    title="Emergency First Aid for Burns and Scalds",
                    category="First Aid",
                    emergency_contact="108",
                    content=(
                        "1. Stop the burning process immediately by removing the heat source.\n"
                        "2. Cool the burn under cool, running tap water for at least 15-20 minutes. Do NOT use ice or butter.\n"
                        "3. Remove restrictive items like jewelry, rings, and clothing around the burn before swelling begins.\n"
                        "4. Cover loosely with a sterile, non-adherent dressing or clean plastic cling wrap.\n"
                        "5. Seek immediate emergency care for deep, extensive burns or burns on face/hands."
                    )
                ),
                models.HealthArticleDB(
                    title="Recognizing Stroke Symptoms: The F.A.S.T. Warning Method",
                    category="Emergency",
                    emergency_contact="112",
                    content=(
                        "F - FACE: Ask the person to smile. Does one side of the face droop?\n"
                        "A - ARMS: Ask the person to raise both arms. Does one arm drift downward?\n"
                        "S - SPEECH: Ask the person to repeat a simple phrase. Is speech slurred or strange?\n"
                        "T - TIME: If you observe any of these signs, call Emergency (108/112) immediately! Every second counts in stroke management."
                    )
                ),
                models.HealthArticleDB(
                    title="Essential Steps for Choking Relief (Heimlich Maneuver)",
                    category="First Aid",
                    emergency_contact="108",
                    content=(
                        "1. Stand behind the person and wrap your arms around their waist.\n"
                        "2. Make a fist with one hand and place the thumb side just above the navel.\n"
                        "3. Grasp your fist with your other hand.\n"
                        "4. Perform quick, inward and upward thrusts until the blockage is dislodged.\n"
                        "5. If the person loses consciousness, lower them to the ground and initiate CPR."
                    )
                ),
                models.HealthArticleDB(
                    title="Preventive Heart Health: 5 Daily Habits for a Healthy Cardiovascular System",
                    category="General Health",
                    emergency_contact="108",
                    content=(
                        "1. Maintain 30 minutes of moderate aerobic exercise (brisk walking, swimming) daily.\n"
                        "2. Follow a heart-friendly diet: minimize sodium, trans fats, and added sugars; enrich meals with greens, berries, and omega-3s.\n"
                        "3. Monitor blood pressure and blood glucose regularly.\n"
                        "4. Avoid tobacco usage and manage chronic stress with mindfulness.\n"
                        "5. Schedule annual health checkups with a certified cardiologist."
                    )
                ),
                models.HealthArticleDB(
                    title="Understanding Blood Pressure Readings & Hypertension Stages",
                    category="General Health",
                    emergency_contact=None,
                    content=(
                        "- Normal: Systolic < 120 mm Hg and Diastolic < 80 mm Hg.\n"
                        "- Elevated: Systolic 120-129 and Diastolic < 80.\n"
                        "- Stage 1 Hypertension: Systolic 130-139 or Diastolic 80-89.\n"
                        "- Stage 2 Hypertension: Systolic 140 or higher, or Diastolic 90 or higher.\n"
                        "- Hypertensive Crisis (Seek Emergency Immediately): Systolic > 180 and/or Diastolic > 120."
                    )
                )
            ]
            db.add_all(articles)

        db.commit()

        # 5. Seed Initial Appointments for demonstration
        appt_count = db.query(models.AppointmentDB).count()
        if appt_count == 0:
            logger.info("Seeding initial appointments for testing demo...")
            first_user = db.query(models.UserDB).filter_by(email="patient@lifeline.com").first()
            dr_sharma = db.query(models.DoctorDB).filter_by(email="doctor.sharma@lifeline.com").first()
            dr_patel = db.query(models.DoctorDB).filter_by(email="doctor.patel@lifeline.com").first()

            if first_user and dr_sharma:
                appt1 = models.AppointmentDB(
                    user_id=first_user.id,
                    doctor_id=dr_sharma.id,
                    date="2026-11-12",
                    time="10:00 AM",
                    status="Confirmed",
                    symptoms="Regular blood pressure checkup and routine consultation",
                    notes="Confirmed. Please bring recent lipid profile results."
                )
                db.add(appt1)

            if first_user and dr_patel:
                appt2 = models.AppointmentDB(
                    user_id=first_user.id,
                    doctor_id=dr_patel.id,
                    date="2026-11-14",
                    time="11:30 AM",
                    status="Pending",
                    symptoms="Child routine vaccination inquiry and dietary advice",
                    notes=None
                )
                db.add(appt2)

            db.commit()

        logger.info("Database seeding successfully completed!")

    except Exception as e:
        db.rollback()
        logger.error(f"Error during database seed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize PostgreSQL database tables
    logger.info("Creating PostgreSQL database tables if not existing...")
    Base.metadata.create_all(bind=engine)
    
    # Run Seeder with a clean session
    db = next(get_db())
    try:
        seed_initial_data(db)
    finally:
        db.close()
    
    yield
    logger.info("Shutting down LifeLine FastAPI service...")

# Ensure tables are created on module import as well
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.warning(f"Initial table creation notice: {e}")



# Initialize FastAPI App
app = FastAPI(
    title="Life Line – Health Assistance API",
    description="Backend API for Life Line Health Assistance Web Application connecting patients, doctors, and administrators with appointment booking, health tools, and emergency resources.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_env == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ROOT & SYSTEM HEALTH
# ============================================================================

@app.get("/")
def root():
    return {
        "project": "Life Line – A Health Assistance Web App",
        "status": "Online",
        "database": "PostgreSQL",
        "documentation": "/docs"
    }

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    try:
        user_count = db.query(models.UserDB).count()
        doctor_count = db.query(models.DoctorDB).count()
        appointment_count = db.query(models.AppointmentDB).count()
        return {
            "status": "healthy",
            "database": "PostgreSQL connected",
            "stats": {
                "users": user_count,
                "doctors": doctor_count,
                "appointments": appointment_count
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database check failed: {str(e)}")


# ============================================================================
# AUTHENTICATION & TESTING USERS (Predefined credentials for all roles)
# ============================================================================

@app.get("/api/auth/test-users", response_model=List[models.TestAccountInfo])
def get_test_users():
    """
    Returns quick-access testing accounts for Viva & testing presentations.
    Provides instant credentials for Patient, Doctor, and Admin roles.
    """
    return [
        models.TestAccountInfo(
            role="user",
            label="Patient Test Account",
            email="patient@lifeline.com",
            password="password123",
            details="John Doe - Can book, view, and cancel appointments"
        ),
        models.TestAccountInfo(
            role="doctor",
            label="Doctor Test Account (Cardiology)",
            email="doctor.sharma@lifeline.com",
            password="password123",
            details="Dr. Rajesh Sharma - Can accept/reject appointments and view patient history"
        ),
        models.TestAccountInfo(
            role="doctor",
            label="Doctor Test Account (Pediatrics)",
            email="doctor.patel@lifeline.com",
            password="password123",
            details="Dr. Priya Patel - Pediatrician"
        ),
        models.TestAccountInfo(
            role="admin",
            label="Admin Test Account",
            email="admin@lifeline.com",
            password="admin123",
            details="Hospital Admin - Manage doctors, users, articles, and monitor all bookings"
        )
    ]


@app.post("/api/auth/login", response_model=models.LoginResponse)
def login(creds: models.LoginRequest, db: Session = Depends(get_db)):
    """
    Unified Login endpoint: supports Patient, Doctor, or Admin authentication.
    """
    email_or_username = creds.email.strip().lower()
    password = creds.password

    # 1. Check Admin
    admin = db.query(models.AdminDB).filter(
        (models.AdminDB.email.ilike(email_or_username)) | 
        (models.AdminDB.username.ilike(email_or_username))
    ).first()

    if admin and admin.password == password:
        return models.LoginResponse(
            success=True,
            role="admin",
            user_id=admin.id,
            name=admin.full_name,
            email=admin.email,
            token=f"admin-token-{admin.id}",
            message="Admin authentication successful"
        )

    # 2. Check Doctor
    doctor = db.query(models.DoctorDB).filter(models.DoctorDB.email.ilike(email_or_username)).first()
    if doctor and doctor.password == password:
        return models.LoginResponse(
            success=True,
            role="doctor",
            user_id=doctor.id,
            name=doctor.name,
            email=doctor.email,
            token=f"doctor-token-{doctor.id}",
            message="Doctor authentication successful"
        )

    # 3. Check Patient/User
    user = db.query(models.UserDB).filter(models.UserDB.email.ilike(email_or_username)).first()
    if user and user.password == password:
        return models.LoginResponse(
            success=True,
            role="user",
            user_id=user.id,
            name=user.name,
            email=user.email,
            token=f"user-token-{user.id}",
            message="User authentication successful"
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email/username or password. Use test credentials provided."
    )


@app.post("/api/auth/register", response_model=models.UserResponse)
def register_user(user_in: models.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new Patient in the User Module.
    """
    existing = db.query(models.UserDB).filter(models.UserDB.email.ilike(user_in.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email address already exists.")

    new_user = models.UserDB(
        name=user_in.name,
        email=user_in.email.lower(),
        password=user_in.password,
        phone=user_in.phone,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ============================================================================
# MODULE 1: USER MODULE (Patients)
# ============================================================================

@app.get("/api/users", response_model=List[models.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Admin module: List all registered patients."""
    return db.query(models.UserDB).order_by(models.UserDB.id.desc()).all()

@app.get("/api/users/{user_id}", response_model=models.UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.UserDB).filter(models.UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{user_id}", response_model=models.UserResponse)
def update_user_profile(user_id: int, user_update: models.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.UserDB).filter(models.UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_update.name:
        user.name = user_update.name
    if user_update.phone:
        user.phone = user_update.phone
    if user_update.email:
        user.email = user_update.email.lower()

    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.UserDB).filter(models.UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}


# ============================================================================
# MODULE 2: DOCTOR MODULE
# ============================================================================

@app.get("/api/doctors", response_model=List[models.DoctorResponse])
def get_doctors(
    specialization: Optional[str] = Query(None, description="Filter doctors by specialization"),
    db: Session = Depends(get_db)
):
    """
    Search and retrieve doctors, optionally filtered by medical specialization.
    """
    query = db.query(models.DoctorDB)
    if specialization and specialization != "All":
        query = query.filter(models.DoctorDB.specialization.ilike(f"%{specialization}%"))
    return query.order_by(models.DoctorDB.id.asc()).all()

@app.get("/api/doctors/specializations")
def get_doctor_specializations(db: Session = Depends(get_db)):
    """
    Returns unique list of doctor specializations for dropdown filtering.
    """
    specs = db.query(models.DoctorDB.specialization).distinct().all()
    return [s[0] for s in specs if s[0]]

@app.get("/api/doctors/{doctor_id}", response_model=models.DoctorResponse)
def get_doctor_by_id(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(models.DoctorDB).filter(models.DoctorDB.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@app.post("/api/doctors", response_model=models.DoctorResponse, status_code=status.HTTP_201_CREATED)
def add_doctor(doc_in: models.DoctorCreate, db: Session = Depends(get_db)):
    """
    Admin module: Add a new doctor to the hospital system.
    """
    existing = db.query(models.DoctorDB).filter(models.DoctorDB.email.ilike(doc_in.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="A doctor with this email is already registered.")

    new_doc = models.DoctorDB(
        name=doc_in.name,
        email=doc_in.email.lower(),
        password=doc_in.password,
        specialization=doc_in.specialization,
        phone=doc_in.phone,
        availability=doc_in.availability,
        experience=doc_in.experience,
        qualification=doc_in.qualification,
        consultation_fee=doc_in.consultation_fee
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@app.put("/api/doctors/{doctor_id}", response_model=models.DoctorResponse)
def update_doctor(doctor_id: int, doc_update: models.DoctorUpdate, db: Session = Depends(get_db)):
    """
    Update doctor details or working availability.
    """
    doc = db.query(models.DoctorDB).filter(models.DoctorDB.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    for field, val in doc_update.model_dump(exclude_unset=True).items():
        if val is not None:
            setattr(doc, field, val)

    db.commit()
    db.refresh(doc)
    return doc

@app.delete("/api/doctors/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """
    Admin module: Remove doctor from hospital registry.
    """
    doc = db.query(models.DoctorDB).filter(models.DoctorDB.id == doctor_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(doc)
    db.commit()
    return {"message": f"Doctor {doc.name} (ID: {doctor_id}) deleted successfully"}


# ============================================================================
# APPOINTMENTS (Booking, History, Conflict Prevention & Status Updates)
# ============================================================================

@app.get("/api/appointments", response_model=List[models.AppointmentResponse])
def get_all_appointments(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    """
    Admin Module: View all appointments across all patients and doctors.
    """
    query = db.query(models.AppointmentDB)
    if status_filter and status_filter != "All":
        query = query.filter(models.AppointmentDB.status.ilike(status_filter))
    return query.order_by(models.AppointmentDB.date.asc(), models.AppointmentDB.time.asc()).all()

@app.get("/api/appointments/user/{user_id}", response_model=List[models.AppointmentResponse])
def get_user_appointments(user_id: int, db: Session = Depends(get_db)):
    """
    User Module: View personal appointment history and upcoming bookings.
    """
    return db.query(models.AppointmentDB)\
        .filter(models.AppointmentDB.user_id == user_id)\
        .order_by(models.AppointmentDB.date.desc(), models.AppointmentDB.id.desc())\
        .all()

@app.get("/api/appointments/doctor/{doctor_id}", response_model=List[models.AppointmentResponse])
def get_doctor_appointments(doctor_id: int, db: Session = Depends(get_db)):
    """
    Doctor Module: View assigned appointments with patient details and symptoms.
    """
    return db.query(models.AppointmentDB)\
        .filter(models.AppointmentDB.doctor_id == doctor_id)\
        .order_by(models.AppointmentDB.date.asc(), models.AppointmentDB.time.asc())\
        .all()

@app.get("/api/appointments/booked-slots/{doctor_id}/{date}")
def get_booked_slots_for_doctor(doctor_id: int, date: str, db: Session = Depends(get_db)):
    """
    Helper for booking UI: returns time slots already booked for a specific doctor on a date.
    Helps the frontend display availability and disable conflicting slots.
    """
    slots = db.query(models.AppointmentDB.time)\
        .filter(
            models.AppointmentDB.doctor_id == doctor_id,
            models.AppointmentDB.date == date,
            models.AppointmentDB.status.in_(["Pending", "Confirmed"])
        ).all()
    return [s[0] for s in slots]

@app.post("/api/appointments", response_model=models.AppointmentResponse, status_code=status.HTTP_201_CREATED)
def book_appointment(
    appt_in: models.AppointmentCreate,
    user_id: int = Query(..., description="ID of patient booking the appointment"),
    db: Session = Depends(get_db)
):
    """
    User Module: Book an appointment.
    Prevents scheduling conflicts: Checks if the doctor already has an appointment
    at the specified date & time.
    """
    # 1. Verify user exists
    user = db.query(models.UserDB).filter(models.UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Patient record not found.")

    # 2. Verify doctor exists
    doctor = db.query(models.DoctorDB).filter(models.DoctorDB.id == appt_in.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Selected doctor does not exist.")

    # 3. Check for appointment conflicts (Viva question: how conflict is prevented)
    conflict = db.query(models.AppointmentDB).filter(
        models.AppointmentDB.doctor_id == appt_in.doctor_id,
        models.AppointmentDB.date == appt_in.date,
        models.AppointmentDB.time == appt_in.time,
        models.AppointmentDB.status.in_(["Pending", "Confirmed"])
    ).first()

    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Time slot '{appt_in.time}' on {appt_in.date} is already booked for {doctor.name}. Please choose another available slot."
        )

    try:
        new_appointment = models.AppointmentDB(
            user_id=user_id,
            doctor_id=appt_in.doctor_id,
            date=appt_in.date,
            time=appt_in.time,
            status="Pending",
            symptoms=appt_in.symptoms
        )
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        return new_appointment

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict detected: Database unique constraint prevented duplicate booking."
        )

@app.put("/api/appointments/{appointment_id}/status", response_model=models.AppointmentResponse)
def update_appointment_status(
    appointment_id: int,
    status_update: models.AppointmentStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Doctor / Admin Module: Accept ("Confirmed"), Reject ("Rejected"), or mark "Completed".
    """
    appt = db.query(models.AppointmentDB).filter(models.AppointmentDB.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    valid_statuses = ["Pending", "Confirmed", "Rejected", "Cancelled", "Completed"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status '{status_update.status}'. Allowed: {valid_statuses}"
        )

    appt.status = status_update.status
    if status_update.notes is not None:
        appt.notes = status_update.notes

    db.commit()
    db.refresh(appt)
    return appt

@app.put("/api/appointments/{appointment_id}/cancel", response_model=models.AppointmentResponse)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """
    User Module: Cancel personal appointment.
    """
    appt = db.query(models.AppointmentDB).filter(models.AppointmentDB.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt.status = "Cancelled"
    db.commit()
    db.refresh(appt)
    return appt

@app.delete("/api/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """
    Admin / User Module: Permanently remove appointment record.
    """
    appt = db.query(models.AppointmentDB).filter(models.AppointmentDB.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(appt)
    db.commit()
    return {"message": f"Appointment #{appointment_id} deleted successfully"}


# ============================================================================
# MODULE 3: ADMIN MODULE (Analytics & Dashboard)
# ============================================================================

@app.get("/api/admin/stats")
def get_admin_dashboard_stats(db: Session = Depends(get_db)):
    """
    Admin dashboard metrics: Total patients, doctors, appointments and status counts.
    """
    total_users = db.query(models.UserDB).count()
    total_doctors = db.query(models.DoctorDB).count()
    total_appointments = db.query(models.AppointmentDB).count()
    pending_appts = db.query(models.AppointmentDB).filter_by(status="Pending").count()
    confirmed_appts = db.query(models.AppointmentDB).filter_by(status="Confirmed").count()
    rejected_appts = db.query(models.AppointmentDB).filter_by(status="Rejected").count()
    cancelled_appts = db.query(models.AppointmentDB).filter_by(status="Cancelled").count()

    return {
        "total_users": total_users,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "pending_appointments": pending_appts,
        "confirmed_appointments": confirmed_appts,
        "rejected_appointments": rejected_appts,
        "cancelled_appointments": cancelled_appts
    }


# ============================================================================
# MODULE 4: HEALTH INFO MODULE (First-aid, Articles, BMI, Helpline)
# ============================================================================

@app.get("/api/health-articles", response_model=List[models.HealthArticleResponse])
def get_health_articles(
    category: Optional[str] = Query(None, description="Category filter (e.g. First Aid, Emergency, General Health)"),
    db: Session = Depends(get_db)
):
    """
    Health Info Module: View health articles and first-aid instructions.
    """
    query = db.query(models.HealthArticleDB)
    if category and category != "All":
        query = query.filter(models.HealthArticleDB.category.ilike(f"%{category}%"))
    return query.order_by(models.HealthArticleDB.id.asc()).all()

@app.get("/api/health-articles/{article_id}", response_model=models.HealthArticleResponse)
def get_health_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(models.HealthArticleDB).filter(models.HealthArticleDB.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Health article not found")
    return article

@app.post("/api/health-articles", response_model=models.HealthArticleResponse, status_code=status.HTTP_201_CREATED)
def create_health_article(art_in: models.HealthArticleCreate, db: Session = Depends(get_db)):
    """
    Admin Module: Publish a new health education article or emergency guide.
    """
    new_art = models.HealthArticleDB(
        title=art_in.title,
        category=art_in.category,
        content=art_in.content,
        emergency_contact=art_in.emergency_contact
    )
    db.add(new_art)
    db.commit()
    db.refresh(new_art)
    return new_art

@app.delete("/api/health-articles/{article_id}")
def delete_health_article(article_id: int, db: Session = Depends(get_db)):
    art = db.query(models.HealthArticleDB).filter(models.HealthArticleDB.id == article_id).first()
    if not art:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(art)
    db.commit()
    return {"message": f"Article '{art.title}' deleted successfully"}

@app.post("/api/health/bmi", response_model=models.BMICalculatorResponse)
def calculate_bmi(req: models.BMICalculatorRequest):
    """
    Health Info Module: Interactive Body Mass Index (BMI) computation.
    Calculates score, classifies category, and returns clinical lifestyle advice.
    Formula: BMI = weight (kg) / (height (m) ^ 2)
    """
    height_m = req.height_cm / 100.0
    bmi = round(req.weight_kg / (height_m * height_m), 1)

    if bmi < 18.5:
        category = "Underweight"
        risk = "Potential nutritional deficiency and weakened immune defense."
        rec = "Consider increasing nutrient-dense caloric intake and consult a dietitian for a balanced weight-gain plan."
    elif 18.5 <= bmi <= 24.9:
        category = "Normal (Healthy Weight)"
        risk = "Low health risk associated with weight."
        rec = "Excellent! Maintain your balanced nutrition, adequate hydration, and regular 150 minutes of weekly aerobic exercise."
    elif 25.0 <= bmi <= 29.9:
        category = "Overweight"
        risk = "Moderate risk for hypertension, cardiovascular strain, and insulin resistance."
        rec = "Incorporate moderate daily cardiovascular exercises (brisk walking, cycling) and reduce intake of refined sugars and processed fats."
    else:
        category = "Obesity"
        risk = "High risk for type-2 diabetes, coronary heart disease, and joint issues."
        rec = "We recommend consulting a primary physician or certified endocrinologist for a personalized weight management program."

    return models.BMICalculatorResponse(
        bmi=bmi,
        category=category,
        risk_level=risk,
        recommendation=rec
    )

@app.get("/api/health/emergency-contacts")
def get_emergency_contacts():
    """
    Health Info Module: Emergency helpline numbers directory.
    """
    return [
        {"name": "National Emergency Helpline", "number": "112", "service": "All-in-one Emergency Services (Police, Fire, Ambulance)", "icon": "shield-fill-exclamation"},
        {"name": "National Ambulance Service", "number": "108", "service": "Medical Emergency & Quick Hospital Dispatch", "icon": "hospital"},
        {"name": "Disaster Management Helpline", "number": "1078", "service": "National Natural & Civil Disaster Response", "icon": "exclamation-triangle-fill"},
        {"name": "Women's Emergency Helpline", "number": "1091", "service": "24/7 Safety, Rescue & Medical Assistance for Women", "icon": "gender-female"},
        {"name": "Tele-MANAS Mental Health Support", "number": "14416", "service": "Free 24x7 National Psychological Counseling & Crisis Care", "icon": "heart-pulse-fill"},
        {"name": "National Poison Information Center", "number": "1800-116-117", "service": "Emergency Toxic Ingestion & Antidote Guidance", "icon": "capsule"}
    ]


if __name__ == "__main__":
    import uvicorn
    # Render binds dynamically to the PORT environment variable
    server_port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {server_port} for Render deployment...")
    uvicorn.run("main:app", host="0.0.0.0", port=server_port, reload=False)

