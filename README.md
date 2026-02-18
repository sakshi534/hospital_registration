# Hospital Registration System (Django)

Simple hospital management web app for:
- Patient registration and searchable records
- Doctor registration
- Visit history
- Prescriptions
- Procedures performed
- Payments tracking

It includes login-based access and role groups: **Admin**, **Receptionist**, **Doctor**.

## 1) Local setup

```bash
cd /Users/sakshi/Desktop/hospital_registration
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python manage.py migrate
./.venv/bin/python manage.py seed_roles
./.venv/bin/python manage.py createsuperuser
./.venv/bin/python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## 2) Login and roles

- Use Django Admin (`/admin`) with superuser to create staff users.
- Assign users to groups:
  - **Admin**: Full access
  - **Receptionist**: Patients, visits, payments
  - **Doctor**: Visits, prescriptions, procedures

### Signup support
- App now includes self-signup at `/signup/` for **Receptionist** and **Doctor** users.
- New users are automatically logged in after signup.
- For initial admin access, still create superuser using:
  ```bash
  ./.venv/bin/python manage.py createsuperuser
  ```

## 3) Main pages

- Dashboard: `/`
- Search: `/search/`
- Patients: `/patients/`
- Doctors: `/doctors/`
- Visits: `/visits/`
- Payments: `/payments/`

## 4) Environment variables

Copy `.env.example` and set values in your host environment:

- `DEBUG` (True/False)
- `SECRET_KEY`
- `ALLOWED_HOSTS` (comma-separated)
- `DATABASE_URL` (for PostgreSQL in production)

## 5) Production deployment on Render (recommended)

This project now includes `render.yaml` so you can deploy quickly using Render Blueprint.

### A) Prepare code
1. Commit and push your project to GitHub.

### B) Deploy via Blueprint
1. In Render, click **New +** → **Blueprint**.
2. Connect your GitHub repo and select this project.
3. Render will detect `render.yaml` and create:
   - Web service (`hospital-registration-web`)
   - PostgreSQL database (`hospital-registration-db`)
4. Approve and deploy.

### C) Post-deploy one-time commands (Render Shell)
Run:
```bash
python manage.py seed_roles
python manage.py createsuperuser
```

### D) Health and access
- Health endpoint: `/health/`
- App URL: your Render service domain (HTTPS)

### E) Important production env vars
These are already modeled in `render.yaml`, but verify values in Render dashboard:
- `DEBUG=False`
- `SECRET_KEY` (auto-generated)
- `DATABASE_URL` (from Render Postgres)
- `ALLOWED_HOSTS` (your Render domain)
- `CSRF_TRUSTED_ORIGINS` (e.g. `https://your-domain.onrender.com`)

Now the app is productionized and can be accessed remotely from anywhere.
