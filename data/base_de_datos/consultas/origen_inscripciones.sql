WITH origen_insc_2026 AS (
    SELECT 
        ic.tipo_y_n_documento,
        propuestas.tipo,
        GROUP_CONCAT(DISTINCT IFNULL(p.origen, "Homologación")/* ORDER BY p.origen*/) AS origen
    FROM estudiantes AS ic
    LEFT JOIN (
        SELECT p.identificacion, p.anio, p.origen 
        FROM preinscriptos AS p
        ORDER BY p.origen)
    AS p
        ON ic.tipo_y_n_documento = p.identificacion AND ic.ano_ingreso = p.anio
    LEFT JOIN propuestas
        ON propuestas.codigo = ic.carrera
    WHERE ic.ano_ingreso = 2026
    GROUP BY ic.tipo_y_n_documento, propuestas.tipo
)
SELECT 
    origen, 
    COUNT(tipo_y_n_documento) AS cantidad
FROM origen_insc_2026
GROUP BY origen, tipo