import pandas as pd
import json
import requests
import io
import urllib3 # Para quitar los avisos de seguridad

# Esto evita que GitHub Actions se llene de mensajes de "Advertencia de seguridad"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generar_json():
    # URL del Excel de Albacete
    url_excel = "https://geoportalgasolineras.es/resources/files/preciosEESS_es.xls"
    
    # IMPORTANTE: Añadimos verify=False para saltar el error de SSL
    response = requests.get(url_excel, verify=False)
    
    # El resto del código sigue igual...
    df = pd.read_excel(io.BytesIO(response.content), header=3)
    
    lista_final = []
    
    for _, fila in df.iterrows():
        gasolinera = {
            "rotulo": str(fila.get('Rótulo', 'N/A')),
            "direccion": str(fila.get('Dirección', 'N/A')),
            "municipio": str(fila.get('Municipio', 'N/A')),
            "toma_de_datos": str(fila.get('Toma de datos', 'Sin fecha')),
            "precio_gasoleo_a": str(fila.get('Precio gasóleo A', '0')).replace(",", "."),
            "precio_gasolina_95": str(fila.get('Precio gasolina 95 E5', '0')).replace(",", ".")
        }
        lista_final.append(gasolinera)
    
    with open('gasolineras.json', 'w', encoding='utf-8') as f:
        json.dump(lista_final, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generar_json()
