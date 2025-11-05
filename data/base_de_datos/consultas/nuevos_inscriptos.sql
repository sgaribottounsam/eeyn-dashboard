
/*SELECT e.tipo_y_n_documento, MIN(e.ano_ingreso) AS primer_ingreso

FROM estudiantes AS e
GROUP BY e.tipo_y_n_documento*/

/*SELECT DISTINCT e.ano_ingreso, count(DISTINCT e.tipo_y_n_documento) AS cantidad_estudiantes
FROM estudiantes AS e*/

SELECT DISTINCT carrera FROM estudiantes

