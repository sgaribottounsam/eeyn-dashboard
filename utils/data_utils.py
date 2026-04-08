# utils/data_utils.py
import pandas as pd

def estandarizar_nombres_df(df, mapeo_columnas):
    """Renombra las columnas de un DataFrame según un mapeo, si existen."""
    df_copia = df.copy()
    columnas_a_renombrar = {k: v for k, v in mapeo_columnas.items() if k in df_copia.columns}
    if columnas_a_renombrar:
        df_copia.rename(columns=columnas_a_renombrar, inplace=True)
    return df_copia
