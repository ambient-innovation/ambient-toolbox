from typing import List


def generate_default_permissions(model_name: str) -> List[str]:
    return [
        f"add_{model_name}",
        f"change_{model_name}",
        f"delete_{model_name}",
        f"view_{model_name}",
    ]
