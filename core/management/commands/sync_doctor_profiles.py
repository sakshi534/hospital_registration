from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Doctor


class Command(BaseCommand):
    help = "Sync Doctor-group auth users into Doctor profiles if missing"

    def handle(self, *args, **options):
        doctor_users = User.objects.filter(groups__name="Doctor").distinct()
        created = 0

        for user in doctor_users:
            email = (user.email or "").strip()
            first_name = (user.first_name or "").strip() or "Doctor"
            last_name = (user.last_name or "").strip() or user.username

            if email:
                exists = Doctor.objects.filter(email=email).exists()
            else:
                exists = Doctor.objects.filter(
                    first_name=first_name,
                    last_name=last_name,
                    phone="Pending",
                ).exists()

            if exists:
                continue

            Doctor.objects.create(
                first_name=first_name,
                last_name=last_name,
                specialization="General Medicine",
                phone="Pending",
                email=email,
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Doctor profile sync complete. Users scanned: {doctor_users.count()}, created: {created}, total profiles: {Doctor.objects.count()}"
            )
        )
