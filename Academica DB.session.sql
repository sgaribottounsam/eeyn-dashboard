/*SELECT estado, COUNT(DISTINCT identificacion) AS cantidad 
 FROM preinscriptos
 WHERE anio = 2026
 GROUP BY estado
 ORDER BY cantidad*/
/*SELECT DISTINCT carrera, COUNT(DISTINCT n_documento) FROM inscripciones_carreras
 WHERE substr(carrera,1,3) IN ('LI-', 'CP-', 'PR-')
 AND anio = 2026
 
 GROUP BY carrera*/
SHOW DATABASE;