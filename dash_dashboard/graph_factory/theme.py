# dash_dashboard/graph_factory/theme.py

# --- CONFIGURACIÓN GLOBAL DE GRÁFICOS ---
GRAPH_HEIGHT = 450 # Ajustado para dar más espacio a la leyenda en la base

COMMON_LAYOUT = dict(
    height=GRAPH_HEIGHT,
    plot_bgcolor='white',
    uniformtext_minsize=10, 
    uniformtext_mode='show',
    font=dict(size=10),
    margin=dict(l=20, r=20, t=40, b=100), # Margen inferior ampliado de 40 a 100
    legend=dict(
        title_text='', # Ocultar título de la leyenda por defecto
        orientation="h",
        yanchor="top",
        y=-0.25, # Aún más abajo para evitar colisiones con las etiquetas X
        xanchor="center",
        x=0.5
    )
)

# --- CONFIGURACIÓN DE COLORES ---
COLORES_CARRERAS = {
    # Grado
    'CP-CCCP-PC': '#5dae8b',
    'CCCP': '#5dae8b',
    '(CP-CCCP-PC) CONTADOR PÚBLICO': '#5dae8b',
    'CP-CCCP-PC-Plan nuevo': '#5dae8b',
    'CP-CCCP-PC-Plan Viejo': '#9dceb9',
    'LI-LAGE-P': '#f6f49d',
    'LI-LAGE-P-Plan nuevo': '#f6f49d',
    'LI-LAGE-P-Plan Viejo': '#faf8bb',
    'LAGE': '#f6f49d',
    '(LI-LAGE-P) LICENCIATURA EN ADMINISTRACIÓN Y GESTIÓN EMPRESARIAL': '#f6f49d',
    'LI-LECO-P': '#ff7676',
    'LECO': '#ff7676',
    '(LI-LECO-P) LICENCIATURA EN ECONOMÍA': '#ff7676',
    'LI-LECO-P-Plan nuevo': '#ff7676',
    'LI-LECO-P-Plan Viejo': '#ffacac',
    'LI-LEDC-P': '#FF8C00',
    '(LI-LEDC-P) LICENCIATURA EN ECONOMÍA DEL CONOCIMIENTO': '#FF8C00',
    'LI-LTUR-P': '#466c95',
    'LTUR': '#466c95',
    '(LI-LTUR-P) LICENCIATURA EN TURISMO': '#466c95',
    'LI-LTUR-P-Plan nuevo': '#466c95',
    'LI-LTUR-P-Plan Viejo': '#90a6bf',
    
    # Pregrado
    'TE-MPCO-P': '#c5705d',
    'TE-GUIA-P': '#8B4513',
    '(TE-GUIA-P) TECNICATURA UNIVERSITARIA EN GUÍA DE TURISMO': '#8B4513',
    
    # Nuevas / 2025 (Asignando colores similares o nuevos)
    'CI-EEYN-P': '#8200e1', # Ciclo Introductorio (Violeta existente)
    'CI-MPCC-P': '#A0522D', # Ciclo Introductorio Martillero (Sienna, similar a GUIA)
    'CV-EEYN-P': '#9370DB', # Curso Vocacional ? (MediumPurple)
    'DO-CECO-P': '#DC143C', # Doctorado (Crimson)
    'DO-EINN-P': '#B22222', # Doctorado (FireBrick)
    'ES-EGTI-P': '#20B2AA', # Especialización (LightSeaGreen)
    'MA-DGTI-P': '#4169E1', # Maestría (RoyalBlue)
    'MA-FINA-P': '#1E90FF', # Maestría (DodgerBlue)
    'NG-EEYN-P': '#708090', # No Grado ? (SlateGray)
    'PR-MPCC-P': '#D2691E', # Martillero Público (Chocolate)
    '(PR-MPCC-P) MARTILLERO PÚBLICO Y CORREDOR DE COMERCIO': '#D2691E',
}

# --- Funciones de Utilidad Cromática ---
def darken_color(hex_color, factor=0.7):
    """Oscurece un color hexadecimal por un factor dado."""
    if hex_color.startswith('#'):
        hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    dark_rgb = tuple(int(c * factor) for c in rgb)
    return f"#{dark_rgb[0]:02x}{dark_rgb[1]:02x}{dark_rgb[2]:02x}"

def lighten_color(hex_color, factor=0.5):
    """Aclara un color hexadecimal mezclándolo con blanco."""
    if hex_color.startswith('#'):
        hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # fórmula: (255 - c) * factor + c
    light_rgb = tuple(int((255 - c) * factor + c) for c in rgb)
    return f"#{light_rgb[0]:02x}{light_rgb[1]:02x}{light_rgb[2]:02x}"
