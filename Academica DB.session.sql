SELECT
            anio,
            strftime('%m-%d', fecha_insc) AS dia_mes,
            COUNT(DISTINCT ic.n_documento) AS cantidad
        FROM inscripciones_carreras AS ic
        JOIN propuestas AS p ON ic.carrera = p.codigo
        WHERE anio >= 2024
          AND (
            (strftime('%m', fecha_insc) = '10') OR
            (strftime('%m', fecha_insc) = '11' AND strftime('%d', fecha_insc) <= '15')
          )
          AND p.tipo = 'Grado'
        GROUP BY anio, dia_mes
        ORDER BY anio, dia_mes