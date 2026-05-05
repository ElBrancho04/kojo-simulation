"""Visualizaciones de resultados para la Fase 7."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import matplotlib.pyplot as plt

from stats import ResultadoExperimento


def _orden_experimentos(resultados: Sequence[ResultadoExperimento]) -> List[str]:
    nombres = {res.nombre for res in resultados}
    return sorted(nombres, key=lambda n: int(n.replace("E", "")))


def _mapear_resultados(resultados: Sequence[ResultadoExperimento]) -> Dict[str, Dict[str, ResultadoExperimento]]:
    pares: Dict[str, Dict[str, ResultadoExperimento]] = {}
    for res in resultados:
        pares.setdefault(res.nombre, {})[res.escenario] = res
    return pares


def _intervalo_error(res: ResultadoExperimento) -> Tuple[float, float]:
    if res.ic_inferior is None or res.ic_superior is None:
        return 0.0, 0.0
    return res.media - res.ic_inferior, res.ic_superior - res.media


def _guardar_figura(ruta_salida: Path) -> None:
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(ruta_salida, dpi=150, bbox_inches="tight")
    plt.close()


def graficar_barras_comparativas(resultados: Sequence[ResultadoExperimento], ruta_salida: Path) -> None:
    pares = _mapear_resultados(resultados)
    experimentos = _orden_experimentos(resultados)

    medias_a = [pares[n]["A"].media for n in experimentos]
    medias_b = [pares[n]["B"].media for n in experimentos]
    errores_a = [list(_intervalo_error(pares[n]["A"])) for n in experimentos]
    errores_b = [list(_intervalo_error(pares[n]["B"])) for n in experimentos]

    x = range(len(experimentos))
    ancho = 0.35

    plt.figure(figsize=(10, 5))
    plt.bar([i - ancho / 2 for i in x], medias_a, width=ancho, yerr=list(zip(*errores_a)), capsize=4, label="Escenario A")
    plt.bar([i + ancho / 2 for i in x], medias_b, width=ancho, yerr=list(zip(*errores_b)), capsize=4, label="Escenario B")
    plt.xticks(list(x), experimentos)
    plt.ylabel("% de quejas")
    plt.title("Comparación de medias por experimento")
    plt.legend()

    _guardar_figura(ruta_salida)


def graficar_boxplots(resultados: Sequence[ResultadoExperimento], ruta_salida: Path) -> None:
    pares = _mapear_resultados(resultados)
    experimentos = _orden_experimentos(resultados)

    data = []
    posiciones = []
    etiquetas = []
    pos = 1
    for nombre in experimentos:
        for escenario in ("A", "B"):
            data.append(pares[nombre][escenario].porcentajes)
            posiciones.append(pos)
            etiquetas.append(f"{nombre}-{escenario}")
            pos += 1
        pos += 0.5

    plt.figure(figsize=(12, 5))
    boxplot = plt.boxplot(data, positions=posiciones, patch_artist=True)

    color_a = "#4C72B0"
    color_b = "#DD8452"
    for idx, caja in enumerate(boxplot["boxes"]):
        caja.set_facecolor(color_a if idx % 2 == 0 else color_b)

    plt.legend(
        [plt.Line2D([0], [0], color=color_a, lw=10), plt.Line2D([0], [0], color=color_b, lw=10)],
        ["Escenario A", "Escenario B"],
        loc="upper right",
    )
    plt.xticks(posiciones, etiquetas, rotation=45, ha="right")
    plt.ylabel("% de quejas")
    plt.title("Distribución de % de quejas por experimento")

    _guardar_figura(ruta_salida)


def graficar_reduccion(resultados: Sequence[ResultadoExperimento], ruta_salida: Path) -> None:
    pares = _mapear_resultados(resultados)
    experimentos = _orden_experimentos(resultados)

    reducciones = [pares[n]["A"].media - pares[n]["B"].media for n in experimentos]

    plt.figure(figsize=(8, 5))
    plt.barh(experimentos, reducciones)
    plt.xlabel("Reducción absoluta (p.p.)")
    plt.title("Reducción absoluta por experimento (A - B)")

    _guardar_figura(ruta_salida)


def graficar_sensibilidad_lambda(resultados: Sequence[ResultadoExperimento], ruta_salida: Path) -> None:
    pares = _mapear_resultados(resultados)
    experimentos = ["E1", "E2", "E6"]

    datos = {"A": [], "B": []}
    for nombre in experimentos:
        for escenario in ("A", "B"):
            res = pares[nombre][escenario]
            datos[escenario].append((res.lambda_pico, res.media))

    plt.figure(figsize=(8, 5))
    for escenario in ("A", "B"):
        serie = sorted(datos[escenario], key=lambda x: x[0])
        x_vals = [x for x, _ in serie]
        y_vals = [y for _, y in serie]
        plt.plot(x_vals, y_vals, marker="o", label=f"Escenario {escenario}")

    plt.xlabel("λ pico (clientes/min)")
    plt.ylabel("% de quejas")
    plt.title("Sensibilidad a λ pico")
    plt.legend()

    _guardar_figura(ruta_salida)


def graficar_sensibilidad_p(resultados: Sequence[ResultadoExperimento], ruta_salida: Path) -> None:
    pares = _mapear_resultados(resultados)
    experimentos = ["E1", "E4", "E5", "E8", "E9"]

    datos = {"A": [], "B": []}
    for nombre in experimentos:
        for escenario in ("A", "B"):
            res = pares[nombre][escenario]
            datos[escenario].append((res.p_sandwich, res.media))

    plt.figure(figsize=(8, 5))
    for escenario in ("A", "B"):
        serie = sorted(datos[escenario], key=lambda x: x[0])
        x_vals = [x for x, _ in serie]
        y_vals = [y for _, y in serie]
        plt.plot(x_vals, y_vals, marker="o", label=f"Escenario {escenario}")

    plt.xlabel("p_sandwich")
    plt.ylabel("% de quejas")
    plt.title("Sensibilidad a la proporción de sándwich")
    plt.legend()

    _guardar_figura(ruta_salida)
