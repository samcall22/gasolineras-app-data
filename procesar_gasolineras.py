import pandas as pd
import requests
import io
import json
import urllib3
import numpy as np

# Desactivar avisos de seguridad SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generar_json():
    url = "https://geoportalgasolineras.es/resources/files/preciosEESS_es.xls"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print("Accediendo a los datos del Ministerio...")
        response = requests.get(url, headers=headers, timeout=40, verify=False)
        response.raise_for_status()

        # Leemos el Excel con el motor xlrd
        df = pd.read_excel(io.BytesIO(response.content), header=3, engine='xlrd')

        # Definimos el mapeo de columnas
        columnas = {
            'Provincia': 'provincia',
            'Municipio': 'municipio',
            'Localidad': 'localidad',
            'Dirección': 'direccion',
            'Código postal': 'CP',
            'Márgen': 'margen',
            'Rótulo': 'rotulo',
            'Toma de datos': 'toma_de_datos',
            'Precio gasolina 95 E5': 'gasolina_95',
            'Precio gasolina 98 E5': 'gasolina_98',
            'Precio gasóleo A': 'diesel_a',
            'Precio gasóleo Premium': 'diesel_premium',
            'Precio gasolina 95 E5 Premium': 'gasolina_95_premium',
            'Precio gasóleo B': 'diesel_b',
            'Precio gasóleo C': 'diesel_c',
            'Precio gases licuados del petróleo': 'glp',
            'Precio AdBlue': 'adblue',
            'Precio diesel renovable': 'diesel_renovable',
            'Precio gasolina renovable': 'gasolina_renovable',
            'Longitud': 'longitud',
            'Latitud': 'latitud'
        }

        # Renombrar y filtrar
        df = df.rename(columns=columnas)
        columnas_finales = [c for c in columnas.values() if c in df.columns]
        df_final = df[columnas_finales].copy()

        # Identificar columnas por tipo
        campos_precio = [
            'gasolina_95', 'gasolina_95_premium', 'gasolina_98', 
            'diesel_a', 'diesel_premium', 'diesel_b', 'diesel_c', 
            'glp', 'adblue', 'diesel_renovable', 'gasolina_renovable',
            'longitud', 'latitud'
        ]
        
        campos_texto = [c for c in df_final.columns if c not in campos_precio]

        # --- 1. LIMPIEZA DE TEXTOS ---
        for col in campos_texto:
            # Reemplazamos nulos por cadena vacía y convertimos a String puro
            df_final[col] = df_final[col].fillna("").astype(str).replace('nan', '')

        # --- 2. LIMPIEZA DE NÚMEROS (PRECIOS Y COORDENADAS) ---
        for col in campos_precio:
            if col in df_final.columns:
                # Convertimos a string, quitamos comas por puntos
                df_final[col] = df_final[col].astype(str).str.replace(',', '.')
                # Convertimos a numérico, lo que no sea número se vuelve NaN
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce')
                # Reemplazamos esos NaN por 0.0 (float)
                df_final[col] = df_final[col].replace(np.nan, 0.0)
                df_final[col] = df_final[col].fillna(0.0)

        # Convertir a lista de diccionarios
        resultado = df_final.to_dict(orient='records')
        
        # Guardar JSON
        with open('gasolineras.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Proceso completado con {len(resultado)} registros. Sin NaNs.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generar_json()
