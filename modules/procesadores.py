import re
import numpy as np
import pandas as pd
from unidecode import unidecode

def capitalizar_nombre(nombre: str) -> str:
    """
    Capitaliza cada parte del nombre (excepto si está todo en mayúsculas).
    Ej: "juan perez" → "Juan Perez", "JUAN PEREZ" → "JUAN PEREZ"
    """
    return " ".join([s.capitalize() if not s.isupper() else s for s in re.split(r"[\s\-\.]", nombre)])

def procesar_autor(nombre: str, apellido: str) -> dict:
    """
    Genera variantes del nombre del autor:
    - nombre_formal: APELLIDO, NOMBRE
    - nombre_visual: Nombre Apellido (capitalizado)
    - sin_tildes: versión sin tildes del nombre_formal
    - nombre_normalizado: apellido nombre sin tildes y en minúscula
    """
    nombre = nombre.strip()
    apellido = apellido.strip()

    nombre_formal = f"{apellido.upper()}, {nombre.upper()}"
    nombre_visual = f"{capitalizar_nombre(nombre)} {capitalizar_nombre(apellido)}"
    sin_tildes = unidecode(nombre_formal)
    nombre_normalizado = unidecode(f"{apellido} {nombre}").lower().strip()

    return {
        "nombre_formal": nombre_formal,
        "nombre_visual": nombre_visual,
        "sin_tildes": sin_tildes,
        "nombre_normalizado": nombre_normalizado
    }

def limpiar_valores_nulos(diccionario: dict) -> dict:
    """
    Reemplaza valores nulos, NaN o vacíos por None.
    Útil antes de insertar en Supabase.
    """
    limpio = {
        k: None if (
            v is None or
            (isinstance(v, str) and v.strip().upper() == "NULL") or
            (isinstance(v, float) and pd.isna(v)) or
            isinstance(v, pd._libs.missing.NAType) or
            (isinstance(v, np.float64) and np.isnan(v))
        ) else v
        for k, v in diccionario.items()
    }
    return limpio

def procesar_autor_desde_texto(texto: str) -> dict:
    """
    Procesa un texto tipo "Pérez, Juan" o "Juan Pérez" y lo divide en nombre y apellido.
    Luego genera variantes con `procesar_autor`.
    """
    texto = texto.strip()
    if "," in texto:
        partes = [p.strip() for p in texto.split(",")]
        apellido = partes[0] if len(partes) >= 1 else ""
        nombre = partes[1] if len(partes) == 2 else ""
    else:
        tokens = texto.split()
        apellido = " ".join(tokens[:-1]) if len(tokens) >= 2 else texto
        nombre = tokens[-1] if len(tokens) >= 2 else ""

    return procesar_autor(nombre, apellido)
