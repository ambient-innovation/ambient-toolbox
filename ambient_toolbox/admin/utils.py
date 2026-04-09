def get_user_display_label(user) -> str:
    """Return a human-readable label for a User instance: ``'Full Name (email)'`` with graceful fallbacks."""
    full_name = user.get_full_name().strip()
    email = user.email
    if full_name and email:
        return f"{full_name} ({email})"
    return full_name or email or str(user)
