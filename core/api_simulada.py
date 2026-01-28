def validate_user(username: str, password: str, role: str) -> bool:
    usuarios = {
        "Administrador": {"admin": "admin123"},
        "Chofer": {"chofer": "chofer123"},
        "Supervisor": {"supervisor": "sup123"}
    }
    return usuarios.get(role, {}).get(username) == password