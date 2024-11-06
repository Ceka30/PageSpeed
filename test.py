from datetime import datetime
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

import requests
import json
import os

API_KEY = 'AIzaSyB9RQYM3GaKkTasbwRR-48GUxEkPQXwNsQ'
API_URL = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
file_path = 'informe.json'

url = 'https://www.entel.cl'

params = {
    'url': url,
    'key': API_KEY,
    'strategy': 'desktop', 
    'category': ['performance', 'accessibility', 'seo']
}

# Elimina el archivo existente si ya existe
if os.path.exists(file_path):
    os.remove(file_path)

# Hacemos la solicitud a la API
response = requests.get(API_URL, params=params)

if response.status_code == 200:
    result = response.json()

    # Guardar archivo JSON
    with open(file_path, 'w', encoding='utf-8') as json_file:
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
    print(f"El informe generado en '{file_path}'.")

    # Obtener el enlace al informe en formato HTML de PageSpeed Insights
    url_reporte = f"https://developers.google.com/speed/pagespeed/insights/?url={url}&tab=mobile"
    print(f"Link del Reporte: {url_reporte}")
    
else:
    print(f"Error en la solicitud: {response.status_code}")

with open('informe.json', 'r', encoding='utf-8') as archivo:
    datos = json.load(archivo)

# Obtener la URL desde el archivo JSON
url = datos["id"]
# Obtener las métricas
metricas = datos["loadingExperience"]["metrics"]
# Obtener la hora de ejecución
fecha_utc = datos["analysisUTCTimestamp"]

def formatear_fecha(fecha):
    fecha_utc = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%S.%fZ")
    fecha_formateada = fecha_utc.strftime("%d %b %Y, %I:%M:%S %p").lower()
    fecha_formateada = fecha_formateada.replace("am", "a.m.").replace("pm", "p.m.")
    return fecha_formateada

# Función para calcular la posición del indicador en porcentaje
def calcular_posicion(valor, limite_bueno, limite_mejora, limite_malo):
    if valor <= limite_bueno:
        return (valor / limite_bueno) * 33.33
    elif valor <= limite_mejora:
        return 33.33 + ((valor - limite_bueno) / (limite_mejora - limite_bueno)) * 33.33
    else:
        return 66.66 + ((valor - limite_mejora) / (limite_malo - limite_mejora)) * 33.33
    
# Obtener las métricas específicas
puntaje_cls = metricas["CUMULATIVE_LAYOUT_SHIFT_SCORE"]["percentile"] / 100
puntaje_ttfb = metricas["EXPERIMENTAL_TIME_TO_FIRST_BYTE"]["percentile"] / 1000
puntaje_fcp = metricas["FIRST_CONTENTFUL_PAINT_MS"]["percentile"] / 1000
puntaje_inp = metricas["INTERACTION_TO_NEXT_PAINT"]["percentile"]
puntaje_lcp = metricas["LARGEST_CONTENTFUL_PAINT_MS"]["percentile"] / 1000

# Obtener la fecha formateada
fecha = formatear_fecha(fecha_utc)

# Obtener las auditorías
auditorias = datos["lighthouseResult"]["audits"].values()

# Obtener los puntajes de Performance, Accessibility y SEO
performance_puntaje = datos["lighthouseResult"]["categories"]["performance"]["score"] * 100
accessibility_puntaje = datos["lighthouseResult"]["categories"]["accessibility"]["score"] * 100
seo_puntaje = datos["lighthouseResult"]["categories"]["seo"]["score"] * 100

# Configurar para que el HTML lea todo tipo de caracteres
entorno = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

# Cargar el template HTML
plantilla = entorno.get_template('template_informe.html')

# Renderizar el template con los datos y posiciones calculadas
contenido_html = plantilla.render(
    fecha=fecha,
    url=url,
    puntaje_cls=puntaje_cls,
    posicion_cls=calcular_posicion(puntaje_cls, 0.1, 0.25, 1.0),
    puntaje_ttfb=puntaje_ttfb,
    posicion_ttfb=calcular_posicion(puntaje_ttfb, 0.8, 1.8, 4.0),
    puntaje_fcp=puntaje_fcp,
    posicion_fcp=calcular_posicion(puntaje_fcp, 1.8, 3.0, 6.0),
    puntaje_inp=puntaje_inp,
    posicion_inp=calcular_posicion(puntaje_inp, 200, 500, 1000),
    puntaje_lcp=puntaje_lcp,
    posicion_lcp=calcular_posicion(puntaje_lcp, 2.5, 4.0, 8.0),
    auditorias=auditorias,
    performance=performance_puntaje,
    accessibility=accessibility_puntaje,
    seo=seo_puntaje
)

# Guardar el informe HTML
with open('informe_rendimiento.html', 'w', encoding='utf-8') as archivo_informe:
    archivo_informe.write(contenido_html)

print("Informe HTML generado exitosamente.")
