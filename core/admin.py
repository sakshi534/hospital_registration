from django.contrib import admin
from .models import (
    Doctor,
    Patient,
    Payment,
    Prescription,
    ProcedurePerformed,
    Visit,
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_id", "first_name", "last_name", "phone", "created_at")
    search_fields = ("patient_id", "first_name", "last_name", "phone", "email")
    list_filter = ("gender", "created_at")


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("doctor_code", "first_name", "last_name", "specialization", "phone")
    search_fields = ("doctor_code", "first_name", "last_name", "specialization")


class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 0


class ProcedureInline(admin.TabularInline):
    model = ProcedurePerformed
    extra = 0


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "visit_date", "reason")
    list_filter = ("visit_date",)
    search_fields = ("patient__patient_id", "patient__first_name", "doctor__first_name", "reason")
    inlines = [PrescriptionInline, ProcedureInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "amount", "method", "status", "paid_on")
    list_filter = ("method", "status", "paid_on")
    search_fields = ("patient__patient_id", "patient__first_name", "reference_id")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("medicine_name", "visit", "dosage", "frequency", "duration")
    search_fields = ("medicine_name", "visit__patient__first_name", "visit__patient__patient_id")


@admin.register(ProcedurePerformed)
class ProcedurePerformedAdmin(admin.ModelAdmin):
    list_display = ("procedure_name", "visit", "performed_on", "cost")
    list_filter = ("performed_on",)
    search_fields = ("procedure_name", "visit__patient__first_name", "visit__patient__patient_id")
