SELECT substr(periodo, 1, 4) AS anio, c.tipo,
         COUNT(DISTINCT identificacion) AS total_estudiantes
FROM inscripciones_cursadas
LEFT JOIN propuestas as c
    ON inscripciones_cursadas.carrera = c.codigo
WHERE estado_insc = 'Aceptada'
    AND c.tipo NOT IN ('Cursos', 'Curso de Ingreso', 'Vocacional')
GROUP BY anio, c.tipo