from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from functools import wraps

from .forms import (
    DoctorForm,
    PatientForm,
    PaymentForm,
    SignupForm,
    PrescriptionForm,
    ProcedureForm,
    VisitForm,
)
from .models import Doctor, Patient, Payment, Visit


def _is_admin_or_super(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name="Admin").exists())


def _is_reception_or_admin(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name__in=["Admin", "Receptionist"]).exists()
    )


def _is_doctor_or_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name__in=["Admin", "Doctor"]).exists()
    )


def _is_non_payment_staff(user):
    return user.is_authenticated and (
        user.is_superuser
        or user.groups.filter(name__in=["Admin", "Receptionist", "Doctor"]).exists()
    )


def role_required(check_fn):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not check_fn(request.user):
                raise PermissionDenied("You do not have permission to access this page.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class UserLoginView(LoginView):
    template_name = "registration/login.html"


def health_check(request):
    return JsonResponse({"status": "ok"})


def signup_view(request):
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data["email"]
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.save()

        role_name = form.cleaned_data["role"]
        group, _ = Group.objects.get_or_create(name=role_name)
        user.groups.add(group)

        if role_name == "Doctor":
            Doctor.objects.create(
                first_name=user.first_name,
                last_name=user.last_name,
                specialization="General Medicine",
                phone="Pending",
                email=user.email,
            )

        auth_login(request, user)
        messages.success(request, "Signup successful. Your account is ready.")
        return redirect("dashboard")

    return render(request, "registration/signup.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    context = {
        "patient_count": Patient.objects.count(),
        "doctor_count": Doctor.objects.count(),
        "visit_count": Visit.objects.count(),
        "payment_count": Payment.objects.count(),
        "recent_visits": Visit.objects.select_related("patient", "doctor")[:5],
        "recent_payments": Payment.objects.select_related("patient")[:5],
    }
    return render(request, "core/dashboard.html", context)


@login_required
def search(request):
    query = request.GET.get("q", "").strip()
    patients = Patient.objects.none()
    if query:
        patients = Patient.objects.filter(
            Q(patient_id__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
        )
    return render(request, "core/search_results.html", {"query": query, "patients": patients})


@role_required(_is_non_payment_staff)
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, "core/patient_list.html", {"patients": patients})


@role_required(_is_non_payment_staff)
def patient_create(request):
    form = PatientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        patient = form.save()
        messages.success(request, f"Patient {patient.patient_id} registered successfully.")
        return redirect("patient_list")
    return render(request, "core/form_page.html", {"title": "Register Patient", "form": form})


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    visits = patient.visits.select_related("doctor")
    payments = patient.payments.all()
    return render(
        request,
        "core/patient_detail.html",
        {"patient": patient, "visits": visits, "payments": payments},
    )


@role_required(_is_non_payment_staff)
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, "core/doctor_list.html", {"doctors": doctors})


@role_required(_is_admin_or_super)
def doctor_create(request):
    form = DoctorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        doctor = form.save()
        messages.success(request, f"Doctor {doctor.doctor_code} registered successfully.")
        return redirect("doctor_list")
    return render(request, "core/form_page.html", {"title": "Register Doctor", "form": form})


@role_required(_is_non_payment_staff)
def visit_list(request):
    visits = Visit.objects.select_related("patient", "doctor")
    return render(request, "core/visit_list.html", {"visits": visits})


@role_required(_is_non_payment_staff)
def visit_create(request):
    initial = {}
    patient_id = request.GET.get("patient")
    if patient_id:
        initial["patient"] = patient_id
    form = VisitForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        visit = form.save(commit=False)
        visit.created_by = request.user
        visit.save()
        messages.success(request, "Visit recorded successfully.")
        return redirect("visit_detail", pk=visit.pk)
    return render(request, "core/form_page.html", {"title": "Record Visit", "form": form})


@login_required
def visit_detail(request, pk):
    visit = get_object_or_404(Visit.objects.select_related("patient", "doctor"), pk=pk)
    return render(request, "core/visit_detail.html", {"visit": visit})


@role_required(_is_doctor_or_admin)
def prescription_create(request):
    initial = {}
    visit_id = request.GET.get("visit")
    if visit_id:
        initial["visit"] = visit_id
    form = PrescriptionForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        prescription = form.save()
        messages.success(request, "Prescription added successfully.")
        return redirect("visit_detail", pk=prescription.visit.pk)
    return render(request, "core/form_page.html", {"title": "Add Prescription", "form": form})


@role_required(_is_doctor_or_admin)
def procedure_create(request):
    initial = {}
    visit_id = request.GET.get("visit")
    if visit_id:
        initial["visit"] = visit_id
    form = ProcedureForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        procedure = form.save()
        messages.success(request, "Procedure recorded successfully.")
        return redirect("visit_detail", pk=procedure.visit.pk)
    return render(request, "core/form_page.html", {"title": "Add Procedure", "form": form})


@role_required(_is_reception_or_admin)
def payment_list(request):
    payments = Payment.objects.select_related("patient", "visit")
    return render(request, "core/payment_list.html", {"payments": payments})


@role_required(_is_reception_or_admin)
def payment_create(request):
    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Payment recorded successfully.")
        return redirect("payment_list")
    return render(request, "core/form_page.html", {"title": "Record Payment", "form": form})
