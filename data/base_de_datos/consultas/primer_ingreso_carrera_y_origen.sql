WITH primera_inscripcion AS (
    SELECT e.tipo_y_n_documento, MIN(e.ano_ingreso) AS primer_ingreso
    FROM estudiantes AS e
    GROUP BY e.tipo_y_n_documento
)
/*PRIMER INGRESO*/
/*SELECT DISTINCT COUNT(DISTINCT e.tipo_y_n_documento),
    IIF(pi.primer_ingreso = 2026,
         'Primer Ingreso',
         'Tiene un ingreso anterior'
        
     ) AS primera_carrera
    FROM estudiantes AS e
    LEFT JOIN preinscriptos AS p
        ON p.identificacion = e.tipo_y_n_documento
    LEFT JOIN primera_inscripcion AS pi
        ON e.tipo_y_n_documento = pi.tipo_y_n_documento
    WHERE e.ano_ingreso = 2026
    GROUP BY primera_carrera*/



/*ORIGEN*/
/*SELECT DISTINCT COUNT(DISTINCT e.tipo_y_n_documento),
    IIF(pi.primer_ingreso < 2026, 'Homologación',
       IFNULL(p.origen, 'Revisar')
     ) AS origen_preinsc
    FROM estudiantes AS e
    LEFT JOIN preinscriptos AS p
        ON p.identificacion = e.tipo_y_n_documento
    LEFT JOIN primera_inscripcion AS pi
        ON e.tipo_y_n_documento = pi.tipo_y_n_documento
    WHERE e.ano_ingreso = 2026
    GROUP BY origen_preinsc
*/

/*CARRERA*/
/*SELECT DISTINCT COUNT(DISTINCT e.tipo_y_n_documento),
    substr(e.carrera,2, 9) as codigo_carrera, propuestas.tipo
    FROM estudiantes AS e
    LEFT JOIN preinscriptos AS p
        ON p.identificacion = e.tipo_y_n_documento
    LEFT JOIN primera_inscripcion AS pi
        ON e.tipo_y_n_documento = pi.tipo_y_n_documento
    LEFT JOIN propuestas
        ON (propuestas.codigo = codigo_carrera
        OR propuestas.codigo = CONCAT(codigo_carrera, 'P'))
    WHERE e.ano_ingreso = 2026
        AND pi.primer_ingreso = 2026
    GROUP BY codigo_carrera*/

/*HISTÓRICO DE PRIMEROS INGRESOS*/
/*SELECT DISTINCT COUNT(DISTINCT e.tipo_y_n_documento),
    substr(e.carrera,2, 9) as codigo_carrera, propuestas.tipo
    FROM estudiantes AS e
    LEFT JOIN preinscriptos AS p
        ON p.identificacion = e.tipo_y_n_documento
    LEFT JOIN primera_inscripcion AS pi
        ON e.tipo_y_n_documento = pi.tipo_y_n_documento
    LEFT JOIN propuestas
        ON (propuestas.codigo = codigo_carrera
        OR propuestas.codigo = CONCAT(codigo_carrera, 'P'))
    WHERE e.ano_ingreso > 2021
        AND pi.primer_ingreso = e.ano_ingreso
    GROUP BY codigo_carrera, e.ano_ingreso*/


/*CON MÁS DE UNA CARRERA*/
/*SELECT  cantidad_carreras, COUNT(*) AS cantidad_estudiantes_con_mas_de_una_carrera
FROM (
    SELECT e.tipo_y_n_documento, COUNT(DISTINCT e.carrera) AS cantidad_carreras
        FROM estudiantes AS e
        LEFT JOIN preinscriptos AS p
            ON p.identificacion = e.tipo_y_n_documento
        LEFT JOIN primera_inscripcion AS pi
            ON e.tipo_y_n_documento = pi.tipo_y_n_documento
        LEFT JOIN propuestas
            ON propuestas.codigo = substr(e.carrera, 2, 9)
        WHERE e.ano_ingreso = 2026
            AND pi.primer_ingreso = 2026
        GROUP BY e.tipo_y_n_documento
        
)
GROUP BY cantidad_carreras*/

/*HOMOLOGACIONES*/
SELECT e.ano_ingreso, COUNT(DISTINCT e.tipo_y_n_documento),
    substr(e.carrera,2, 9) as codigo_carrera, propuestas.tipo
    FROM estudiantes AS e
    LEFT JOIN preinscriptos AS p
        ON p.identificacion = e.tipo_y_n_documento
    LEFT JOIN primera_inscripcion AS pi
        ON e.tipo_y_n_documento = pi.tipo_y_n_documento
    LEFT JOIN propuestas
        ON (propuestas.codigo = codigo_carrera
        OR propuestas.codigo = CONCAT(codigo_carrera, 'P'))
    WHERE e.ano_ingreso > 2021
        AND pi.primer_ingreso < e.ano_ingreso
    GROUP BY codigo_carrera, e.ano_ingreso