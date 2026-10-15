"""Generador de un dataset academico sintetico para MongoDB.

Proyecto Final - Bases de Datos para IA (ITQ).

Crea cuatro colecciones en formato JSON (Extended JSON de MongoDB):
estudiantes, asignaturas, calificaciones y asistencia.

Reglas del curso (tomadas de la Clase 1):
    - Nota final sobre 10: 3 parciales de 2.2 puntos + proyecto final de 3.4.
    - Cada parcial: 50 % tarea autonoma/practica y 50 % evaluacion.
    - Aprueba con nota final >= 7 y asistencia >= 70 %.

Todos los datos son ficticios (nombres, cedulas y correos inventados).
"""

import json
import random
import unicodedata
from datetime import date, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuracion general
# ---------------------------------------------------------------------------
SEMILLA = 2026  # misma semilla = mismo dataset en cada ejecucion
TOTAL_ESTUDIANTES = 120
PERIODO = "2026-II"
NOTA_MINIMA = 7.0
ASISTENCIA_MINIMA = 70.0
PUNTOS_PARCIAL = 2.2
PUNTOS_PROYECTO = 3.4
CARPETA_SALIDA = Path("data")

PARCIALES = [
    {"numero": 1, "inicio": date(2026, 9, 22), "fin": date(2026, 9, 29)},
    {"numero": 2, "inicio": date(2026, 9, 30), "fin": date(2026, 10, 7)},
    {"numero": 3, "inicio": date(2026, 10, 8), "fin": date(2026, 10, 16)},
]

# dias_clase: 0 = lunes ... 4 = viernes
ASIGNATURAS = [
    {
        "_id": "BDD101",
        "nombre": "Bases de Datos",
        "docente": "Ing. Paola Mendoza",
        "creditos": 4,
        "horas_semana": 4,
        "dias_clase": [0, 2],
    },
    {
        "_id": "PRG102",
        "nombre": "Programacion con Python",
        "docente": "Ing. Marco Salinas",
        "creditos": 4,
        "horas_semana": 4,
        "dias_clase": [1, 3],
    },
    {
        "_id": "MAT103",
        "nombre": "Matematicas para IA",
        "docente": "Mat. Rocio Benalcazar",
        "creditos": 3,
        "horas_semana": 3,
        "dias_clase": [0, 3],
    },
    {
        "_id": "EST104",
        "nombre": "Estadistica Aplicada",
        "docente": "Ing. Hernan Pazmino",
        "creditos": 3,
        "horas_semana": 3,
        "dias_clase": [2, 4],
    },
    {
        "_id": "ING105",
        "nombre": "Ingles Tecnico",
        "docente": "Lic. Sarah Whitmore",
        "creditos": 2,
        "horas_semana": 2,
        "dias_clase": [1, 4],
    },
]

# Ajuste de dificultad por materia (negativo = mas dificil)
DIFICULTAD = {
    "BDD101": -0.3,
    "PRG102": -0.2,
    "MAT103": -0.7,
    "EST104": -0.4,
    "ING105": 0.3,
}

# Hora de clase guardada en UTC (Ecuador = UTC-5)
# Matutina 07:00 -> 12:00Z | Nocturna 18:30 -> 23:30Z
HORA_JORNADA = {"MATUTINA": "12:00:00", "NOCTURNA": "23:30:00"}

CARRERAS = [
    "Desarrollo de Software",
    "Ciencia de Datos e Inteligencia Artificial",
    "Redes y Telecomunicaciones",
]

# (ciudad, codigo de provincia para la cedula, peso)
CIUDADES = [
    ("Quito", "17", 70),
    ("Sangolqui", "17", 8),
    ("Latacunga", "05", 5),
    ("Ibarra", "10", 5),
    ("Ambato", "18", 4),
    ("Guayaquil", "09", 3),
    ("Cuenca", "01", 3),
    ("Riobamba", "06", 2),
]

NOMBRES_F = [
    "Ana", "María", "Lucía", "Valeria", "Camila", "Daniela", "Gabriela",
    "Andrea", "Paola", "Karla", "Sofía", "Fernanda", "Estefanía",
    "Mishell", "Jessica", "Carolina", "Diana", "Alejandra", "Belén",
    "Nicole",
]
NOMBRES_M = [
    "Carlos", "José", "Luis", "Juan", "Andrés", "Diego", "Kevin", "Bryan",
    "Mateo", "Santiago", "David", "Jorge", "Christian", "Fernando",
    "Esteban", "Alexis", "Darwin", "Pablo", "Sebastián", "Ricardo",
]
APELLIDOS = [
    "López", "Pérez", "Torres", "Ruiz", "García", "Andrade", "Chávez",
    "Guerrero", "Vera", "Morales", "Herrera", "Castillo", "Cevallos",
    "Paredes", "Salazar", "Mora", "Jaramillo", "Zambrano", "Villacís",
    "Toapanta", "Quishpe", "Cajas", "Aguirre", "Benítez", "Espinosa",
    "Ortiz", "Proaño", "Suárez", "Valencia", "Yépez",
]


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------
def limitar(valor, minimo, maximo):
    """Devuelve el valor dentro del rango [minimo, maximo]."""
    return max(minimo, min(maximo, valor))


def quitar_tildes(texto):
    """Quita tildes para armar los correos (Jose en lugar de José)."""
    normalizado = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in normalizado if not unicodedata.combining(c))


def fecha_mongo(fecha, hora="00:00:00"):
    """Convierte una fecha al formato Extended JSON que entiende MongoDB."""
    return {"$date": f"{fecha.isoformat()}T{hora}Z"}


def generar_cedula(codigo_provincia):
    """Genera una cedula ecuatoriana ficticia con digito verificador valido."""
    digitos = [int(d) for d in codigo_provincia]
    digitos.append(random.randint(0, 5))  # tercer digito: persona natural
    digitos += [random.randint(0, 9) for _ in range(6)]

    total = 0
    for posicion, digito in enumerate(digitos):
        producto = digito * (2 if posicion % 2 == 0 else 1)
        if producto > 9:
            producto -= 9
        total += producto

    verificador = (10 - total % 10) % 10
    return "".join(str(d) for d in digitos) + str(verificador)


def generar_nota(base, desviacion=0.9):
    """Genera una nota sobre 10 con un decimal."""
    return round(limitar(random.gauss(base, desviacion), 0, 10), 1)


def obtener_parcial(fecha):
    """Indica a que parcial pertenece una fecha de clase."""
    for parcial in PARCIALES:
        if parcial["inicio"] <= fecha <= parcial["fin"]:
            return parcial["numero"]
    return None


def generar_fechas_clase(dias_clase):
    """Lista las fechas de clase de una materia dentro del periodo."""
    fechas = []
    dia = PARCIALES[0]["inicio"]
    while dia <= PARCIALES[-1]["fin"]:
        if dia.weekday() in dias_clase:
            fechas.append(dia)
        dia += timedelta(days=1)
    return fechas


# ---------------------------------------------------------------------------
# Generacion de colecciones
# ---------------------------------------------------------------------------
def generar_estudiantes():
    """Crea la coleccion de estudiantes con su perfil de rendimiento."""
    estudiantes = []
    perfiles = {}
    nombres_usados = set()
    cedulas_usadas = set()
    correos_usados = set()

    ciudades = [c[:2] for c in CIUDADES]
    pesos = [c[2] for c in CIUDADES]

    while len(estudiantes) < TOTAL_ESTUDIANTES:
        genero = random.choice(["F", "M"])
        lista = NOMBRES_F if genero == "F" else NOMBRES_M
        nombres = " ".join(random.sample(lista, 2))
        apellidos = " ".join(random.sample(APELLIDOS, 2))

        if (nombres, apellidos) in nombres_usados:
            continue
        nombres_usados.add((nombres, apellidos))

        ciudad, provincia = random.choices(ciudades, weights=pesos)[0]
        cedula = generar_cedula(provincia)
        while cedula in cedulas_usadas:
            cedula = generar_cedula(provincia)
        cedulas_usadas.add(cedula)

        usuario = quitar_tildes(
            f"{nombres.split()[0]}.{apellidos.split()[0]}"
        ).lower()
        correo = f"{usuario}@estudiante.ejemplo.edu.ec"
        contador = 2
        while correo in correos_usados:
            correo = f"{usuario}{contador}@estudiante.ejemplo.edu.ec"
            contador += 1
        correos_usados.add(correo)

        jornada = random.choices(["MATUTINA", "NOCTURNA"], [55, 45])[0]
        prob_trabaja = 0.70 if jornada == "NOCTURNA" else 0.20
        trabaja = random.random() < prob_trabaja
        edad = random.randint(18, 24) if jornada == "MATUTINA" else \
            random.randint(20, 38)
        nacimiento = date(2026 - edad, random.randint(1, 12),
                          random.randint(1, 28))

        codigo = f"EST-{len(estudiantes) + 1:04d}"
        estudiantes.append({
            "_id": codigo,
            "cedula": cedula,
            "nombres": nombres,
            "apellidos": apellidos,
            "genero": genero,
            "fecha_nacimiento": fecha_mongo(nacimiento),
            "correo": correo,
            "ciudad": ciudad,
            "carrera": random.choice(CARRERAS),
            "jornada": jornada,
            "trabaja": trabaja,
            "periodo": PERIODO,
            "fecha_matricula": fecha_mongo(
                date(2026, 9, random.randint(8, 19))
            ),
        })

        # Perfil oculto: sirve para que notas y asistencia sean coherentes
        en_riesgo = random.random() < 0.12
        if en_riesgo:
            habilidad = random.gauss(6.3, 0.8)
            compromiso = random.gauss(0.70, 0.10)
        else:
            habilidad = random.gauss(8.4, 0.8)
            compromiso = random.gauss(0.90, 0.06)
        if trabaja:
            compromiso -= 0.04

        perfiles[codigo] = {
            "habilidad": limitar(habilidad, 3.5, 9.8),
            "compromiso": limitar(compromiso, 0.40, 0.99),
            "jornada": jornada,
        }

    return estudiantes, perfiles


def generar_asistencia(perfiles):
    """Crea un registro de asistencia por estudiante, materia y clase."""
    asistencia = []
    for asignatura in ASIGNATURAS:
        fechas = generar_fechas_clase(asignatura["dias_clase"])
        for codigo, perfil in perfiles.items():
            for fecha in fechas:
                if random.random() < perfil["compromiso"]:
                    estado = "ATRASO" if random.random() < 0.08 else "PRESENTE"
                else:
                    estado = "AUSENTE"
                asistencia.append({
                    "id_estudiante": codigo,
                    "codigo_asignatura": asignatura["_id"],
                    "parcial": obtener_parcial(fecha),
                    "fecha": fecha_mongo(
                        fecha, HORA_JORNADA[perfil["jornada"]]
                    ),
                    "estado": estado,
                })
    return asistencia


def calcular_porcentajes(asistencia):
    """Calcula el % de asistencia (PRESENTE + ATRASO) por materia."""
    conteo = {}
    for registro in asistencia:
        clave = (registro["id_estudiante"], registro["codigo_asignatura"])
        total, asistidas = conteo.get(clave, (0, 0))
        asistio = registro["estado"] != "AUSENTE"
        conteo[clave] = (total + 1, asistidas + int(asistio))

    return {
        clave: round(asistidas / total * 100, 2)
        for clave, (total, asistidas) in conteo.items()
    }


def generar_calificaciones(perfiles, porcentajes):
    """Crea un documento de calificaciones por estudiante y materia."""
    calificaciones = []
    contador = 1

    for codigo, perfil in perfiles.items():
        for asignatura in ASIGNATURAS:
            codigo_asig = asignatura["_id"]
            pct_asistencia = porcentajes[(codigo, codigo_asig)]

            # Quien falta mas, rinde menos
            base = (perfil["habilidad"] + DIFICULTAD[codigo_asig]
                    + 2.0 * (pct_asistencia / 100 - 0.85))

            parciales = []
            for parcial in PARCIALES:
                # 3 % de probabilidad de no entregar la tarea
                if random.random() < 0.03:
                    tarea = 0.0
                else:
                    tarea = generar_nota(base + 0.4)
                evaluacion = generar_nota(base - 0.2, 1.0)
                puntaje = round((tarea + evaluacion) / 2 / 10 * PUNTOS_PARCIAL,
                                2)
                parciales.append({
                    "parcial": parcial["numero"],
                    "tarea": tarea,
                    "evaluacion": evaluacion,
                    "puntaje": puntaje,
                })

            nota_proyecto = generar_nota(base + 0.3, 0.8)
            puntaje_proyecto = round(nota_proyecto / 10 * PUNTOS_PROYECTO, 2)

            nota_final = round(
                sum(p["puntaje"] for p in parciales) + puntaje_proyecto, 2
            )

            motivos = []
            if nota_final < NOTA_MINIMA:
                motivos.append("NOTA")
            if pct_asistencia < ASISTENCIA_MINIMA:
                motivos.append("ASISTENCIA")

            calificaciones.append({
                "_id": f"CAL-{contador:05d}",
                "id_estudiante": codigo,
                "codigo_asignatura": codigo_asig,
                "periodo": PERIODO,
                "parciales": parciales,
                "proyecto_final": {
                    "nota": nota_proyecto,
                    "puntaje": puntaje_proyecto,
                },
                "nota_final": nota_final,
                "porcentaje_asistencia": pct_asistencia,
                "estado": "REPROBADO" if motivos else "APROBADO",
                "motivo_reprobacion": motivos,
            })
            contador += 1

    return calificaciones


def guardar_json(nombre, datos):
    """Guarda una coleccion como arreglo JSON (listo para mongoimport)."""
    ruta = CARPETA_SALIDA / f"{nombre}.json"
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)
    print(f"  {ruta}: {len(datos)} documentos")


def main():
    """Genera todas las colecciones y las guarda en la carpeta data/."""
    random.seed(SEMILLA)
    CARPETA_SALIDA.mkdir(exist_ok=True)

    estudiantes, perfiles = generar_estudiantes()
    asistencia = generar_asistencia(perfiles)
    porcentajes = calcular_porcentajes(asistencia)
    calificaciones = generar_calificaciones(perfiles, porcentajes)

    asignaturas = [
        {k: v for k, v in a.items() if k != "dias_clase"} | {
            "dias_clase": [
                ["lunes", "martes", "miercoles", "jueves", "viernes"][d]
                for d in a["dias_clase"]
            ],
            "nota_minima": NOTA_MINIMA,
            "asistencia_minima": ASISTENCIA_MINIMA,
        }
        for a in ASIGNATURAS
    ]

    print("Dataset generado:")
    guardar_json("estudiantes", estudiantes)
    guardar_json("asignaturas", asignaturas)
    guardar_json("calificaciones", calificaciones)
    guardar_json("asistencia", asistencia)

    aprobados = sum(1 for c in calificaciones if c["estado"] == "APROBADO")
    print(f"Aprobados: {aprobados} de {len(calificaciones)} registros")


if __name__ == "__main__":
    main()
