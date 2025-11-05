/*SELECT e.propuesta, COUNT(DISTINCT e.documento)

FROM egresados AS e
LEFT JOIN propuestas AS c
    ON e.propuesta = c.codigo
WHERE c.tipo = 'Grado'

GROUP BY e.propuesta*/

SELECT c.tipo, COUNT(e.documento)

FROM egresados AS e
LEFT JOIN propuestas AS c
    ON e.propuesta = c.codigo

WHERE c.tipo IN ('Grado', 'Posgrado', 'Pregrado')


GROUP BY c.tipo