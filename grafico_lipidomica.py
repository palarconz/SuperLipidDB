"""
Script para realizar análisis estadísticos completos de datos de lipidómica
y generar un gráfico de calidad científica con anotaciones estadísticas visuales.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


def cargar_datos(archivo_csv: str | Path):
    """Carga los datos del CSV separando por condición."""
    datos = defaultdict(lambda: defaultdict(list))
    with open(archivo_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        lipidos = [col for col in reader.fieldnames if col not in ("Muestra", "Condicion")]
        for fila in reader:
            cond = fila["Condicion"]
            for lip in lipidos:
                datos[cond][lip].append(float(fila[lip]))
    return lipidos, datos


def realizar_analisis_estadistico(lipidos: list[str], datos: dict[str, dict[str, list[float]]]):
    """
    Realiza prueba t de Welch y calcula Fold-Change y significancia.
    """
    resultados = []
    p_valores = []

    for lipido in lipidos:
        ctrl = np.array(datos["Control"][lipido])
        trat = np.array(datos["Tratamiento"][lipido])

        # Estadísticos descriptivos
        media_ctrl, sd_ctrl = mean(ctrl), stdev(ctrl)
        media_trat, sd_trat = mean(trat), stdev(trat)

        # Welch's t-test (no asume varianzas iguales)
        t_stat, p_val = stats.ttest_ind(ctrl, trat, equal_var=False)

        # Log2 Fold Change
        fold_change = media_trat / media_ctrl
        log2_fc = np.log2(fold_change)

        p_valores.append(p_val)
        resultados.append({
            "lipido": lipido,
            "media_ctrl": media_ctrl,
            "sd_ctrl": sd_ctrl,
            "media_trat": media_trat,
            "sd_trat": sd_trat,
            "t_stat": t_stat,
            "p_val": p_val,
            "fold_change": fold_change,
            "log2_fc": log2_fc,
            "ctrl_data": ctrl,
            "trat_data": trat,
        })

    # Corrección de Benjamini-Hochberg (FDR)
    # Ordenar p-valores para ajustar
    n = len(p_valores)
    orden = np.argsort(p_valores)
    p_ajustados = np.zeros(n)
    cummin = 1.0
    for idx in reversed(orden):
        rank = np.where(orden == idx)[0][0] + 1
        adj = p_valores[idx] * n / rank
        cummin = min(cummin, adj)
        p_ajustados[idx] = cummin

    for i, res in enumerate(resultados):
        res["p_adj"] = min(1.0, float(p_ajustados[i]))
        p = res["p_val"]
        if p < 0.0001:
            res["signif"] = "****"
        elif p < 0.001:
            res["signif"] = "***"
        elif p < 0.01:
            res["signif"] = "**"
        elif p < 0.05:
            res["signif"] = "*"
        else:
            res["signif"] = "ns"

    return resultados


def dibujar_bracket_significancia(ax, x1, x2, y, h, texto, p_val):
    """Dibuja un corchete de significancia estadística entre dos posiciones x."""
    # Línea del corchete: _┌───┐_
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.2, color="#222222")

    # Formato de texto: ej. '*** (p = 0.0004)' o 'ns (p = 0.12)'
    if p_val < 0.0001:
        etiqueta = f"{texto}\n(p < 0.0001)"
    else:
        etiqueta = f"{texto}\n(p = {p_val:.4f})"

    ax.text(
        (x1 + x2) * 0.5,
        y + h * 1.1,
        etiqueta,
        ha="center",
        va="bottom",
        color="#111111",
        fontsize=9,
        fontweight="bold" if texto != "ns" else "normal",
    )


def generar_grafico_con_estadistica(resultados: list[dict], salida_png: Path):
    """Genera gráfico de barras con puntos de dispersión y corchetes de significancia."""
    lipidos = [r["lipido"] for r in resultados]
    x = np.arange(len(lipidos))
    width = 0.32

    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)

    medias_ctrl = [r["media_ctrl"] for r in resultados]
    sds_ctrl = [r["sd_ctrl"] for r in resultados]
    medias_trat = [r["media_trat"] for r in resultados]
    sds_trat = [r["sd_trat"] for r in resultados]

    # Barras de Control
    bars_ctrl = ax.bar(
        x - width / 2,
        medias_ctrl,
        width,
        yerr=sds_ctrl,
        capsize=4,
        error_kw={"elinewidth": 1.2, "ecolor": "#333333"},
        label="Control (n=10)",
        color="#2b5c8f",
        alpha=0.85,
        edgecolor="#1a3654",
        linewidth=1.0,
        zorder=2,
    )

    # Barras de Tratamiento
    bars_trat = ax.bar(
        x + width / 2,
        medias_trat,
        width,
        yerr=sds_trat,
        capsize=4,
        error_kw={"elinewidth": 1.2, "ecolor": "#333333"},
        label="Tratamiento (n=10)",
        color="#d95f02",
        alpha=0.85,
        edgecolor="#803801",
        linewidth=1.0,
        zorder=2,
    )

    # Puntos individuales (stripplot con jitter suave)
    np.random.seed(42)
    for i, res in enumerate(resultados):
        jitter_ctrl = np.random.uniform(-0.06, 0.06, size=len(res["ctrl_data"]))
        jitter_trat = np.random.uniform(-0.06, 0.06, size=len(res["trat_data"]))

        ax.scatter(
            (x[i] - width / 2) + jitter_ctrl,
            res["ctrl_data"],
            color="#0d2847",
            alpha=0.6,
            s=22,
            edgecolors="white",
            linewidth=0.5,
            zorder=3,
        )
        ax.scatter(
            (x[i] + width / 2) + jitter_trat,
            res["trat_data"],
            color="#6b2b00",
            alpha=0.6,
            s=22,
            edgecolors="white",
            linewidth=0.5,
            zorder=3,
        )

    # Añadir corchetes de significancia estadística
    max_y_total = 0
    for i, res in enumerate(resultados):
        puntos_max = max(max(res["ctrl_data"]), max(res["trat_data"]))
        barras_max = max(res["media_ctrl"] + res["sd_ctrl"], res["media_trat"] + res["sd_trat"])
        y_top = max(puntos_max, barras_max)

        h_step = max(y_top * 0.035, 6.0)
        y_bracket = y_top + h_step * 1.8
        dibujar_bracket_significancia(
            ax,
            x1=x[i] - width / 2,
            x2=x[i] + width / 2,
            y=y_bracket,
            h=h_step,
            texto=res["signif"],
            p_val=res["p_val"],
        )
        final_top = y_bracket + h_step * 3.5
        if final_top > max_y_total:
            max_y_total = final_top

    # Configuración de límites y rejilla
    ax.set_ylim(0, max_y_total * 1.10)
    ax.set_ylabel("Abundancia Relativa (u.a.)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Análisis Estadístico de Lipidómica: Especies de Fosfatidilcolina (PC)\nControl vs. Tratamiento (Welch's t-test)",
        fontsize=14,
        fontweight="bold",
        pad=18,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(lipidos, fontsize=11, fontweight="bold")

    # Leyenda estilizada
    ax.legend(
        loc="upper right",
        frameon=True,
        facecolor="white",
        edgecolor="#cccccc",
        fontsize=10.5,
    )

    # Nota al pie sobre significancia
    nota_pie = (
        "Significancia estadística (t de Welch): **** p < 0.0001, *** p < 0.001, ** p < 0.01, * p < 0.05, ns: no significativo (p ≥ 0.05).\n"
        "Barras: Media ± DE. Puntos individuales representan réplicas biológicas (n=10 por grupo)."
    )
    fig.text(0.12, 0.02, nota_pie, fontsize=8.5, color="#444444", style="italic")

    ax.grid(axis="y", linestyle="--", alpha=0.5, zorder=1)
    ax.set_axisbelow(True)

    plt.subplots_adjust(bottom=0.14, top=0.90)
    plt.savefig(salida_png)
    plt.close()
    print(f"Gráfico con anotaciones estadísticas guardado en: {salida_png.name}")


def main():
    base_dir = Path(__file__).parent
    archivo_csv = base_dir / "datos_lipidomica.csv"
    salida_png = base_dir / "grafico_lipidomica.png"

    lipidos, datos = cargar_datos(archivo_csv)
    resultados = realizar_analisis_estadistico(lipidos, datos)

    print("\n" + "=" * 80)
    print("🔬 REPORTE DE ANÁLISIS ESTADÍSTICO (Prueba t de Welch)")
    print("=" * 80)
    encabezado = f"{'Lípido':<10} | {'Control (Media±DE)':<20} | {'Tratamiento (Media±DE)':<22} | {'Log2(FC)':<8} | {'p-valor':<10} | {'Signif'}"
    print(encabezado)
    print("-" * len(encabezado))

    for r in resultados:
        str_ctrl = f"{r['media_ctrl']:.2f} ± {r['sd_ctrl']:.2f}"
        str_trat = f"{r['media_trat']:.2f} ± {r['sd_trat']:.2f}"
        print(f"{r['lipido']:<10} | {str_ctrl:<20} | {str_trat:<22} | {r['log2_fc']:>+7.2f}  | {r['p_val']:.4e} | {r['signif']}")
    print("=" * 80 + "\n")

    generar_grafico_con_estadistica(resultados, salida_png)


if __name__ == "__main__":
    main()
