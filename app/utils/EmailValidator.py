# utils.py
import re

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def es_correo_valido(correo: str) -> bool:
    """
    Valida si un correo electrónico tiene un formato sintácticamente correcto.
    """
    if not correo:
        return False
    # .strip() elimina espacios en blanco accidentales al inicio o final
    return bool(re.match(EMAIL_REGEX, correo.strip()))