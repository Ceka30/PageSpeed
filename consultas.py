import requests
import json

API_KEY = 'AIzaSyB9RQYM3GaKkTasbwRR-48GUxEkPQXwNsQ'
API_URL = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'

url = 'https://www.entel.cl/mayoristas'

params = {
    'url': url,
    'key': API_KEY,
    'strategy': 'desktop',  #cambiar a 'desktop'
    'category': ['performance', 'accessibility', 'seo']
}

# Hacemos la solicitud a la API
response = requests.get(API_URL, params=params)

if response.status_code == 200:
    result = response.json()

    # Guardar archivo JSON
    with open('informe.json', 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)

    performance = result['lighthouseResult']['categories'].get('performance', {}).get('score', 0) * 100
    accessibility = result['lighthouseResult']['categories'].get('accessibility', {}).get('score', 0) * 100
    seo = result['lighthouseResult']['categories'].get('seo', {}).get('score', 0) * 100

    # Imprimimos los resultados personalizados
    print(f"Auditoria PageSpeed: {url}")
    print(f"Performance: {performance}")
    print(f"Accesibilidad: {accessibility}")
    print(f"SEO: {seo}")

    # Confirmamos que el archivo JSON se ha guardado correctamente
    print(f"El informe generado en 'informe.json'.")

    # Obtener el enlace al informe en formato HTML de PageSpeed Insights
    url_reporte = f"https://developers.google.com/speed/pagespeed/insights/?url={url}&tab=mobile"
    print(f"Link del Reporte: {url_reporte}")
    
else:
    print(f"Error en la solicitud: {response.status_code}")
