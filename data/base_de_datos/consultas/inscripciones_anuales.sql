WITH ingresos AS (
SELECT tipo_y_n_documento,
       min(e.ano_ingreso) AS primer_ingreso    
FROM estudiantes AS e
GROUP BY tipo_y_n_documento
)

SELECT i.primer_ingreso, 
       COUNT(DISTINCT e.tipo_y_n_documento) AS cantidad_estudiantes,
       e.carrera
FROM ingresos AS i
LEFT JOIN estudiantes AS e
    ON e.tipo_y_n_documento = i.tipo_y_n_documento
        AND e.ano_ingreso = i.primer_ingreso
WHERE primer_ingreso >= 2021

GROUP BY i.primer_ingreso, e.carrera
