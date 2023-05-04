from django.core.cache import cache


def clear_cache():
    """
    Clears the django cache
    """
    cache.clear()
