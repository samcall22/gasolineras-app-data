import pandas as pd
import requests
import io
import json
import urllib3

# Desactivamos avisos de seguridad
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generar_json():
    # URL oficial (Nacional)
    url = "https://geoportalgasolineras.es/resources/files/preciosEESS_es.xls"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print("Accediendo a los datos del Ministerio...")
        # Añadimos verify=False para evitar el error de certificado SSL
        response = requests.get(url, headers=headers, timeout=40, verify=False)
        response.raise_for_status()

        # Usamos engine='xlrd' para archivos .xls antiguos
        df = pd.read_excel(io.BytesIO(response.content), header=3, engine='xlrd')

        columnas = {
            'Provincia': 'provincia',
            'Municipio': 'municipio',
            'Localidad': 'localidad',
            'Dirección': 'direccion',
            'Código postal': 'CP',
            'Márgen': 'margen',
            'Rótulo': 'rotulo',
            'Toma de datos': 'toma_de_datos', # No olvides este
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

        df = df.rename(columns=columnas)
        columnas_validas = [c for c in columnas.values() if c in df.columns]
        df_final = df[columnas_validas].copy()

        # --- 1. LIMPIEZA DE TEXTOS ---
        # Rellenamos CUALQUIER vacío inicial con una cadena vacía ""
        df_final = df_final.fillna("")

        campos_precio = [
            'gasolina_95', 'gasolina_95_premium', 'gasolina_98', 
            'diesel_a', 'diesel_premium', 'diesel_b', 'diesel_c', 
            'glp', 'adblue', 'diesel_renovable', 'gasolina_renovable'
        ]

        # --- 2. LIMPIEZA DE NÚMEROS ---
        for col in campos_precio:
            if col in df_final.columns:
                # Convertimos a string, cambiamos coma por punto
                df_final[col] = df_final[col].astype(str).str.replace(',', '.')
                # Convertimos a número. Si hay error (como una celda vacía), pone NaN
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce')
                # CAMBIO CLAVE: Los NaN ahora serán 0.0 (número)
                df_final[col] = df_final[col].fillna(0.0)

        resultado = df_final.to_dict(orient='records')
        
        with open('gasolineras.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Proceso completado. Se han guardado {len(resultado)} registros.")

    except Exception as e:
        print(f"❌ Error al procesar: {e}")

if __name__ == "__main__":
    generar_json()
