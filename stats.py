"""Recolección y análisis estadístico de la simulación de Kojo."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import NormalDist, mean, stdev
from typing import Iterable, List, Optional, Sequence

import config
from model import Cliente


_T_CRITICO_975 = {
	1: 12.706,
	2: 4.303,
	3: 3.182,
	4: 2.776,
	5: 2.571,
	6: 2.447,
	7: 2.365,
	8: 2.306,
	9: 2.262,
	10: 2.228,
	11: 2.201,
	12: 2.179,
	13: 2.160,
	14: 2.145,
	15: 2.131,
	16: 2.120,
	17: 2.110,
	18: 2.101,
	19: 2.093,
	20: 2.086,
	21: 2.080,
	22: 2.074,
	23: 2.069,
	24: 2.064,
	25: 2.060,
	26: 2.056,
	27: 2.052,
	28: 2.048,
	29: 2.045,
	30: 2.042,
}


def extraer_tiempos_totales(clientes: Iterable[Cliente]) -> List[float]:
	"""Calcula el tiempo total por cliente: fin_servicio - llegada."""

	tiempos = []
	for cliente in clientes:
		if cliente.tiempo_fin_servicio is None:
			continue
		tiempos.append(cliente.tiempo_fin_servicio - cliente.tiempo_llegada)
	return tiempos


def porcentaje_quejas(tiempos: Sequence[float], umbral: float = config.UMBRAL_ESPERA) -> float:
	"""Calcula el porcentaje de clientes con tiempo total > umbral."""

	total = len(tiempos)
	if total == 0:
		return 0.0
	quejas = sum(1 for t in tiempos if t > umbral)
	return (quejas / total) * 100.0


def porcentajes_por_replicas(
	replicas: Sequence[Sequence[float]],
	umbral: float = config.UMBRAL_ESPERA,
) -> List[float]:
	"""Convierte una lista de réplicas en % de quejas por réplica."""

	return [porcentaje_quejas(replica, umbral) for replica in replicas]


def _t_critico(confianza: float, df: int) -> float:
	"""Devuelve el valor crítico t de Student para un nivel de confianza."""

	if df <= 0:
		return float("nan")
	if abs(confianza - 0.95) < 1e-9:
		if df in _T_CRITICO_975:
			return _T_CRITICO_975[df]
	z = NormalDist().inv_cdf(0.5 + confianza / 2)
	return z


def media_intervalo_confianza(
	datos: Sequence[float],
	confianza: float = 0.95,
) -> tuple[float, Optional[float], Optional[float]]:
	"""Calcula media e intervalo de confianza al 95% (t-Student)."""

	n = len(datos)
	if n == 0:
		return 0.0, None, None
	promedio = mean(datos)
	if n < 2:
		return promedio, None, None
	desviacion = stdev(datos)
	error_estandar = desviacion / (n ** 0.5)
	t_crit = _t_critico(confianza, n - 1)
	margen = t_crit * error_estandar
	return promedio, promedio - margen, promedio + margen


@dataclass
class ResultadoExperimento:
	nombre: str
	escenario: str
	porcentajes: List[float]
	media: float
	ic_inferior: Optional[float]
	ic_superior: Optional[float]
	n: int


def resumir_experimento(
	nombre: str,
	escenario: str,
	replicas_tiempos: Sequence[Sequence[float]],
	umbral: float = config.UMBRAL_ESPERA,
	confianza: float = 0.95,
) -> ResultadoExperimento:
	"""Genera el resumen estadístico de un experimento."""

	porcentajes = porcentajes_por_replicas(replicas_tiempos, umbral)
	promedio, ic_inf, ic_sup = media_intervalo_confianza(porcentajes, confianza)
	return ResultadoExperimento(
		nombre=nombre,
		escenario=escenario,
		porcentajes=porcentajes,
		media=promedio,
		ic_inferior=ic_inf,
		ic_superior=ic_sup,
		n=len(porcentajes),
	)


if __name__ == "__main__":
	ejemplo = [
		[2.0, 6.0, 7.5, 3.2],
		[1.0, 4.5, 8.0, 6.2, 3.0],
		[9.0, 2.5, 5.1],
	]
	resultado = resumir_experimento("E_demo", "A", ejemplo)
	print(resultado)
