def role_flags(request):
    user = request.user
    if not user.is_authenticated:
        return {
            "is_admin_user": False,
            "is_reception_user": False,
            "is_doctor_user": False,
        }

    group_names = set(user.groups.values_list("name", flat=True))
    is_admin = user.is_superuser or "Admin" in group_names
    is_reception = is_admin or "Receptionist" in group_names
    is_doctor = is_admin or "Doctor" in group_names

    return {
        "is_admin_user": is_admin,
        "is_reception_user": is_reception,
        "is_doctor_user": is_doctor,
        "is_non_payment_staff_user": is_reception or is_doctor,
    }
