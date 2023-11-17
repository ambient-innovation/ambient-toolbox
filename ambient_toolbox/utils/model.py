from django.db.models import ForeignKey


def object_to_dict(obj, blacklisted_fields: list = None, include_id: bool = False) -> dict:
    """
    Returns a dict with all data defined in the model class as a key-value-dict
    Attention: Does not work for M2M fields!
    """

    # Default blacklist
    blacklisted_fields = blacklisted_fields if blacklisted_fields else []

    # Add default django primary key to blacklist
    if not include_id:
        blacklisted_fields.append("id")

    data = vars(obj)
    valid_data = {}

    valid_fields = []
    for f in obj.__class__._meta.get_fields():
        if type(f) != ForeignKey:
            valid_fields.append(f.name)
        else:
            valid_fields.append(f"{f.name}_id")

    for key, value in list(data.items()):
        if key in valid_fields and key not in blacklisted_fields:
            valid_data[key] = value

    return valid_data
