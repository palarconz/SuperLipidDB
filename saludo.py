import getpass
from datetime import datetime


def obtener_saludo(nombre: str = None) -> str:
    """Genera un saludo personalizado según la hora del día."""
    if not nombre:
        # Detectar el nombre de usuario del sistema si no se proporciona uno
        nombre = getpass.getuser()

    hora = datetime.now().hour
    if 5 <= hora < 12:
        momento = "Buenos días"
    elif 12 <= hora < 20:
        momento = "Buenas tardes"
    else:
        momento = "Buenas noches"

    return f"👋 ¡{momento}, {nombre}! Qué gusto saludarte. Espero que tengas un excelente día programando."


if __name__ == "__main__":
    # Saludo para Pedro Felipe
    print(obtener_saludo("Pedro Felipe"))
