from django.db import models
from django.utils import timezone


class Patient(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    patient_id = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    blood_group = models.CharField(max_length=8, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient_id} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.patient_id:
            date_part = timezone.now().strftime("%Y%m%d")
            prefix = f"P-{date_part}"
            count = Patient.objects.filter(patient_id__startswith=prefix).count() + 1
            self.patient_id = f"{prefix}-{count:03d}"
        super().save(*args, **kwargs)


class Doctor(models.Model):
    doctor_code = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name} ({self.specialization})"

    def save(self, *args, **kwargs):
        if not self.doctor_code:
            prefix = "D"
            count = Doctor.objects.count() + 1
            self.doctor_code = f"{prefix}-{count:03d}"
        super().save(*args, **kwargs)


class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="visits")
    visit_date = models.DateField(default=timezone.now)
    reason = models.CharField(max_length=255)
    diagnosis = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-visit_date", "-created_at"]

    def __str__(self):
        return f"Visit #{self.id} - {self.patient} with {self.doctor}"


class Prescription(models.Model):
    visit = models.ForeignKey(
        Visit, on_delete=models.CASCADE, related_name="prescriptions"
    )
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.medicine_name} for {self.visit.patient}"


class ProcedurePerformed(models.Model):
    visit = models.ForeignKey(
        Visit, on_delete=models.CASCADE, related_name="procedures"
    )
    procedure_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    performed_on = models.DateField(default=timezone.now)
    outcome = models.CharField(max_length=200, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-performed_on", "-created_at"]

    def __str__(self):
        return f"{self.procedure_name} - {self.visit.patient}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Cash"),
        ("card", "Card"),
        ("upi", "UPI"),
        ("bank_transfer", "Bank Transfer"),
        ("insurance", "Insurance"),
    ]

    STATUS_CHOICES = [
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("failed", "Failed"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="payments")
    visit = models.ForeignKey(
        Visit, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="cash")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="paid")
    reference_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    paid_on = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-paid_on", "-created_at"]

    def __str__(self):
        return f"{self.patient} - {self.amount} ({self.status})"

# Create your models here.
