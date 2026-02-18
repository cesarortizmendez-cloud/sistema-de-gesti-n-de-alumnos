
Sistema de Gestión de Alumnos (SGA) — Tkinter + SQLite + Exportación Excel/PDF

Autor: César Ortiz Méndez 

en esta carpeta encontrarás un .exe el cual puedes copiar en tu escritorio y ejecutar
\SGA.exe

si modificas el código, debes ejecutar el siguiente código en ti cmd y se creará un nuevo .exe 

pyinstaller --noconfirm --clean --onefile --windowed --name SGA main.py



1) Descripción general

El Sistema de Gestión de Alumnos (SGA) es una aplicación de escritorio desarrollada en Python 3 con Tkinter (GUI) y persistencia en SQLite, diseñada para administrar información académica (universidades, carreras, cursos, alumnos, evaluaciones y notas), calcular promedios ponderados y generar reportes exportables a Excel y PDF.

La solución está construida con una arquitectura modular, separando:

Interfaz gráfica (ventanas Tkinter)

Acceso a datos (repositorios repo_*)

Persistencia (SQLite)

Validaciones y manejo de errores

Exportaciones (Excel/PDF)

Registro de actividad (logs)

Esto permite un código mantenible, escalable y consistente con los criterios del módulo.

2) Funcionalidades principales

Gestión académica (CRUD):

Administración de cursos y su contexto académico (universidad/carrera/periodo).

Administración de alumnos.

Administración de evaluaciones por curso (nombre + porcentaje).

Registro de notas por alumno inscrito en un curso.

Cálculo automático de promedio ponderado por alumno en un curso.

Validaciones (ej.: rangos de nota, consistencia de datos, campos obligatorios, etc.).

Exportación de reportes de notas (matriz alumnos × evaluaciones) a:

Excel (.xlsx)

PDF (.pdf)

Registro de actividad: las operaciones relevantes quedan registradas en logs.

3) Aplicaciones de la POO:

3.1 Programación Orientada a Objetos (POO) y estructura escalable

El proyecto mantiene una separación por responsabilidades (UI, repositorios, persistencia, utilitarios), favoreciendo mantenibilidad y escalabilidad.

Se aplica encapsulación y diseño modular para que cada componente tenga un propósito claro y reutilizable, cumpliendo con el enfoque de POO solicitado.



3.2 Persistencia de datos (SQLite + archivos)

La base del sistema es SQLite, usada para almacenamiento seguro y consistente.


La aplicación está diseñada para que la información sea exportable (Excel/PDF) y pueda complementarse con formatos de archivo (según el enunciado se considera JSON/CSV como parte del manejo de datos).



3.3 Interfaz gráfica (Tkinter)

El sistema implementa GUI con Tkinter, con ventanas dedicadas a los módulos principales (cursos, alumnos, evaluaciones y notas).


3.4 Validaciones avanzadas y manejo de errores

Se implementan validaciones (por ejemplo, nota válida, conversiones seguras, manejo de errores al guardar/cargar datos).

Se emplea control de errores para evitar caídas de la aplicación y entregar feedback al usuario (mensajes messagebox).



3.5 Registro de actividad (logs)

Las operaciones críticas (por ejemplo, guardar notas) quedan registradas mediante un repositorio de logs, cumpliendo el requisito de auditoría/registro de actividad.



3.6 Integración con servicios externos (API)

El documento solicita integración con APIs externas (validaciones y notificaciones).



En el sistema SGA, esta capacidad se contempla como una capa integrable (por ejemplo: validar datos académicos externos o enviar notificaciones), manteniendo el diseño modular para incorporar la integración sin alterar el núcleo del sistema.

3.7 Pruebas unitarias

El documento indica la implementación de pruebas unitarias como criterio de validación.



La arquitectura del proyecto (repositorios desacoplados de la UI) permite probar funciones de negocio y acceso a datos de forma aislada.

4) Arquitectura y módulos del proyecto

Nota: los nombres listados corresponden a la estructura modular utilizada en el desarrollo (UI + repositorios + persistencia + utilitarios).

main.py

Punto de entrada del sistema.

Inicializa la base de datos (si aplica) y abre la ventana principal.

modulos/ui_principal.py

Ventana principal (menú/launcher).

Permite abrir las ventanas del sistema: cursos, alumnos, evaluaciones y notas.

modulos/ui_cursos.py

Interfaz para gestionar cursos y su información asociada (universidad, carrera, periodo, código, nombre del curso).

modulos/ui_alumnos.py

Interfaz para gestionar alumnos (alta, edición, eliminación, búsqueda/listado).

modulos/ui_evaluaciones.py

Interfaz para crear evaluaciones asociadas a un curso y asignar sus porcentajes.

Controla la suma de porcentajes y consistencia del esquema de evaluación.

modulos/ui_notas.py

Interfaz de registro y visualización de notas:

Lista de alumnos inscritos en un curso.

Tabla única de evaluaciones con % y Nota.

Edición de nota con “casillas” y con doble click.

Cálculo de promedio ponderado.

Exportación total a Excel y PDF.

modulos/bd_sqlite.py

Capa de persistencia:

Apertura de conexión.

Creación/aseguramiento de tablas/vistas.

Configuración de integridad referencial.

modulos/repo_*

Repositorios de acceso a datos:

repo_cursos.py: consultas y operaciones CRUD para cursos y vistas detalladas.

repo_alumnos.py: CRUD de alumnos.

repo_inscripciones.py: inscripción/desinscripción de alumnos en cursos.

repo_evaluaciones.py: CRUD de evaluaciones y utilitarios (ej. suma de porcentajes).

repo_notas.py: lectura/guardado de notas, promedio ponderado y reporte para exportación.

repo_logs.py: registro de eventos del sistema.

modulos/validaciones.py

Funciones de validación (por ejemplo: validar rango de nota, formato de campos, etc.).

modulos/exportaciones.py

Exportación de reportes completos a:

Excel (.xlsx)

PDF (.pdf)

5) Resumen funcional (explicación de cada función clave)

Este resumen se enfoca en las funciones principales que sostienen la lógica del sistema (las que conectan UI ↔ BD ↔ reportes).

5.1 Repositorio de inscripciones — repo_inscripciones.py

listar_inscritos_por_curso(curso_id)

Obtiene los alumnos inscritos en un curso.

Generalmente incluye métricas calculadas (promedio/suma de porcentajes) para mostrar en pantalla.

inscribir_alumno(alumno_id, curso_id)

Crea la relación alumno–curso (inscripción).

obtener_inscripcion(alumno_id, curso_id)

Verifica si un alumno ya está inscrito en ese curso (evita duplicados).

desinscribir(inscripcion_id)

Elimina una inscripción (y, por integridad, puede eliminar notas asociadas si existe cascada).

5.2 Repositorio de evaluaciones — repo_evaluaciones.py

suma_porcentajes(curso_id)

Suma los porcentajes de las evaluaciones del curso.

Se usa para alertar si el curso no suma 100%.

5.3 Repositorio de notas — repo_notas.py

obtener_notas_por_inscripcion(inscripcion_id)

Devuelve todas las evaluaciones del curso del alumno y su nota actual.

Si aún no existe nota guardada, retorna 0 (para mantener una tabla completa y editable).

guardar_nota(inscripcion_id, evaluacion_id, nota)

Guarda o actualiza una nota.

Aplica validación (rango permitido) y luego realiza UPSERT (update si existe, insert si no).

Registra un log del evento.

obtener_promedio_inscripcion(inscripcion_id)

Lee el promedio ponderado desde una vista/consulta calculada en la base de datos.

obtener_reporte_notas_por_curso(curso_id)

Construye una estructura lista para exportación:

lista de evaluaciones

lista de alumnos con sus notas por evaluación

Permite generar un Excel/PDF con “matriz de notas” completa.

5.4 Exportación — exportaciones.py

exportar_notas_curso_excel(ruta, curso_info, evaluaciones, filas)

Genera un archivo Excel con:

encabezados del curso

columnas por evaluación

filas por alumno

promedio/suma de porcentajes

exportar_notas_curso_pdf(ruta, curso_info, evaluaciones, filas)

Genera un PDF con el mismo contenido lógico del Excel, en formato imprimible.

5.5 Validaciones — validaciones.py

validar_nota(nota)

Verifica que la nota sea numérica y esté dentro del rango permitido.

Si no cumple, lanza un error controlado que la UI muestra al usuario.

5.6 Ventana de notas — ui_notas.py (métodos clave)

_crear_ui()

Crea todos los widgets: Combobox de cursos, tablas, panel de ingreso, botones.

_ajustar_columnas_notas()

Ajusta automáticamente los anchos de columnas para que Evaluación/%/Nota ocupen 1/3 cada una.

_cargar_cursos() y on_curso_change()

Cargan cursos disponibles y actualizan contexto (inscritos, suma de porcentajes, etc.).

on_select_inscrito()

Al seleccionar un alumno inscrito, carga sus evaluaciones y notas.

on_guardar_nota_panel()

Guarda la nota escrita en el panel y recarga tabla para visualizar el valor.

on_doble_click_nota() + _commit_edicion()

Permite editar directamente una celda “Nota” con doble click.

on_recalcular()

Refresca el promedio ponderado desde la BD.

on_exportar_excel() / on_exportar_pdf()

Exporta el reporte completo del curso.

6) Ejecución y compilación (resumen)

Ejecutar en desarrollo:

python main.py

Compilar a .exe (PyInstaller):

pyinstaller --noconfirm --clean --onefile --windowed --name SGA main.py