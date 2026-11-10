# Render Deployment Guide for LifeLine Backend

This guide outlines how to deploy the **LifeLine FastAPI Backend** to **Render** using your **Aiven PostgreSQL Cloud Database**.

---

## 📋 Pre-Configured Database Details (Already Active & Seeded)

Your cloud database is already connected, all 5 database tables (`users`, `doctors`, `appointments`, `admin`, `health_articles`) have been created, and initial test accounts are pre-seeded:

- **Host:** `pg-2246798-project-854c.e.aivencloud.com`
- **Port:** `12035`
- **Database:** `defaultdb`
- **User:** `avnadmin`
- **SSL Mode:** `require`
- **Full Connection URI:**
  ```text
  postgresql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>?sslmode=require
  ```

---

## 🚀 Steps to Deploy on Render

### Step 1: Push Code to GitHub / GitLab
Make sure your `Mini-Project-Backend` folder is committed and pushed to your GitHub or GitLab repository:
```bash
git add .
git commit -m "Configure FastAPI backend for Render deployment with Aiven PostgreSQL"
git push origin main
```

---

### Step 2: Create a Web Service on Render
1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** in the top right corner and select **Web Service**.
3. Connect your Git repository containing the backend code.
4. Fill in the service configuration details:

| Setting | Value |
| :--- | :--- |
| **Name** | `lifeline-backend` |
| **Region** | Choose Frankfurt (EU) or Oregon (US) |
| **Branch** | `main` |
| **Root Directory** | `Mini-Project-Backend` *(Leave blank if repo root IS the backend)* |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

---

### Step 3: Add Environment Variables on Render
Under the **Environment Variables** section on Render, add the following key-value pairs:

| Key | Value |
| :--- | :--- |
| **`DATABASE_URL`** | `postgresql://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>?sslmode=require` |
| **`ENVIRONMENT`** | `production` |
| **`ALLOWED_ORIGINS`** | `*` *(or your frontend Render URL)* |
| **`PYTHON_VERSION`** | `3.10.12` |

> [!NOTE]
> Render automatically sets the `$PORT` environment variable and injects it into `uvicorn main:app --host 0.0.0.0 --port $PORT`.

---

### Step 4: Deploy & Verify
1. Click **Create Web Service**.
2. Render will run `pip install -r requirements.txt` and start the server.
3. Once the build finishes and shows **"Your service is live 🎉"**, verify by visiting:
   - Health Check: `https://<your-render-subdomain>.onrender.com/api/health`
   - Interactive Swagger Docs: `https://<your-render-subdomain>.onrender.com/docs`

---

## 🧪 Pre-Seeded Test Accounts (Ready on Cloud Database)

| Role | Email / Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Patient** | `patient@lifeline.com` | `password123` | Patient appointment booking & history |
| **Doctor** | `doctor.sharma@lifeline.com` | `password123` | Dr. Rajesh Sharma (Cardiology portal) |
| **Doctor** | `doctor.patel@lifeline.com` | `password123` | Dr. Priya Patel (Pediatrics portal) |
| **Admin** | `admin@lifeline.com` or `admin` | `admin123` | Hospital management & analytics |
