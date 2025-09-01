#!/bin/bash

# Salir inmediatamente si un comando falla
set -e

# Ejecutar la aplicación Streamlit
streamlit run dashboard_eeyn.py --server.port $PORT --server.headless true

