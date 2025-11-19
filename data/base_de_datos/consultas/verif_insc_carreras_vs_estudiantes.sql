SELECT ic.n_documento, ic.apellido_y_nombre, 
    IFNULL(GROUP_CONCAT(DISTINCT substr(ic.carrera,1,9)), 'REVISAR') AS inscripciones, 
    IFNULL(GROUP_CONCAT(DISTINCT substr(e.carrera,2,9)), "REVISAR") AS carreras, 
 COUNT(DISTINCT e.carrera) AS cantidad_carreras
FROM inscripciones_carreras AS ic
RIGHT JOIN estudiantes AS e
    ON e.tipo_y_n_documento = ic.n_documento
    AND e.ano_ingreso = 2026
    AND substr(ic.carrera, 1, 3) != 'CI-'
WHERE ic.anio = 2026 
    AND substr(ic.carrera, 1, 3) != 'CI-' /* ('LI-', 'CP-', 'PR-')*/

GROUP BY ic.n_documento

HAVING inscripciones = carreras