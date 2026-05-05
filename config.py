# config.py
# ============================================================
# Parámetros configurables de la simulación
# La Cocina de Kojo
# ============================================================

# --- Horario del local (en minutos desde las 10:00 AM) ---
APERTURA        = 0       # 10:00 AM
CIERRE          = 660     # 21:00 PM (11 horas = 660 minutos)

# --- Períodos pico (en minutos desde las 10:00 AM) ---
PICO1_INICIO    = 90      # 11:30 AM
PICO1_FIN       = 210     # 01:30 PM
PICO2_INICIO    = 420     # 05:00 PM
PICO2_FIN       = 540     # 07:00 PM

# --- Tasas de llegada (clientes por minuto) ---
LAMBDA_NORMAL   = 10 / 60   # 10 clientes/hora fuera de pico
LAMBDA_PICO     = 30 / 60   # 30 clientes/hora en pico

# --- Proporción de tipos de cliente ---
# p = probabilidad de que un cliente pida sándwich
# (1 - p) = probabilidad de que pida sushi
P_SANDWICH      = 0.50

# --- Tiempos de servicio (distribución uniforme, en minutos) ---
SANDWICH_MIN    = 3
SANDWICH_MAX    = 5
SUSHI_MIN       = 5
SUSHI_MAX       = 8

# --- Umbral de queja (en minutos) ---
UMBRAL_ESPERA   = 5       # Tiempo total (cola + preparación)

# --- Configuración de la simulación ---
NUM_REPLICAS    = 1000
SEMILLA         = 42      # Para reproducibilidad

# --- Matriz de experimentos ---
EXPERIMENTOS = [
    {"nombre": "E1", "lambda_normal": 10/60, "lambda_pico": 30/60, "p_sandwich": 0.50},
    {"nombre": "E2", "lambda_normal": 10/60, "lambda_pico": 40/60, "p_sandwich": 0.50},
    {"nombre": "E3", "lambda_normal": 15/60, "lambda_pico": 30/60, "p_sandwich": 0.50},
    {"nombre": "E4", "lambda_normal": 10/60, "lambda_pico": 30/60, "p_sandwich": 0.30},
    {"nombre": "E5", "lambda_normal": 10/60, "lambda_pico": 30/60, "p_sandwich": 0.70},
    {"nombre": "E6", "lambda_normal": 10/60, "lambda_pico": 50/60, "p_sandwich": 0.50},
    {"nombre": "E7", "lambda_normal": 15/60, "lambda_pico": 40/60, "p_sandwich": 0.50},
    {"nombre": "E8", "lambda_normal": 10/60, "lambda_pico": 30/60, "p_sandwich": 0.20},
    {"nombre": "E9", "lambda_normal": 10/60, "lambda_pico": 30/60, "p_sandwich": 0.80},
    {"nombre": "E10", "lambda_normal": 20/60, "lambda_pico": 50/60, "p_sandwich": 0.50},
]