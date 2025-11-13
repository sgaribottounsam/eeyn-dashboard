/*WITH primera_inscripcion AS (
    SELECT e.tipo_y_n_documento, MIN(e.ano_ingreso) AS primer_ingreso
    FROM estudiantes AS e
    GROUP BY e.tipo_y_n_documento
)

SELECT DISTINCT e.tipo_y_n_documento, e.apellido_y_nombre,
    IFNULL(p.origen, 'Revisar') AS origen_preinsc, e.ano_ingreso
    FROM estudiantes AS e
    LEFT JOIN preinscriptos AS p
        ON p.identificacion = e.tipo_y_n_documento
    LEFT JOIN primera_inscripcion AS pi
        ON e.tipo_y_n_documento = pi.tipo_y_n_documento


    WHERE e.ano_ingreso = 2026
        AND pi.primer_ingreso = 2026
        AND origen_preinsc = 'Revisar'*/

WITH primera_inscripcion AS (
            SELECT e.tipo_y_n_documento, MIN(e.ano_ingreso) AS primer_ingreso
            FROM estudiantes AS e
            GROUP BY e.tipo_y_n_documento
        )
        SELECT DISTINCT COUNT(DISTINCT e.tipo_y_n_documento) as cantidad,
            p.codigo as carrera
            FROM estudiantes AS e
            LEFT JOIN primera_inscripcion AS pi
                ON e.tipo_y_n_documento = pi.tipo_y_n_documento
            LEFT JOIN propuestas as p
                ON p.codigo LIKE '%p.carrera%'
            WHERE e.ano_ingreso = 2026
                AND pi.primer_ingreso = e.ano_ingreso
            GROUP BY p.codigo