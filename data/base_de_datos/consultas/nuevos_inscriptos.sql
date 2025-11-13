
/*WITH primera_inscripcion AS (
    SELECT e.tipo_y_n_documento, MIN(e.ano_ingreso) AS primer_ingreso
    FROM estudiantes AS e
    GROUP BY e.tipo_y_n_documento
)

SELECT COUNT(DISTINCT e.tipo_y_n_documento) AS cantidad, 
    IIF(pi.primer_ingreso = 2026, 
        'Primera vez en la EEyN', 
        'Ya tenía legajo de la EEyN') AS situacion_eeyn
FROM estudiantes AS e
LEFT JOIN primera_inscripcion AS pi
    ON e.tipo_y_n_documento = pi.tipo_y_n_documento
WHERE e.ano_ingreso = 2026
GROUP BY situacion_eeyn
LIMIT 20

