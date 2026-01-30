import pandas as pd
import json
import requests
import io
import urllib3

# Desactivar avisos de seguridad SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generar_json():
    # URL de Albacete
    url_excel = "https://geoportalgasolineras.es/resources/files/preciosEESS_es.xls"
    
    response = requests.get(url_excel, verify=False)
    
    # --- CAMBIO AQUÍ: Añadimos engine='xlrd' ---
    df = pd.read_excel(io.BytesIO(response.content), header=3, engine='xlrd')
    
    # Limpiamos nombres de columnas
    df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]

    lista_final = []
    
    for _, fila in df.iterrows():
        def limpiar_precio(valor):
            val = str(valor).replace(',', '.').strip()
            # Si el valor es 'nan', 'None' o está vacío, devolvemos "0.0"
            return val if val not in ['nan', 'None', '', 'NaN'] else "0.0"

        # Mapeamos todos los campos del Excel
        gasolinera = {
            "provincia": str(fila.get('Provincia', '')),
            "municipio": str(fila.get('Municipio', '')),
            "localidad": str(fila.get('Localidad', '')),
            "cp": str(fila.get('Código postal', '')),
            "direccion": str(fila.get('Dirección', '')),
            "margen": str(fila.get('Margen', '')),
            "toma_de_datos": str(fila.get('Toma de datos', '')),
            "precio_95_e5": limpiar_precio(fila.get('Precio gasolina 95 E5', '0')),
            "precio_98_e5": limpiar_precio(fila.get('Precio gasolina 98 E5', '0')),
            "precio_gasoleo_a": limpiar_precio(fila.get('Precio gasóleo A', '0')),
            "precio_gasoleo_premium": limpiar_precio(fila.get('Precio gasóleo Premium', '0')),
            "precio_glp": limpiar_precio(fila.get('Precio gases licuados del petróleo', '0')),
            "precio_gnc": limpiar_precio(fila.get('Precio gas natural comprimido', '0')),
            "rotulo": str(fila.get('Rótulo', 'N/A')),
            "horario": str(fila.get('Horario', 'N/A'))
        }
        lista_final.append(gasolinera)
    
    with open('gasolineras.json', 'w', encoding='utf-8') as f:
        json.dump(lista_final, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generar_json()
