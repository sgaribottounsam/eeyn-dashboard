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
    GROUP BY primera_carrera
*/


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
    substr(e.carrera,2, 9) as carrera
    FROM estudiantes AS e
    LEFT JOIN preinscriptos AS p
        ON p.identificacion = e.tipo_y_n_documento
    LEFT JOIN primera_inscripcion AS pi
        ON e.tipo_y_n_documento = pi.tipo_y_n_documento
    WHERE e.ano_ingreso = 2026
        AND pi.primer_ingreso = 2026
    GROUP BY e.carrera*/

/*CARRERA*/
/*SELECT DISTINCT COUNT(DISTINCT e.tipo_y_n_documento),
    substr(e.carrera,2, 9) as carrera
    FROM estudiantes AS e
    LEFT JOIN preinscriptos AS p
        ON p.identificacion = e.tipo_y_n_documento
    LEFT JOIN primera_inscripcion AS pi
        ON e.tipo_y_n_documento = pi.tipo_y_n_documento
    WHERE e.ano_ingreso = 2026
        AND pi.primer_ingreso = 2026
    GROUP BY e.carrera*/

/*HISTÓRICO DE PRIMEROS INGRESOS*/
/*SELECT DISTINCT COUNT(DISTINCT e.tipo_y_n_documento),
    substr(e.carrera,2, 9) as carrera, e.ano_ingreso
    FROM estudiantes AS e
    LEFT JOIN preinscriptos AS p
        ON p.identificacion = e.tipo_y_n_documento
    LEFT JOIN primera_inscripcion AS pi
        ON e.tipo_y_n_documento = pi.tipo_y_n_documento
    WHERE e.ano_ingreso >= 2022
        AND pi.primer_ingreso = e.ano_ingreso
    GROUP BY e.carrera, e.ano_ingreso*/