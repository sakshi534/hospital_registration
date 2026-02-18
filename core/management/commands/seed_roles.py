from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default role groups: Admin, Receptionist, Doctor"

    def handle(self, *args, **options):
        for role in ["Admin", "Receptionist", "Doctor"]:
            Group.objects.get_or_create(name=role)
        self.stdout.write(self.style.SUCCESS("Default role groups are ready."))
