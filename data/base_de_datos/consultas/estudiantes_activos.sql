SELECT substr(periodo, 1, 4) AS anio, carrera,
         COUNT(DISTINCT identificacion) AS total_estudiantes
FROM inscripciones_cursadas
WHERE estado_insc = 'Aceptada'
    AND carrera NOT IN ('MA-MEDT-P', 'PR-MPCC-P', 'TE-GUIA-P', 'TG-EEYN-P', 'ES-EGTI-P')
GROUP BY anio