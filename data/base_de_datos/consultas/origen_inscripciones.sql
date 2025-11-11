WITH origen_insc_2026 AS (
    SELECT ic.n_documento, ic.carrera, IFNULL(p.origen, "Homologación") AS estado
    FROM inscripciones_carreras ic
    LEFT JOIN preinscriptos AS p
    ON ic.n_documento = p.identificacion
        AND ic.anio = p.anio
    WHERE ic.anio = 2026
)

SELECT estado, carrera, COUNT(DISTINCT n_documento) AS cantidad
FROM origen_insc_2026
WHERE substr(carrera,1,3) IN ('LI-', 'CP-', 'PR-')
GROUP BY estado, carrera