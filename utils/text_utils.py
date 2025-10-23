import re

def to_snake_case(name):
    """Convierte un string a formato snake_case, manejando acentos y caracteres comunes."""
    name = name.strip()
    name = re.sub(r'[\s\.\/\(\)]+', '_', name) # Reemplaza espacios y otros separadores por _
    name = re.sub(r'[ÁÉÍÓÚáéíóúÑñ]', lambda m: {'Á':'a','É':'e','Í':'i','Ó':'o','Ú':'u','á':'a','é':'e','í':'i','ó':'o','ú':'u','Ñ':'n','ñ':'n'}[m.group(0)], name)
    name = re.sub(r'[^a-zA-Z0-9_]', '', name) # Elimina caracteres no alfanuméricos restantes
    return name.lower()
