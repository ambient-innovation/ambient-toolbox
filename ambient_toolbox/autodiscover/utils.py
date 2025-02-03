def unique_append_to_inner_list(*, data: dict, key: str | int, value) -> dict:
    """
    Inserts "value" in the dictionary "data" on "key".
    If "key" doesn't exist yet, it will create a new list containing "value".
    If "value" at "key" already exists, it won't be appended.
    """
    if key not in data:
        data[key] = [value]
    elif value not in data[key]:
        data[key].append(value)

    return data
