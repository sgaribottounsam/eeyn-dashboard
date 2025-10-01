#!/bin/bash

# Salir inmediatamente si un comando falla
set -e

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación Dash con Gunicorn
gunicorn dash_dashboard.index:server