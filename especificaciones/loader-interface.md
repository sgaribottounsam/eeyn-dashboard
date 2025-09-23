Especificación Funcional: Interfaz de Carga de Datos Académicos
1. Objetivo

Crear una aplicación web simple y segura que permita a un asistente administrativo cargar nuevos reportes de inscripciones a cursadas en la base de datos academica.db. La herramienta debe ser intuitiva y guiar al usuario a través del proceso, proporcionando una respuesta clara sobre el resultado de la carga.
2. Herramienta Recomendada: Streamlit

Para esta tarea específica, recomiendo utilizar Streamlit.

    ¿Por qué Streamlit y no Dash? Mientras que Dash es excelente para dashboards de visualización complejos, Streamlit brilla por su simplicidad y velocidad de desarrollo para herramientas internas y aplicaciones orientadas a procesos. La cantidad de código necesaria para construir esta interfaz en Streamlit será significativamente menor y más fácil de mantener que su equivalente en Dash. Podemos crear un script admin_uploader.py completamente separado de tu proyecto de dashboard.

3. Especificaciones Funcionales (La Interfaz)

La interfaz de usuario será una única página con los siguientes componentes, en orden:

    Título Principal: "Herramienta de Carga de Datos Académicos"

    Paso 1: Tipo de Importación

        Componente: Un menú desplegable (select box).

        Etiqueta: "Seleccionar tipo de importación:"

        Opciones:

            "Inscripciones a Cursadas" (por ahora, la única opción habilitada).

            (Futuro) "Inscripciones a Carreras", "Egresados", etc.

    Paso 2: Período Lectivo

        Componente: Un menú desplegable (select box).

        Etiqueta: "Seleccionar período lectivo:"

        Lógica: La lista de opciones se debe generar dinámicamente en el script. Debe crear una lista de strings desde 2010-1, 2010-2, 2010-3 hasta el año actual + 1 (para permitir cargas futuras). Por ejemplo: 2024-1, 2024-2, 2024-3, 2025-1, etc.

    Paso 3: Cargar Archivo

        Componente: Un cargador de archivos (file uploader).

        Etiqueta: "Cargar el archivo Excel de inscripciones:"

        Validación: El componente debe aceptar únicamente archivos con extensión .xlsx.

    Paso 4: Ejecutar Proceso

        Componente: Un botón (button).

        Etiqueta: "Procesar y Cargar Datos"

    Paso 5: Área de Resultados

        Componente: Un bloque de texto o un cuadro de mensaje.

        Comportamiento: Inicialmente estará vacío. Después de hacer clic en el botón, aquí se mostrará el resultado del proceso.

4. Flujo de Usuario

    El asistente abre la aplicación.

    Selecciona "Inscripciones a Cursadas".

    Selecciona el período lectivo correspondiente al reporte, por ejemplo, "2025-2".

    Arrastra o selecciona el archivo .xlsx descargado del sistema.

    Hace clic en "Procesar y Cargar Datos".

    La aplicación muestra un indicador de "Procesando...".

    Al finalizar, el área de resultados muestra un mensaje de éxito, por ejemplo: "¡Éxito! Se procesaron y reemplazaron 13,241 filas para el período 2025-2." o un mensaje de error si algo falló
    
    5. Lógica del Backend (Lo que pasa por detrás)

    Cuando el asistente hace clic en el botón "Procesar y Cargar Datos", el script de Streamlit (admin_uploader.py) ejecutará la siguiente secuencia de acciones:

    Validación de Entradas:

        Verifica que el usuario haya seleccionado un tipo de importación.

        Verifica que se haya seleccionado un período lectivo.

        Verifica que se haya subido un archivo.

        Si alguna validación falla, muestra un mensaje de error claro y detiene el proceso.

    Manejo del Archivo Subido:

        Toma el archivo .xlsx subido por el usuario.

        Lo guarda temporalmente en la carpeta de datos crudos (data/crudos/). El nombre del archivo podría ser estandarizado, por ejemplo inscripciones_temp.xlsx.

    Ejecución del Script Limpiador:

        Modificación necesaria: Se deberá modificar el script limpiador_inscripciones.py para que acepte el período lectivo y la ruta del archivo de entrada como argumentos de línea de comandos, en lugar de tenerlos fijos en el código.

        El script de Streamlit llamará al limpiador como un subproceso, pasándole los parámetros necesarios. Ejemplo: python limpiadores/limpiador_inscripciones.py --periodo 2025-2 --archivo data/crudos/inscripciones_temp.xlsx.

        Capturará la salida de la terminal del limpiador para monitorear el progreso y verificar si tuvo éxito.

    Ejecución del Script Importador:

        Si el limpiador se ejecutó sin errores, el script de Streamlit procederá a llamar al importador importador_inscripciones.py.

        Modificación necesaria: Este script también deberá ser modificado para aceptar la ruta del archivo CSV procesado como argumento.

        Capturará la salida de la terminal del importador para obtener la cantidad de filas insertadas o reemplazadas.

    Reporte de Resultados:

        Basado en la salida de los scripts, mostrará un mensaje final en el "Área de Resultados" de la interfaz.

            Éxito: "¡Proceso completado! Se importaron X registros para el período Y."

            Error: "Ocurrió un error durante la limpieza de datos: [mensaje de error del script]".

    Limpieza:

        Eliminará el archivo temporal (inscripciones_temp.xlsx) de la carpeta data/crudos/ para no dejar archivos basura.