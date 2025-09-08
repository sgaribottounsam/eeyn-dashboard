/*SELECT * FROM anio_academico;
/*SELECT DISTINCT Tipo_de_Certificado
FROM certificados*/
/*
WITH egresados_grado AS (
    SELECT DISTINCT eg.documento, 
        eg.fecha_ingreso, 
        eg.fecha_egreso, 
        eg.certificado, 
        eg.propuesta, 
        eg.plan,
        c.Tipo_de_Certificado AS tipo_certificado
    FROM egresados AS eg
    LEFT JOIN certificados AS c
        ON eg.Certificado = c.codigo
    WHERE c.Tipo_de_Certificado = "Título de Grado Universitario"
)

SELECT e.Propuesta, e.Plan, COUNT(DISTINCT e.Documento) AS cantidad
FROM egresados_grado AS e
GROUP BY e.Propuesta, e.Plan
*/

SELECT DISTINCT e.Propuesta, e.plan
FROM egresados AS e
ORDER BY e.Propuesta