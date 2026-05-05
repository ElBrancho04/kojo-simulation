# La Cocina de Kojo — Simulación de Eventos Discretos

Simulación de eventos discretos de un puesto de comida rápida en un centro comercial. El objetivo es comparar dos escenarios operativos y determinar cuál reduce el porcentaje de clientes que esperan más de 5 minutos (tiempo total en el sistema).

## Descripción del problema

La Cocina de Kojo opera de **10:00 AM a 9:00 PM** y sirve dos productos: sándwiches y sushi. El sistema experimenta dos períodos de alta demanda:

- **Pico 1:** 11:30 AM – 1:30 PM
- **Pico 2:** 5:00 PM – 7:00 PM

Se comparan dos escenarios:

| Escenario | Configuración |
|-----------|--------------|
| **A** | 2 empleados fijos durante todo el día |
| **B** | 2 empleados fijos + 1 empleado adicional solo en horas pico |

La **métrica de desempeño** es el porcentaje de clientes cuyo tiempo total en el sistema (espera en cola + preparación del pedido) supera los 5 minutos.

## Estructura del proyecto

```
kojo-simulation/
├── config.py        # Parámetros configurables (λ, p, umbrales, experimentos)
├── model.py         # Entidades: Cliente, Servidor, Evento
├── simulation.py    # Motor de simulación de eventos discretos
├── stats.py         # Análisis estadístico e intervalos de confianza
├── plots.py         # Generación de gráficos y visualizaciones
├── main.py          # Punto de entrada: ejecuta todos los experimentos
├── validation.py    # Validaciones del simulador (Fase de verificación)
├── requirements.txt # Dependencias del proyecto
├── informe_kojo.pdf # Informe completo del proyecto
└── outputs/         # Resultados generados automáticamente
    ├── resultados.csv
    ├── porcentajes.csv
    ├── barras_comparativas.png
    ├── boxplots.png
    ├── reduccion.png
    ├── sensibilidad_lambda.png
    └── sensibilidad_p.png
```

## Requisitos

- Python 3.14.0
- matplotlib >= 3.7

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/ElBrancho04/kojo-simulation.git
cd kojo-simulation

# 2. Crear y activar entorno virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## Uso

### Ejecutar la simulación completa

```bash
python main.py
```

Esto ejecuta los 10 experimentos (1,000 réplicas cada uno) para ambos escenarios A y B, genera todos los gráficos e imprime los resultados en consola. El tiempo de ejecución aproximado es de **30–35 segundos**.

Los resultados se guardan automáticamente en la carpeta `outputs/`.

### Ejecutar las validaciones del simulador

```bash
python validation.py
```

Verifica el correcto funcionamiento del motor: rangos de tiempos de servicio, cambios de λ en cada período, activación del servidor extra y comportamiento al cierre.

### Modificar parámetros

Todos los parámetros configurables se encuentran en `config.py`:

```python
# Tasas de llegada
LAMBDA_NORMAL = 10 / 60   # clientes/minuto fuera de pico
LAMBDA_PICO   = 30 / 60   # clientes/minuto en hora pico

# Proporción de tipos de cliente
P_SANDWICH = 0.50         # probabilidad de pedir sándwich

# Umbral de queja
UMBRAL_ESPERA = 5         # minutos (tiempo total en el sistema)

# Número de réplicas
NUM_REPLICAS = 1000
```

Para agregar o modificar experimentos, editar la lista `EXPERIMENTOS` en `config.py`.

## Modelo de simulación

El sistema implementa una simulación de eventos discretos con los siguientes componentes:

**Eventos:**
- `LLEGADA` — cliente entra al sistema; se le asigna tipo y se encola o atiende
- `FIN_SERVICIO` — empleado termina el pedido; se registra el tiempo total del cliente
- `CAMBIO_PERIODO` — actualiza la tasa λ e activa/desactiva el servidor extra (Escenario B)
- `CIERRE` — detiene las llegadas a las 21:00 y vacía el sistema

**Distribuciones:**
- Tiempo entre llegadas: Exponencial(λ) — distinto por período
- Tiempo de preparación sándwich: Uniforme[3, 5] min
- Tiempo de preparación sushi: Uniforme[5, 8] min

**Cola:** única FIFO, servidores polivalentes (atienden cualquier tipo de pedido).

## Resultados principales

Se ejecutaron 1,000 réplicas por experimento con las mismas semillas aleatorias para ambos escenarios. Todos los intervalos de confianza del 95% entre escenarios A y B son disjuntos, confirmando que las diferencias son estadísticamente significativas.

| Exp. | λ normal | λ pico | p sándwich | Media A | Media B | Reducción |
|------|----------|--------|------------|---------|---------|-----------|
| E1 | 10/h | 30/h | 0.50 | 87.46% | 73.22% | 14.25 pp |
| E2 | 10/h | 40/h | 0.50 | 94.24% | 86.89% | 7.35 pp |
| E3 | 15/h | 30/h | 0.50 | 91.23% | 77.17% | 14.06 pp |
| E4 | 10/h | 30/h | 0.30 | 94.20% | 86.74% | 7.46 pp |
| E5 | 10/h | 30/h | 0.70 | 77.71% | 55.84% | 21.88 pp |
| E6 | 10/h | 50/h | 0.50 | 96.85% | 93.79% | 3.06 pp |
| E7 | 15/h | 40/h | 0.50 | 96.34% | 89.76% | 6.58 pp |
| E8 | 10/h | 30/h | 0.20 | 96.67% | 92.13% | 4.54 pp |
| E9 | 10/h | 30/h | 0.80 | 71.47% | 45.01% | **26.46 pp** |
| E10 | 20/h | 50/h | 0.50 | 98.19% | 97.76% | 0.43 pp |

**Conclusión principal:** el tercer empleado en horas pico siempre reduce el porcentaje de quejas. Su impacto es máximo cuando la mayoría de clientes piden sándwich (servicio más rápido) y mínimo bajo cargas de pico muy altas o carga normal extrema.

## Informe

El informe completo del proyecto está disponible en [`informe_kojo.pdf`](./informe_kojo.pdf). Incluye la descripción formal del modelo, supuestos, diagramas de flujo, análisis estadístico detallado y conclusiones.

## Autor

**Abraham Rey Sánchez Amador** — Grupo C-312  
Facultad de Matemática y Computación, Universidad de La Habana
