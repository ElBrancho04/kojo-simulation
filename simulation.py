"""Motor de simulación de eventos discretos para La Cocina de Kojo."""

from __future__ import annotations

import heapq
import random
from collections import deque
from typing import Deque, Dict, List, Optional

import config
from model import Cliente, Evento, Servidor, reset_event_counter

LLEGADA = "LLEGADA"
FIN_SERVICIO = "FIN_SERVICIO"
CAMBIO_PERIODO = "CAMBIO_PERIODO"
CIERRE = "CIERRE"


def _interarribo(lambda_actual: float, rng: random.Random) -> float:
	if lambda_actual <= 0:
		return float("inf")
	return rng.expovariate(lambda_actual)


def _tipo_cliente(p_sandwich: float, rng: random.Random) -> str:
	return "sandwich" if rng.random() < p_sandwich else "sushi"


def _tiempo_servicio(tipo: str, rng: random.Random) -> float:
	if tipo == "sandwich":
		return rng.uniform(config.SANDWICH_MIN, config.SANDWICH_MAX)
	return rng.uniform(config.SUSHI_MIN, config.SUSHI_MAX)


def _programar_evento(eventos: List[Evento], tipo: str, tiempo: float, datos: Optional[dict] = None) -> None:
	heapq.heappush(eventos, Evento(tipo=tipo, tiempo=tiempo, datos=datos or {}))


def _obtener_servidor_libre(servidores: List[Servidor]) -> Optional[Servidor]:
	for servidor in servidores:
		if servidor.activo and not servidor.ocupado:
			return servidor
	return None


def _iniciar_servicio(
	cliente: Cliente,
	servidor: Servidor,
	tiempo_actual: float,
	eventos: List[Evento],
	rng: random.Random,
	recolector: Optional[Dict] = None,
) -> None:
	servidor.ocupado = True
	cliente.tiempo_inicio_servicio = tiempo_actual
	tiempo_servicio = _tiempo_servicio(cliente.tipo, rng)
	cliente.tiempo_fin_servicio = tiempo_actual + tiempo_servicio
	if recolector is not None:
		if cliente.tipo == "sandwich":
			recolector.setdefault("servicio_sandwich", []).append(tiempo_servicio)
		else:
			recolector.setdefault("servicio_sushi", []).append(tiempo_servicio)
	_programar_evento(
		eventos,
		FIN_SERVICIO,
		cliente.tiempo_fin_servicio,
		{"cliente": cliente, "servidor": servidor},
	)


def simular_dia(
	escenario: str = "A",
	lambda_normal: float = config.LAMBDA_NORMAL,
	lambda_pico: float = config.LAMBDA_PICO,
	p_sandwich: float = config.P_SANDWICH,
	seed: Optional[int] = None,
	debug: bool = False,
	debug_max_eventos: Optional[int] = None,
	recolector: Optional[Dict] = None,
) -> List[float]:
	"""Simula un día de trabajo y retorna los tiempos totales por cliente."""

	rng = random.Random(seed)
	tiempos_totales: List[float] = []
	cola: Deque[Cliente] = deque()
	eventos: List[Evento] = []
	lambda_actual = lambda_normal
	cierre_activo = False
	cliente_id = 0
	contador_eventos = 0
	tiempo_actual = 0.0

	if recolector is None:
		recolector = {}

	recolector.setdefault("servicio_sandwich", [])
	recolector.setdefault("servicio_sushi", [])
	recolector.setdefault("cambios_lambda", [])
	recolector.setdefault("cambios_extra", [])
	recolector.setdefault("llegadas_despues_cierre", [])
	recolector.setdefault("desbalances_tiempo", [])

	reset_event_counter()

	def log_evento(mensaje: str) -> None:
		if not debug:
			return
		if debug_max_eventos is not None and contador_eventos >= debug_max_eventos:
			return
		print(mensaje)

	servidores: List[Servidor] = [Servidor(id=1), Servidor(id=2)]
	servidor_extra = None
	if escenario.upper() == "B":
		servidor_extra = Servidor(id=3, activo=False)
		servidores.append(servidor_extra)

	_programar_evento(eventos, CAMBIO_PERIODO, config.PICO1_INICIO, {"lambda": lambda_pico, "activar_extra": True})
	_programar_evento(eventos, CAMBIO_PERIODO, config.PICO1_FIN, {"lambda": lambda_normal, "activar_extra": False})
	_programar_evento(eventos, CAMBIO_PERIODO, config.PICO2_INICIO, {"lambda": lambda_pico, "activar_extra": True})
	_programar_evento(eventos, CAMBIO_PERIODO, config.PICO2_FIN, {"lambda": lambda_normal, "activar_extra": False})
	_programar_evento(eventos, CIERRE, config.CIERRE, {})

	primera_llegada = config.APERTURA + _interarribo(lambda_actual, rng)
	if primera_llegada <= config.CIERRE:
		_programar_evento(eventos, LLEGADA, primera_llegada, {})

	while eventos:
		evento = heapq.heappop(eventos)
		tiempo_actual = evento.tiempo
		datos = evento.datos
		contador_eventos += 1

		if debug:
			estados = ", ".join(
				f"S{srv.id}:{'O' if srv.ocupado else 'L'}:{'A' if srv.activo else 'I'}"
				for srv in servidores
			)
			log_evento(
				f"t={tiempo_actual:.2f} | {evento.tipo} | cola={len(cola)} | {estados}"
			)

		if evento.tipo == LLEGADA:
			if cierre_activo or tiempo_actual > config.CIERRE:
				recolector["llegadas_despues_cierre"].append(tiempo_actual)
				continue

			cliente_id += 1
			tipo = _tipo_cliente(p_sandwich, rng)
			cliente = Cliente(id=cliente_id, tipo=tipo, tiempo_llegada=tiempo_actual)

			servidor_libre = _obtener_servidor_libre(servidores)
			if servidor_libre:
				_iniciar_servicio(cliente, servidor_libre, tiempo_actual, eventos, rng, recolector)
			else:
				cola.append(cliente)

			siguiente_llegada = tiempo_actual + _interarribo(lambda_actual, rng)
			if siguiente_llegada <= config.CIERRE:
				_programar_evento(eventos, LLEGADA, siguiente_llegada, {})

		elif evento.tipo == FIN_SERVICIO:
			cliente = datos["cliente"]
			servidor = datos["servidor"]
			servidor.ocupado = False
			tiempo_total = cliente.tiempo_fin_servicio - cliente.tiempo_llegada
			tiempos_totales.append(tiempo_total)

			tiempo_espera = cliente.tiempo_inicio_servicio - cliente.tiempo_llegada
			tiempo_servicio = cliente.tiempo_fin_servicio - cliente.tiempo_inicio_servicio
			diferencia = abs(tiempo_total - (tiempo_espera + tiempo_servicio))
			if diferencia > 1e-9:
				recolector["desbalances_tiempo"].append(
					{
						"id": cliente.id,
						"diferencia": diferencia,
					}
				)

			if servidor.activo and cola:
				siguiente_cliente = cola.popleft()
				_iniciar_servicio(siguiente_cliente, servidor, tiempo_actual, eventos, rng, recolector)

		elif evento.tipo == CAMBIO_PERIODO:
			lambda_actual = datos["lambda"]
			recolector["cambios_lambda"].append((tiempo_actual, lambda_actual))

			if servidor_extra is not None:
				activar = datos["activar_extra"]
				if activar:
					servidor_extra.activo = True
					recolector["cambios_extra"].append((tiempo_actual, True))
					if not servidor_extra.ocupado and cola:
						siguiente_cliente = cola.popleft()
						_iniciar_servicio(siguiente_cliente, servidor_extra, tiempo_actual, eventos, rng, recolector)
				else:
					servidor_extra.activo = False
					recolector["cambios_extra"].append((tiempo_actual, False))

		elif evento.tipo == CIERRE:
			cierre_activo = True
			recolector["cierre"] = tiempo_actual

	recolector["ultimo_evento"] = tiempo_actual

	return tiempos_totales


if __name__ == "__main__":
	tiempos = simular_dia(seed=config.SEMILLA)
	if tiempos:
		promedio = sum(tiempos) / len(tiempos)
		print(f"Clientes atendidos: {len(tiempos)} | Tiempo total promedio: {promedio:.2f} min")
