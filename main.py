"""Punto de entrada para ejecutar los experimentos de Kojo."""

from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Iterable, List, Sequence

import config
from simulation import simular_dia
from stats import ResultadoExperimento, resumir_experimento


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
	return resumir_experimento(nombre, escenario, replicas_tiempos)


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
			]
		)
		for res in resultados:
			writer.writerow(
				[
					res.nombre,
					res.escenario,
					res.n,
					f"{res.media:.6f}",
					"" if res.ic_inferior is None else f"{res.ic_inferior:.6f}",
					"" if res.ic_superior is None else f"{res.ic_superior:.6f}",
				]
			)


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
	resultados = ejecutar_experimentos(config.EXPERIMENTOS)
	exportar_csv(resultados, Path("outputs") / "resultados.csv")
	imprimir_resumen(resultados)


if __name__ == "__main__":
	main()
