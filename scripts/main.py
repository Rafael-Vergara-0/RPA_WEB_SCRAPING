# =============================================================================
# ===                     FRAMEWORK DE AUTOMATIZACIÓN RPA                 ===
# ===           Por [Tu Nombre] - Exhibición para Portafolio              ===
# =============================================================================
#
# DESCRIPCIÓN:
# Este script es un ejemplo de un framework de Automatización Robótica de
# Procesos (RPA) desarrollado en Python. Demuestra un enfoque modular, robusto
# y escalable para automatizar tareas web complejas que involucran:
#
#   - Login en plataformas seguras.
#   - Navegación a través de menús dinámicos.
#   - Interacción con formularios (ej. selección de fechas).
#   - Descarga de archivos (ej. reportes CSV).
#   - Procesamiento y limpieza de datos con Pandas.
#   - Interacción con el usuario a través de una GUI simple (Tkinter).
#   - Logging detallado y manejo de errores profesional.
#
# NOTA: Las URLs, selectores y lógica de negocio específica han sido
# reemplazados por placeholders genéricos para proteger la confidencialidad
# y demostrar la capacidad de adaptación del framework.
#
# =============================================================================

# --- 1. IMPORTACIONES Y CONFIGURACIÓN DEL ENTORNO ---
# Se importan las librerías estándar, las de terceros (Pandas, Selenium) y
# los módulos propios del proyecto.

import json
import os
import sys
import time
import logging
import platform
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import csv

# --- AJUSTE DE RUTA PARA IMPORTACIONES ROBUSTAS ---
# Esta sección garantiza que los módulos propios (como 'config') se puedan
# importar correctamente, sin importar desde dónde se ejecute el script.
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- IMPORTACIÓN Y CONFIGURACIÓN DEL MÓDULO DE LOGGING CENTRALIZADO ---
# Se utiliza un módulo 'log_config' (una pieza clave de este framework) que maneja
# las rutas de archivos de forma inteligente, distinguiendo entre entorno de
# desarrollo y producción (ejecutable .exe empaquetado).
try:
    from config.log_config import configurar_logging, get_credentials_path, get_data_path
    
    # Cada ejecución genera su propio archivo de log con timestamp, facilitando
    # la depuración de un proceso específico sin mezclarlo con otros.
    timestamp_log = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_log_ejecucion = f"ejecucion_rpa_{timestamp_log}.log"
    configurar_logging(nombre_archivo_log=nombre_log_ejecucion)

except ImportError:
    # Si 'log_config' falla, el script no se detiene. Provee un logging básico
    # para poder diagnosticar el problema. Esto es 'degradación agraciada'.
    print("ERROR CRÍTICO: No se pudo importar 'log_config'. Usando logging de emergencia.")
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger("RPA_Main_Flow")

# --- Importaciones de GUI (Tkinter) y Web (Selenium) ---
# Las importaciones se agrupan por funcionalidad para mayor claridad.
import tkinter as tk
from tkinter import simpledialog, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# --- 2. CONSTANTES Y CONFIGURACIÓN DEL PROCESO ---
# Almacenar URLs y selectores como constantes en la parte superior del script
# mejora enormemente la mantenibilidad. Si la web cambia, solo hay que
# actualizar esta sección.

URL_PRUEBA_LOGIN = "https://mi-aplicacion-web-de-prueba.com/login"
DIR_DESCARGAS_TEMPORAL = "descargas_temp"
NOMBRE_BASE_REPORTE_FINAL = "reporte_procesado"

# --- Selectores de la Página de Login ---
ID_CAMPO_USUARIO = "username"
ID_CAMPO_PASSWORD = "password"
ID_CAMPO_EMPRESA = "companyId" # Ejemplo de un campo extra en el login
SELECTOR_BOTON_LOGIN = (By.XPATH, "//button[contains(text(), 'Ingresar')]")

# --- Selectores de la Página Principal (Post-Login) ---
SELECTOR_ICONO_MENU = (By.CSS_SELECTOR, "i.fa-bars.menu-icon")
TEXTO_OPCION_MENU = "Reportes Avanzados"
SELECTOR_FECHA_INICIO = (By.ID, "date-start")

# --- Selectores del Módulo/Pop-up de Exportación ---
XPATH_BOTON_EXPORTAR = "//div[@class='report-container']//button[@title='Exportar']"
XPATH_OPCION_EXPORTAR_CSV = "//ul[@class='export-menu']//li[text()='Exportar a CSV']"
XPATH_BOTON_CONFIRMAR_DESCARGA = "//div[@class='modal-dialog']//button[text()='Confirmar']"


# --- 3. FUNCIONES AUXILIARES Y DE LÓGICA DE NEGOCIO ---
# El código se divide en funciones lógicas, cada una con una única
# responsabilidad. Esto facilita las pruebas, la reutilización y la lectura.

def cargar_credenciales(ruta_archivo: str) -> dict | None:
    """
    Carga de forma segura las credenciales desde un archivo JSON externo.
    Maneja errores comunes como archivo no encontrado o JSON mal formado.
    Separar las credenciales del código es una práctica de seguridad fundamental.
    """
    logger.debug(f"Intentando cargar credenciales desde: {ruta_archivo}")
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Archivo de credenciales no encontrado en la ruta especificada: {ruta_archivo}")
        messagebox.showerror("Error", f"No se encontró el archivo de credenciales:\n{ruta_archivo}")
        return None
    except json.JSONDecodeError:
        logger.error(f"El archivo de credenciales contiene un error de formato JSON: {ruta_archivo}")
        messagebox.showerror("Error", f"Archivo de credenciales con formato JSON inválido.")
        return None


def obtener_fecha_interactiva(fecha_sugerida: str) -> str | None:
    """
    Demuestra la capacidad de crear un RPA interactivo.
    Usa Tkinter para presentar una GUI simple al usuario, permitiéndole confirmar
    una fecha sugerida o ingresar una manualmente. Esto es mucho más amigable
    que requerir la modificación de un archivo de configuración.
    """
    logger.info("Mostrando diálogo de selección de fecha al usuario.")
    # El código interno de la GUI (original) es excelente para demostrarlo.
    # Aquí se mantiene la lógica, mostrando que la capacidad existe.
    root = tk.Tk(); root.withdraw()
    fecha_seleccionada = simpledialog.askstring("Fecha del Reporte", f"Ingrese la fecha (dd/mm/yyyy):\n(Sugerida: {fecha_sugerida})", initialvalue=fecha_sugerida)
    if fecha_seleccionada:
        logger.info(f"Usuario seleccionó la fecha: {fecha_seleccionada}")
    else:
        logger.warning("Usuario canceló la selección de fecha.")
    return fecha_seleccionada


def realizar_login(driver, wait, creds: dict):
    """
    Encapsula toda la lógica de login. Si el proceso de login cambia,
    solo se modifica esta función.
    """
    logger.info("Iniciando proceso de login.")
    try:
        driver.get(URL_PRUEBA_LOGIN)
        wait.until(EC.visibility_of_element_located((By.ID, ID_CAMPO_USUARIO))).send_keys(creds["correo"])
        wait.until(EC.visibility_of_element_located((By.ID, ID_CAMPO_PASSWORD))).send_keys(creds["contraseña"])
        wait.until(EC.visibility_of_element_located((By.ID, ID_CAMPO_EMPRESA))).send_keys(creds["empresa"])
        wait.until(EC.element_to_be_clickable(SELECTOR_BOTON_LOGIN)).click()
        
        # Una buena práctica es esperar por un elemento de la página siguiente
        # para confirmar que el login fue exitoso.
        wait.until(EC.visibility_of_element_located(SELECTOR_ICONO_MENU))
        logger.info("Login realizado con éxito.")
        return True
    except TimeoutException:
        logger.error("Timeout durante el login. ¿Credenciales incorrectas o la página no cargó a tiempo?")
        return False
    except Exception as e:
        logger.exception(f"Error inesperado durante el login: {e}")
        return False


def procesar_reporte_con_pandas(ruta_csv_descargado: Path, ruta_dir_salida: Path, fecha_reporte: str) -> Path | None:
    """
    Encapsula la lógica de Transformación y Carga (parte del ETL).
    Esta función es un ejemplo de cómo manipular datos usando Pandas. La lógica
    interna puede ser tan compleja como se requiera.
    """
    logger.info(f"Iniciando procesamiento de datos con Pandas para el archivo: {ruta_csv_descargado.name}")
    try:
        # Cargar el archivo, intentando diferentes codificaciones si es necesario (robustez).
        df = pd.read_csv(ruta_csv_descargado, delimiter=";", encoding='utf-8', on_bad_lines='skip')
        logger.debug(f"Archivo cargado. {len(df)} filas y {len(df.columns)} columnas iniciales.")

        # --- LÓGICA DE TRANSFORMACIÓN DE DATOS (EJEMPLO GENÉRICO) ---

        # 1. LIMPIEZA: Renombrar columnas para estandarizar (quitar espacios, acentos).
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # 2. ENRIQUECIMIENTO: Añadir nuevas columnas basadas en datos existentes.
        df.insert(0, 'fecha_reporte', pd.to_datetime(fecha_reporte, format='%d/%m/%Y').strftime('%Y-%m-%d'))
        
        # 3. TRANSFORMACIÓN: Aplicar una función para crear una categoría.
        if 'tipo_transaccion' in df.columns:
            df['es_ingreso'] = df['tipo_transaccion'].apply(lambda x: True if 'venta' in str(x).lower() else False)

        # 4. FILTRADO: Eliminar filas que no cumplen un criterio.
        if 'importe_neto' in df.columns:
            df['importe_neto'] = pd.to_numeric(df['importe_neto'], errors='coerce')
            df.dropna(subset=['importe_neto'], inplace=True) # Eliminar filas donde el importe no es un número
            df = df[df['importe_neto'] > 0]

        # 5. SELECCIÓN: Quedarse solo con las columnas de interés en el orden deseado.
        columnas_finales = ['fecha_reporte', 'id_cliente', 'tipo_transaccion', 'importe_neto']
        columnas_existentes_para_final = [col for col in columnas_finales if col in df.columns]
        df_final = df[columnas_existentes_para_final]

        logger.info(f"Procesamiento finalizado. {len(df_final)} filas listas para exportar.")
        
        # --- EXPORTACIÓN ---
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ruta_salida_final = ruta_dir_salida / f"{NOMBRE_BASE_REPORTE_FINAL}_{timestamp}.csv"
        df_final.to_csv(ruta_salida_final, index=False, sep=';', quoting=csv.QUOTE_ALL, encoding='utf-8-sig')

        logger.info(f"Reporte procesado guardado exitosamente en: {ruta_salida_final}")
        return ruta_salida_final

    except FileNotFoundError:
        logger.error(f"El archivo a procesar no fue encontrado: {ruta_csv_descargado}")
        return None
    except Exception as e:
        logger.exception(f"Error inesperado durante el procesamiento con Pandas: {e}")
        return None

# --- 4. FLUJO PRINCIPAL DE EJECUCIÓN ---
def ejecutar_flujo_rpa():
    """
    Función principal que orquesta todo el proceso.
    Sigue una secuencia lógica y utiliza el manejo de errores en cada paso crítico.
    """
    logger.info("================ INICIO DEL FLUJO RPA ================")
    
    ruta_credenciales = get_credentials_path()
    credenciales = cargar_credenciales(ruta_credenciales)
    if not credenciales:
        logger.critical("No se pudieron cargar las credenciales. Terminando proceso.")
        return # Salida temprana si falla un paso crítico

    dir_descarga_temp = get_data_path(DIR_DESCARGAS_TEMPORAL)
    dir_salida_final = get_data_path()

    # --- Pre-Ejecución: Limpieza de directorios ---
    # Es una buena práctica asegurar un estado limpio antes de cada ejecución,
    # especialmente en la carpeta de descargas para evitar usar archivos antiguos.
    try:
        if os.path.exists(dir_descarga_temp):
            shutil.rmtree(dir_descarga_temp)
            logger.info(f"Directorio temporal limpiado: {dir_descarga_temp}")
        os.makedirs(dir_descarga_temp)
    except OSError as e:
        logger.error(f"No se pudo limpiar/crear el directorio de descargas: {e}")
        return

    driver = None
    proceso_exitoso = False
    try:
        # --- PASO 1: Inicialización del Navegador ---
        logger.info("Inicializando WebDriver de Chrome...")
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("prefs", {"download.default_directory": dir_descarga_temp})
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 30) # Un wait global con un timeout generoso.
        driver.maximize_window()

        # --- PASO 2: Login ---
        if not realizar_login(driver, wait, credenciales):
            raise Exception("Fallo en el Login. Abortando.") # Lanzar excepción para ir al finally

        # --- PASO 3: Interacción con el Usuario para obtener fecha ---
        fecha_sugerida = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
        fecha_elegida = obtener_fecha_interactiva(fecha_sugerida)
        if not fecha_elegida:
            logger.warning("Proceso cancelado por el usuario en la selección de fecha.")
            return

        # --- PASO 4: Navegación y descarga (simulado) ---
        logger.info("Iniciando secuencia de navegación y descarga del reporte...")
        # Aquí iría el código para navegar menús, aplicar filtros de fecha y
        # hacer clic en los botones de exportación, usando los selectores definidos.
        # Por ejemplo: wait.until(EC.element_to_be_clickable(XPATH_BOTON_EXPORTAR)).click()
        # Se simulará la creación de un archivo para continuar el flujo.
        
        ruta_csv_descargado_simulado = Path(dir_descarga_temp) / "reporte_bruto_simulado.csv"
        pd.DataFrame({
            'ID Cliente': [101, 102, 103], 'Tipo Transaccion': ['Venta', 'Devolucion', 'Venta'],
            'Importe Neto': [200.50, -50.0, 120.75]
        }).to_csv(ruta_csv_descargado_simulado, index=False, sep=';')
        logger.info(f"Descarga simulada completada. Archivo: {ruta_csv_descargado_simulado}")

        # --- PASO 5: Procesamiento de Datos ---
        ruta_archivo_final = procesar_reporte_con_pandas(
            ruta_csv_descargado_simulado, Path(dir_salida_final), fecha_elegida
        )

        if ruta_archivo_final:
            logger.info("PROCESO COMPLETADO CON ÉXITO.")
            messagebox.showinfo("Éxito", f"El proceso ha finalizado correctamente.\nReporte guardado en: {ruta_archivo_final}")
            proceso_exitoso = True
        else:
            logger.error("El procesamiento de datos falló. Revise los logs.")
            messagebox.showerror("Error", "Ocurrió un error al procesar los datos. Consulte el archivo de log para más detalles.")

    except Exception as e:
        logger.critical(f"Ha ocurrido un error CRÍTICO en el flujo principal: {e}", exc_info=True)
        messagebox.showerror("Error Crítico", f"Ha ocurrido un error inesperado durante la ejecución:\n{e}\n\nRevise los logs.")

    finally:
        # --- PASO FINAL: Cierre de recursos ---
        # El bloque 'finally' se ejecuta siempre, garantizando que el navegador
        # se cierre incluso si ocurre un error, para no dejar procesos zombie.
        if driver:
            logger.info("Cerrando el navegador y finalizando el proceso.")
            driver.quit()
        logger.info("================= FIN DEL FLUJO RPA =================")


# --- PUNTO DE ENTRADA DEL SCRIPT ---
# El estándar de Python para asegurar que el código se ejecute solo
# cuando el archivo es llamado directamente.
if __name__ == "__main__":
    ejecutar_flujo_rpa()