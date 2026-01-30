import pandas as pd
import requests
import io
import json

def generar_json():
    # URL oficial de descarga (XLS)
    url = "https://geoportalgasolineras.es/resources/files/preciosEESS_es.xls"
    
    # Header para evitar el error de formato/bloqueo
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print("Accediendo a los datos del Ministerio...")
        response = requests.get(url, headers=headers, timeout=40)
        response.raise_for_status()

        # Leemos el Excel. El header suele estar en la fila 3
        df = pd.read_excel(io.BytesIO(response.content), header=3)

        # Mapeo manteniendo tus nombres previos y añadiendo los nuevos en concordancia
        columnas = {
            'Provincia': 'provincia',
            'Municipio': 'municipio',
            'Localidad': 'localidad',
            'Dirección': 'direccion',
            'Márgen': 'margen',
            'Rótulo': 'rotulo',
            # Campos anteriores
            'Precio gasolina 95 E5': 'gasolina_95',
            'Precio gasolina 98 E5': 'gasolina_98',
            'Precio gasóleo A': 'diesel_a',
            'Precio gasóleo Premium': 'diesel_premium',
            # Nuevos campos solicitados
            'Precio gasolina 95 E5 Premium': 'gasolina_95_premium',
            'Precio gasóleo B': 'diesel_b',
            'Precio gasóleo C': 'diesel_c',
            'Precio gases licuados del petróleo': 'glp',
            'Precio AdBlue': 'adblue',
            'Precio diesel renovable': 'diesel_renovable',
            'Precio gasolina renovable': 'gasolina_renovable',
            # Coordenadas
            'Longitud': 'longitud',
            'Latitud': 'latitud'
        }

        # Renombrar
        df = df.rename(columns=columnas)
        
        # Filtrar solo las que hemos mapeado
        columnas_validas = [c for c in columnas.values() if c in df.columns]
        df_final = df[columnas_validas].copy()

        # Lista de campos numéricos para limpiar (puntos por comas)
        campos_precio = [
            'gasolina_95', 'gasolina_95_premium', 'gasolina_98', 
            'diesel_a', 'diesel_premium', 'diesel_b', 'diesel_c', 
            'glp', 'adblue', 'diesel_renovable', 'gasolina_renovable'
        ]

        # Limpieza de datos: de "1,459" (str) a 1.459 (float)
        for col in campos_precio:
            if col in df_final.columns:
                df_final[col] = (df_final[col]
                                 .astype(str)
                                 .str.replace(',', '.')
                                 .apply(pd.to_numeric, errors='coerce'))

        # Conversión final a JSON
        resultado = df_final.to_dict(orient='records')
        
        with open('gasolineras.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)
            
        print(f"✅ Proceso completado. Se han guardado {len(resultado)} registros.")

    except Exception as e:
        print(f"❌ Error al procesar: {e}")

if __name__ == "__main__":
    generar_json()
