WITH egresados_grado AS (
    SELECT DISTINCT eg.documento, 
        eg.fecha_ingreso, 
        eg.fecha_egreso, 
        eg.certificado, 
        eg.propuesta, 
        pl.actualizado AS plan,
        c.Tipo_de_Certificado AS tipo_certificado
    FROM egresados AS eg
    LEFT JOIN certificados AS c
        ON eg.Certificado = c.codigo
    LEFT JOIN planes AS pl
        ON eg.propuesta = pl.propuesta AND eg.plan = pl.plan 
    WHERE c.Tipo_de_Certificado = "Título de Grado Universitario"
)

SELECT e.Propuesta, e.Plan, COUNT(DISTINCT e.Documento) AS cantidad
FROM egresados_grado AS e
GROUP BY e.Propuesta, e.Plan;
