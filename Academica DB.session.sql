
SELECT anio, carrera, COUNT(DISTINCT n_documento) FROM inscripciones_carreras 
WHERE anio = 2025
GROUP BY carrera, anio
