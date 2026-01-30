import pandas as pd
import json
import requests
import io
import urllib3

# Desactivar avisos de seguridad SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generar_json():
    # URL de Albacete (puedes cambiar el 02 por otra provincia si quieres)
    url_excel = "https://geoportal.minetur.gob.es/QueGasolineraTieneElPrecioMasBajo/descargaPrecios?provincia=02"
    
    response = requests.get(url_excel, verify=False)
    # Leemos el Excel. El encabezado real está en la fila 3
    df = pd.read_excel(io.BytesIO(response.content), header=3)
    
    # Limpiamos nombres de columnas para que no tengan saltos de línea ni espacios raros
    df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]

    lista_final = []
    
    for _, fila in df.iterrows():
        # Función auxiliar para limpiar precios (comas por puntos)
        def limpiar_precio(valor):
            val = str(valor).replace(',', '.').strip()
            return val if val != 'nan' else "0.0"

        gasolinera = {
            "provincia": str(fila.get('Provincia', '')),
            "municipio": str(fila.get('Municipio', '')),
            "localidad": str(fila.get('Localidad', '')),
            "cp": str(fila.get('Código postal', '')),
            "direccion": str(fila.get('Dirección', '')),
            "toma_de_datos": str(fila.get('Toma de datos', '')),
            "precio_95": limpiar_precio(fila.get('Precio gasolina 95 E5', '0')),
            "precio_98": limpiar_precio(fila.get('Precio gasolina 98 E5', '0')),
            "precio_gasoleo_a": limpiar_precio(fila.get('Precio gasóleo A', '0')),
            "precio_gasoleo_b": limpiar_precio(fila.get('Precio gasóleo B', '0')),
            "precio_gasoleo_premium": limpiar_precio(fila.get('Precio gasóleo Premium', '0')),
            "precio_bioetanol": limpiar_precio(fila.get('Precio bioetanol', '0')),
            "precio_biodiesel": limpiar_precio(fila.get('Precio biodiesel', '0')),
            "precio_glp": limpiar_precio(fila.get('Precio gases licuados del petróleo', '0')),
            "rotulo": str(fila.get('Rótulo', 'N/A')),
            "horario": str(fila.get('Horario', 'N/A')),
            "tipo_venta": str(fila.get('Tipo venta', '')),
        }
        lista_final.append(gasolinera)
    
    with open('gasolineras.json', 'w', encoding='utf-8') as f:
        json.dump(lista_final, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    generar_json()
