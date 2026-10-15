# Análisis académico con MongoDB y Python

Proyecto Final — Bases de Datos para la IA (ITQ) · Docente: Michael Israel Guamán Caisaluisa.

Dataset **ficticio** de 120 estudiantes y 5 asignaturas del período 2026-II
(22-sep al 16-oct-2026), cargado en MongoDB y analizado con Python.
Todo el código cumple PEP 8 (verificado con `flake8`).

## Equipo y responsabilidades

| Integrante | Rol | Archivos |
|---|---|---|
| Edgar Crespo | Creación del repositorio y conjunto de datos | `README.md`, `requirements.txt`, `.gitignore`, `generar_dataset.py`, `data/` |
| Edgar Ulloa | Carga en MongoDB y consultas de agregación | `cargar_mongodb.py`, `consultas_mongodb.js` |
| Freddy Guevara | Análisis en Python y visualización | `analisis_academico.ipynb`, `analisis_academico.py`, `graficos/` |

## Estructura

```
proyecto_academico/
├── generar_dataset.py      # crea los JSON de la carpeta data/
├── cargar_mongodb.py       # carga los JSON en MongoDB
├── consultas_mongodb.js    # consultas de agregación para mongosh
├── analisis_academico.ipynb # notebook: consultas + gráficos (entrega principal)
├── analisis_academico.py   # misma lógica como script
├── requirements.txt
├── data/                   # 4 colecciones en Extended JSON
└── graficos/               # PNG generados por el análisis
```

## Reglas de aprobación

| Componente | Puntos | Detalle |
|---|---|---|
| Parcial 1, 2 y 3 | 2,2 c/u | 50 % tarea + 50 % evaluación |
| Proyecto final | 3,4 | Nota sobre 10 escalada a 3,4 |
| **Total** | **10** | Aprueba con **nota ≥ 7** y **asistencia ≥ 70 %** |

## Colecciones

| Colección | Documentos | Contenido |
|---|---|---|
| `estudiantes` | 120 | Cédula, nombres, ciudad, carrera, jornada, si trabaja |
| `asignaturas` | 5 | Código, nombre, docente, créditos, días de clase |
| `calificaciones` | 600 | Parciales, proyecto, nota final, % asistencia, estado |
| `asistencia` | 4 560 | Un registro por clase: PRESENTE, ATRASO o AUSENTE |

Relaciones: `id_estudiante` → `estudiantes._id` y
`codigo_asignatura` → `asignaturas._id`. El atraso cuenta como asistencia.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
python generar_dataset.py       # opcional: regenera data/ (semilla fija)
python cargar_mongodb.py        # carga la base (opcional si usaste Compass)
python analisis_academico.py    # consultas + gráficos en graficos/
```

### Notebook en VS Code

1. Instala las extensiones **Python** y **Jupyter** (Microsoft).
2. Abre `analisis_academico.ipynb`, elige el kernel de Python
   (arriba a la derecha) y pulsa **Run All**.
3. Verifica PEP 8 del notebook: `pip install nbqa flake8` y luego
   `nbqa flake8 analisis_academico.ipynb`.

La conexión se configura con variables de entorno:

| Variable | Valor por defecto |
|---|---|
| `MONGO_URI` | `mongodb://localhost:27017` |
| `MONGO_DB` | `academica` |

Ejemplo con Atlas (PowerShell):

```powershell
$env:MONGO_URI = "mongodb+srv://usuario:clave@cluster.xxxxx.mongodb.net/"
python analisis_academico.py
```

## Análisis y gráficos

| # | Consulta | Técnica de agregación | Gráfico |
|---|---|---|---|
| 1 | Rendimiento por materia | `$group`, `$lookup`, `$unwind` | `1_aprobacion_por_materia.png` |
| 2 | Motivos de reprobación | `$match`, `$group` | `2_motivos_reprobacion.png` |
| 3 | Trabajo y jornada | `$lookup`, `$group` por 2 campos, `$addToSet` | `3_reprobacion_por_perfil.png` |
| 4 | Estudiantes en riesgo | doble `$group` | `4_estudiantes_en_riesgo.png` |
| 5 | Asistencia por parcial | `$group` con `$cond` y `$ne` | `5_asistencia_por_parcial.png` |
| 6 | Asistencia vs. nota | `find` con proyección | `6_asistencia_vs_nota.png` |

## Hallazgos

1. **Matemáticas para IA** es la materia crítica: 61,7 % de aprobación,
   frente a 84,2 % de Inglés Técnico.
2. De 173 reprobaciones, **142 (82 %) se deben a la nota**; 31 estudiantes
   reprobaron solo por asistencia.
3. **Trabajar no redujo el rendimiento**: quienes trabajan reprueban menos
   (22,9–25,1 %) que quienes no trabajan (30,0–33,1 %). Los grupos son
   pequeños y desiguales, así que no se concluye causalidad.
4. **28 estudiantes están en riesgo** (3 o más materias reprobadas);
   14 reprobaron las 5.
5. **La asistencia es estable** entre parciales (84,0 % – 86,7 %).
