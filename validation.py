"""Validaciones del simulador para la Fase 6."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import config
from simulation import simular_dia


def _validar_rangos_servicio(recolector: Dict) -> Tuple[bool, List[str]]:
    errores = []
    for valor in recolector.get("servicio_sandwich", []):
        if not (config.SANDWICH_MIN <= valor <= config.SANDWICH_MAX):
            errores.append(f"Tiempo sándwich fuera de rango: {valor:.2f}")
    for valor in recolector.get("servicio_sushi", []):
        if not (config.SUSHI_MIN <= valor <= config.SUSHI_MAX):
            errores.append(f"Tiempo sushi fuera de rango: {valor:.2f}")
    return len(errores) == 0, errores


def _validar_cambios_lambda(recolector: Dict) -> Tuple[bool, List[str]]:
    esperados = [
        (config.PICO1_INICIO, config.LAMBDA_PICO),
        (config.PICO1_FIN, config.LAMBDA_NORMAL),
        (config.PICO2_INICIO, config.LAMBDA_PICO),
        (config.PICO2_FIN, config.LAMBDA_NORMAL),
    ]
    observados = recolector.get("cambios_lambda", [])
    errores = []

    if len(observados) < len(esperados):
        errores.append("No se registraron todos los cambios de λ.")
    else:
        for (t_exp, l_exp), (t_obs, l_obs) in zip(esperados, observados):
            if t_exp != t_obs or abs(l_exp - l_obs) > 1e-9:
                errores.append(f"Cambio λ esperado en {t_exp} a {l_exp}, observado {t_obs} a {l_obs}")
    return len(errores) == 0, errores


def _validar_extra(recolector: Dict, escenario: str) -> Tuple[bool, List[str]]:
    if escenario.upper() == "A":
        return True, []
    esperados = [
        (config.PICO1_INICIO, True),
        (config.PICO1_FIN, False),
        (config.PICO2_INICIO, True),
        (config.PICO2_FIN, False),
    ]
    observados = recolector.get("cambios_extra", [])
    errores = []
    if len(observados) < len(esperados):
        errores.append("No se registraron todos los cambios del servidor extra.")
    else:
        for (t_exp, a_exp), (t_obs, a_obs) in zip(esperados, observados):
            if t_exp != t_obs or a_exp != a_obs:
                errores.append(f"Cambio extra esperado {t_exp}:{a_exp}, observado {t_obs}:{a_obs}")
    return len(errores) == 0, errores


def _validar_cierre(recolector: Dict) -> Tuple[bool, List[str]]:
    errores = []
    if recolector.get("llegadas_despues_cierre"):
        errores.append("Se detectaron llegadas después del cierre.")
    ultimo_evento = recolector.get("ultimo_evento")
    if ultimo_evento is None or ultimo_evento < config.CIERRE:
        errores.append("El sistema no se vació después del cierre.")
    return len(errores) == 0, errores


def _validar_tiempos(recolector: Dict) -> Tuple[bool, List[str]]:
    if recolector.get("desbalances_tiempo"):
        return False, ["Se detectaron desbalances entre tiempo total y espera+servicio."]
    return True, []


def validar_simulador(
    escenario: str = "A",
    replicas: int = 3,
    debug: bool = True,
    debug_max_eventos: Optional[int] = 200,
) -> None:
    """Ejecuta validaciones básicas con trazas opcionales."""

    print(f"Validación Fase 6 | Escenario {escenario} | Réplicas: {replicas}")
    for i in range(replicas):
        recolector: Dict = {}
        simular_dia(
            escenario=escenario,
            seed=config.SEMILLA + i,
            debug=debug,
            debug_max_eventos=debug_max_eventos,
            recolector=recolector,
        )

        resultados = []
        resultados.append(_validar_rangos_servicio(recolector))
        resultados.append(_validar_cambios_lambda(recolector))
        resultados.append(_validar_extra(recolector, escenario))
        resultados.append(_validar_cierre(recolector))
        resultados.append(_validar_tiempos(recolector))

        errores = [mensaje for ok, msgs in resultados if not ok for mensaje in msgs]
        if errores:
            print(f"Replica {i + 1}: FALLÓ")
            for error in errores:
                print(f"  - {error}")
        else:
            print(f"Replica {i + 1}: OK")


if __name__ == "__main__":
    validar_simulador(escenario="A", replicas=3, debug=True, debug_max_eventos=200)
    validar_simulador(escenario="B", replicas=3, debug=False, debug_max_eventos=200)
