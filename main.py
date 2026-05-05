"""Punto de entrada para ejecutar los experimentos de Kojo."""

from __future__ import annotations

import csv
import random
import time
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import config
from simulation import simular_dia
from plots import (
	graficar_barras_comparativas,
	graficar_boxplots,
	graficar_reduccion,
	graficar_sensibilidad_lambda,
	graficar_sensibilidad_p,
)
from stats import ResultadoExperimento, imprimir_tabla_comparativa, resumir_experimento


def generar_semillas(num_replicas: int, semilla_base: int) -> List[int]:
	"""Genera una lista de semillas reproducibles para las réplicas."""

	rng = random.Random(semilla_base)
	return [rng.randrange(1_000_000_000) for _ in range(num_replicas)]


def ejecutar_experimento(
	nombre: str,
	escenario: str,
	lambda_normal: float,
	lambda_pico: float,
	p_sandwich: float,
	semillas: Sequence[int],
) -> ResultadoExperimento:
	"""Ejecuta las réplicas de un experimento y resume resultados."""

	replicas_tiempos: List[List[float]] = []
	for seed in semillas:
		tiempos = simular_dia(
			escenario=escenario,
			lambda_normal=lambda_normal,
			lambda_pico=lambda_pico,
			p_sandwich=p_sandwich,
			seed=seed,
		)
		replicas_tiempos.append(tiempos)
	return resumir_experimento(
		nombre,
		escenario,
		lambda_normal,
		lambda_pico,
		p_sandwich,
		replicas_tiempos,
	)


def ejecutar_experimentos(
	experimentos: Iterable[dict],
	num_replicas: int = config.NUM_REPLICAS,
	semilla_base: int = config.SEMILLA,
) -> List[ResultadoExperimento]:
	"""Ejecuta todos los experimentos para escenarios A y B."""

	semillas = generar_semillas(num_replicas, semilla_base)
	resultados: List[ResultadoExperimento] = []

	for exp in experimentos:
		nombre = exp["nombre"]
		lambda_normal = exp["lambda_normal"]
		lambda_pico = exp["lambda_pico"]
		p_sandwich = exp["p_sandwich"]

		resultados.append(
			ejecutar_experimento(
				nombre,
				"A",
				lambda_normal,
				lambda_pico,
				p_sandwich,
				semillas,
			)
		)
		resultados.append(
			ejecutar_experimento(
				nombre,
				"B",
				lambda_normal,
				lambda_pico,
				p_sandwich,
				semillas,
			)
		)

	return resultados


def exportar_csv(resultados: Sequence[ResultadoExperimento], ruta: Path) -> None:
	"""Exporta resultados a un archivo CSV."""

	pares = _emparejar_resultados(resultados)
	ruta.parent.mkdir(parents=True, exist_ok=True)
	with ruta.open("w", newline="", encoding="utf-8") as archivo:
		writer = csv.writer(archivo)
		writer.writerow(
			[
				"experimento",
				"escenario",
				"n",
				"media",
				"ic_inferior",
				"ic_superior",
				"reduccion_absoluta",
				"reduccion_relativa",
			]
		)
		for res in resultados:
			reduccion_abs, reduccion_rel = _obtener_reducciones(pares, res.nombre)
			writer.writerow(
				[
					res.nombre,
					res.escenario,
					res.n,
					f"{res.media:.6f}",
					"" if res.ic_inferior is None else f"{res.ic_inferior:.6f}",
					"" if res.ic_superior is None else f"{res.ic_superior:.6f}",
					"" if reduccion_abs is None else f"{reduccion_abs:.6f}",
					"" if reduccion_rel is None else f"{reduccion_rel:.6f}",
				]
			)


def exportar_porcentajes_csv(resultados: Sequence[ResultadoExperimento], ruta: Path) -> None:
	"""Exporta los porcentajes diarios por réplica a CSV."""

	ruta.parent.mkdir(parents=True, exist_ok=True)
	with ruta.open("w", newline="", encoding="utf-8") as archivo:
		writer = csv.writer(archivo)
		writer.writerow(["experimento", "escenario", "replica", "porcentaje"])
		for res in resultados:
			for idx, porcentaje in enumerate(res.porcentajes, start=1):
				writer.writerow([res.nombre, res.escenario, idx, f"{porcentaje:.6f}"])


def _emparejar_resultados(
	resultados: Sequence[ResultadoExperimento],
) -> dict:
	pares = {}
	for res in resultados:
		pares.setdefault(res.nombre, {})[res.escenario] = res
	return pares


def _obtener_reducciones(pares: dict, nombre: str) -> Tuple[Optional[float], Optional[float]]:
	res_a = pares.get(nombre, {}).get("A")
	res_b = pares.get(nombre, {}).get("B")
	if not res_a or not res_b:
		return None, None
	reduccion_abs = res_a.media - res_b.media
	reduccion_rel = (reduccion_abs / res_a.media * 100) if res_a.media != 0 else 0.0
	return reduccion_abs, reduccion_rel


def imprimir_resumen(resultados: Sequence[ResultadoExperimento]) -> None:
	"""Imprime un resumen en consola."""

	for res in resultados:
		ic = (
			"N/A"
			if res.ic_inferior is None or res.ic_superior is None
			else f"[{res.ic_inferior:.2f}, {res.ic_superior:.2f}]"
		)
		print(
			f"{res.nombre} | Escenario {res.escenario} | "
			f"Media={res.media:.2f}% | IC95%={ic} | n={res.n}"
		)


def main() -> None:
	inicio = time.perf_counter()
	resultados = ejecutar_experimentos(config.EXPERIMENTOS)
	exportar_csv(resultados, Path("outputs") / "resultados.csv")
	exportar_porcentajes_csv(resultados, Path("outputs") / "porcentajes.csv")
	imprimir_resumen(resultados)
	imprimir_tabla_comparativa(resultados)

	graficar_barras_comparativas(resultados, Path("outputs") / "barras_comparativas.png")
	graficar_boxplots(resultados, Path("outputs") / "boxplots.png")
	graficar_reduccion(resultados, Path("outputs") / "reduccion.png")
	graficar_sensibilidad_lambda(resultados, Path("outputs") / "sensibilidad_lambda.png")
	graficar_sensibilidad_p(resultados, Path("outputs") / "sensibilidad_p.png")

	duracion = time.perf_counter() - inicio
	print(f"Tiempo total de ejecución: {duracion:.2f} s")


if __name__ == "__main__":
	main()
