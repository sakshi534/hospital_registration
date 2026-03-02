from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Doctor, Patient, Payment, Prescription, ProcedurePerformed, Visit


class DateInput(forms.DateInput):
    input_type = "date"


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "phone",
            "email",
            "address",
            "blood_group",
            "emergency_contact",
        ]
        widgets = {
            "date_of_birth": DateInput(),
            "address": forms.Textarea(attrs={"rows": 2}),
        }


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            "first_name",
            "last_name",
            "specialization",
            "phone",
            "email",
            "license_number",
            "consultation_fee",
        ]


class VisitForm(forms.ModelForm):
    class Meta:
        model = Visit
        fields = [
            "patient",
            "doctor",
            "visit_date",
            "reason",
            "diagnosis",
            "notes",
            "follow_up_date",
        ]
        widgets = {
            "visit_date": DateInput(),
            "follow_up_date": DateInput(),
            "diagnosis": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = [
            "visit",
            "medicine_name",
            "dosage",
            "frequency",
            "duration",
            "instructions",
        ]
        widgets = {
            "instructions": forms.Textarea(attrs={"rows": 2}),
        }


class ProcedureForm(forms.ModelForm):
    class Meta:
        model = ProcedurePerformed
        fields = [
            "visit",
            "procedure_name",
            "description",
            "performed_on",
            "outcome",
            "cost",
        ]
        widgets = {
            "performed_on": DateInput(),
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            "patient",
            "visit",
            "amount",
            "method",
            "status",
            "reference_id",
            "notes",
            "paid_on",
        ]
        widgets = {
            "paid_on": DateInput(),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class SignupForm(UserCreationForm):
    ROLE_CHOICES = [
        ("Receptionist", "Receptionist"),
        ("Doctor", "Doctor"),
    ]

    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "password1",
            "password2",
        )


class PublicAppointmentForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    date_of_birth = forms.DateField(required=False, widget=DateInput())
    gender = forms.ChoiceField(
        choices=[("", "Select"), *Patient.GENDER_CHOICES], required=False
    )
    phone = forms.CharField(max_length=20)
    email = forms.EmailField(required=False)
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
    emergency_contact = forms.CharField(max_length=20, required=False)

    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())
    visit_date = forms.DateField(widget=DateInput())
    reason = forms.CharField(max_length=255)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
