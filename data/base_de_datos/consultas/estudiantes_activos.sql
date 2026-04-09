SELECT substr(periodo, 1, 4) AS anio,
    substr(periodo, 6, 1) AS cuatrimestre,
    c.tipo,
    c.codigo AS carrera,
    identificacion
FROM inscripciones_cursadas
    LEFT JOIN propuestas as c ON inscripciones_cursadas.carrera = c.codigo
WHERE estado_insc = 'Aceptada'
    AND c.tipo IN (
        'Grado',
        'Pregrado',
        'Posgrado',
        'Curso de Ingreso'
    )
    AND substr(periodo, 1, 4) BETWEEN '2022' AND '2026'