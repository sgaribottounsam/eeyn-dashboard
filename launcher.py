#!/usr/bin/env python3
"""
Script simple para ejecutar el Dashboard EEyN
Coloca este archivo en la misma carpeta que los CSVs
"""

import os
import sys
import subprocess
from pathlib import Path


def verificar_archivos():
    """Verifica que todos los archivos CSV necesarios estén presentes."""
    archivos_necesarios = [
        '_output/inscripciones_materias/KPI_insc_materias.csv',
        '_output/inscripciones_materias/TODAS_evolucion.csv',
        '_output/inscripciones_materias/GRADO_evolucion.csv',
        '_output/inscripciones_materias/CPU_cantidad_materias.csv'
    ]

    print("🔍 Verificando archivos CSV...")
    archivos_faltantes = []

    for archivo in archivos_necesarios:
        if not os.path.exists(archivo):
            archivos_faltantes.append(archivo)
            print(f"❌ {archivo}")
        else:
            print(f"✅ {archivo}")

    if archivos_faltantes:
        print(f"\n⚠️ Faltan archivos: {', '.join(archivos_faltantes)}")
        print("Asegúrate de que estén en la carpeta '_output' del proyecto.")
        return False

    print("✅ Todos los archivos CSV están presentes")
    return True


def verificar_dependencias():
    """Verifica las dependencias de Python."""
    dependencias = ['streamlit', 'pandas', 'plotly']

    print("\n🐍 Verificando dependencias de Python...")
    faltantes = []

    for dep in dependencias:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            faltantes.append(dep)
            print(f"❌ {dep}")

    if faltantes:
        print(f"\n⚠️ Dependencias faltantes: {', '.join(faltantes)}")
        print("Ejecuta: pip install streamlit pandas plotly")
        return False

    print("✅ Todas las dependencias están instaladas")
    return True


def verificar_dashboard_file():
    """Verifica que el archivo del dashboard exista."""
    dashboard_file = '_output/dashboard_eeyn.py'
    print(f"\n🔍 Verificando archivo del dashboard: {dashboard_file}...")

    if os.path.exists(dashboard_file):
        print(f"✅ Archivo '{dashboard_file}' encontrado.")
        return True
    else:
        print(f"❌ Archivo '{dashboard_file}' no encontrado.")
        print("Asegúrate de que el archivo del dashboard esté en la carpeta '_output'.")
        return False


def ejecutar_dashboard():
    """Ejecuta el dashboard."""
    dashboard_file = '_output/dashboard_eeyn.py'

    print("\n🚀 Iniciando Dashboard EEyN...")
    print("📊 URL: http://localhost:8501")
    print("🛑 Para detener: Ctrl+C")
    print("=" * 50)

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            dashboard_file,
            "--server.port=8501",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard detenido")
    except FileNotFoundError:
        print("❌ Streamlit no encontrado. Instala con: pip install streamlit")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    print("=" * 60)
    print("🎓 DASHBOARD ACADÉMICO EEyN")
    print("   Escuela de Economía y Negocios - UNSAM")
    print("=" * 60)

    # Verificaciones
    if not verificar_archivos():
        input("\nPresiona Enter para salir...")
        return
        
    if not verificar_dependencias():
        input("\nPresiona Enter para salir...")
        return

    if not verificar_dashboard_file():
        input("\nPresiona Enter para salir...")
        return

    # Si todo está bien, ejecutar directamente
    ejecutar_dashboard()


if __name__ == "__main__":
    main()
