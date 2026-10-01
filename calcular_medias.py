"""
Script para analizar datos de lipidómica desde un archivo CSV.
Calcula la media de abundancia de cada especie lipídica (PC) agrupada por condición.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


def calcular_medias_por_condicion(archivo_csv: str | Path) -> dict[str, dict[str, float]]:
    """
    Lee un archivo CSV de lipidómica y calcula la media de cada lípido por condición.

    Retorna un diccionario con la estructura:
    {
        'Control': {'PC(32:0)': 144.5, ...},
        'Tratamiento': {'PC(32:0)': 165.9, ...}
    }
    """
    datos_por_grupo = defaultdict(lambda: defaultdict(list))
    lipidos = []

    with open(archivo_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columnas = reader.fieldnames or []

        # Identificar las columnas de lípidos (todas excepto 'Muestra' y 'Condicion')
        lipidos = [col for col in columnas if col not in ("Muestra", "Condicion")]

        for fila in reader:
            condicion = fila["Condicion"]
            for lipido in lipidos:
                valor = float(fila[lipido])
                datos_por_grupo[condicion][lipido].append(valor)

    # Calcular la media para cada lípido en cada condición
    medias_por_grupo = {}
    for condicion, lipidos_datos in datos_por_grupo.items():
        medias_por_grupo[condicion] = {
            lipido: mean(valores) for lipido, valores in lipidos_datos.items()
        }

    return medias_por_grupo


def mostrar_resultados(medias: dict[str, dict[str, float]]):
    """Muestra los resultados formateados en una tabla clara por consola."""
    grupos = list(medias.keys())
    if not grupos:
        print("No se encontraron datos.")
        return

    lipidos = list(medias[grupos[0]].keys())

    print("\n" + "=" * 65)
    print("📊 RESULTADOS DEL ANÁLISIS DE LIPIDÓMICA: MEDIA POR GRUPO")
    print("=" * 65)

    header = f"{'Lípido':<12} | " + " | ".join(f"{g:>15}" for g in grupos)
    print(header)
    print("-" * len(header))

    for lipido in lipidos:
        fila = f"{lipido:<12} | "
        for grupo in grupos:
            media_val = medias[grupo].get(lipido, 0.0)
            fila += f"{media_val:>15.2f} | "
        print(fila.rstrip(" |"))

    print("=" * 65 + "\n")


if __name__ == "__main__":
    ruta_csv = Path(__file__).parent / "datos_lipidomica.csv"
    print(f"Leyendo archivo: {ruta_csv.name}...")

    resultados = calcular_medias_por_condicion(ruta_csv)
    mostrar_resultados(resultados)
