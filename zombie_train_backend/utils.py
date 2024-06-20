def get_codename(permission: str) -> str:
    return permission.split(".")[-1]
