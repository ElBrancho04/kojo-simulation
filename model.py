"""Entidades base del modelo de simulación para La Cocina de Kojo."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from typing import Any, Optional


@dataclass
class Cliente:
	"""Representa a un cliente que llega al sistema."""

	id: int
	tipo: str
	tiempo_llegada: float
	tiempo_inicio_servicio: Optional[float] = None
	tiempo_fin_servicio: Optional[float] = None

	def __repr__(self) -> str:
		return (
			"Cliente(id={id}, tipo={tipo}, llegada={llegada:.2f}, "
			"inicio={inicio}, fin={fin})"
		).format(
			id=self.id,
			tipo=self.tipo,
			llegada=self.tiempo_llegada,
			inicio=(None if self.tiempo_inicio_servicio is None else f"{self.tiempo_inicio_servicio:.2f}"),
			fin=(None if self.tiempo_fin_servicio is None else f"{self.tiempo_fin_servicio:.2f}"),
		)


@dataclass
class Servidor:
	"""Representa a un empleado/servidor en el sistema."""

	id: int
	ocupado: bool = False
	activo: bool = True

	def __repr__(self) -> str:
		estado = "ocupado" if self.ocupado else "libre"
		activo = "activo" if self.activo else "inactivo"
		return f"Servidor(id={self.id}, {estado}, {activo})"


_event_counter = count()


def reset_event_counter() -> None:
	"""Reinicia el contador de secuencia de eventos para una nueva réplica."""
	global _event_counter
	_event_counter = count()


@dataclass(order=True)
class Evento:
	"""Evento compatible con heapq (ordenado por tiempo y secuencia)."""

	sort_index: tuple = field(init=False, repr=False)
	tiempo: float
	tipo: str
	datos: Any = field(default=None, compare=False)
	secuencia: int = field(default_factory=lambda: next(_event_counter), compare=False)

	def __post_init__(self) -> None:
		self.sort_index = (self.tiempo, self.secuencia)

	def __repr__(self) -> str:
		return (
			"Evento(tipo={tipo}, tiempo={tiempo:.2f}, sec={sec})"
		).format(tipo=self.tipo, tiempo=self.tiempo, sec=self.secuencia)
