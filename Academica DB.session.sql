SELECT
            ic.anio, -- Usar el año académico correcto
            strftime('%m-%d', ic.fecha_insc) AS dia_mes,
            COUNT(ic.n_documento) AS cantidad
        FROM inscripciones_carreras AS ic
        JOIN propuestas AS p ON ic.carrera = p.codigo
        WHERE ic.anio = 2025 -- Filtrar por año académico
          AND (
            (strftime('%m', ic.fecha_insc) = '10') OR
            (strftime('%m', ic.fecha_insc) = '11') OR
            (strftime('%m', ic.fecha_insc) = '12' AND strftime('%d', ic.fecha_insc) <= '30')
          )
          AND p.tipo = 'Grado'
        GROUP BY ic.anio, dia_mes
        ORDER BY ic.anio, dia_mes
