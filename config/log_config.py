# config/log_config.py
"""
Módulo centralizado para configuración de logging y GESTIÓN DE RUTAS
compatibles con desarrollo y PyInstaller.

Maneja la distinción entre rutas de LECTURA (código, recursos internos)
y rutas de ESCRITURA (logs, datos generados, config externa como credenciales).
"""
import logging
import os
import sys
import inspect # Necesario para fallbacks de ruta
from logging.handlers import RotatingFileHandler

# ---------------------------------------------------------------------------
# Estado Interno del Logging
# ---------------------------------------------------------------------------
_configuracion_realizada = False
_ruta_archivo_log_actual = None

# ---------------------------------------------------------------------------
# Detección de Entorno Empaquetado (PyInstaller)
# ---------------------------------------------------------------------------
IS_BUNDLED = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# ---------------------------------------------------------------------------
# Cálculo Centralizado de Rutas Base
# ---------------------------------------------------------------------------

def _obtener_ruta_base_lectura():
    """
    Retorna la ruta base absoluta para LEER archivos/código.
    - En modo empaquetado: Retorna la carpeta temporal _MEIPASS.
    - En modo desarrollo: Retorna la raíz del proyecto detectada.
    """
    if IS_BUNDLED:
        # Los archivos empaquetados se leen desde _MEIPASS
        ruta_base = sys._MEIPASS
    else:
        # En desarrollo, encontrar la raíz del proyecto
        ruta_base = None
        try:
            # Intenta usar __file__ (asumiendo que está en config/)
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            # Sube un nivel para llegar a la raíz del proyecto desde config/
            ruta_base = os.path.abspath(os.path.join(directorio_actual, '..'))
        except NameError:
            # Fallback si __file__ no está definido (ej. interactivo, zipapp)
            try:
                # Intenta usar la pila de llamadas para encontrar el script original
                caller_frame = inspect.currentframe()
                # Retroceder en la pila hasta encontrar un frame con un archivo .py válido
                # (Evita quedarse en frames internos de librerías si es posible)
                while caller_frame and caller_frame.f_back and '__file__' not in caller_frame.f_globals:
                    caller_frame = caller_frame.f_back
                
                # Si encontramos un frame adecuado con __file__
                if caller_frame and '__file__' in caller_frame.f_globals:
                     caller_file = caller_frame.f_globals['__file__']
                # O intenta directamente con inspect.getfile en un frame anterior
                else: 
                     caller_frame_fallback = inspect.currentframe().f_back if inspect.currentframe().f_back else inspect.currentframe()
                     caller_file = inspect.getfile(caller_frame_fallback)
                
                directorio_script_original = os.path.dirname(os.path.abspath(caller_file))
                
                # Heurística: Si el script original está en 'scripts', sube un nivel
                if os.path.basename(directorio_script_original) == 'scripts':
                    ruta_base = os.path.abspath(os.path.join(directorio_script_original, '..'))
                else:
                    # Asume que el script original está en la raíz o la detección falló
                    ruta_base = directorio_script_original
            except Exception:
                 # Fallback definitivo: Usa el directorio de trabajo actual
                 ruta_base = os.path.abspath('.')
                 # print(f"ADVERTENCIA (log_config): No se pudo determinar la raíz del proyecto, usando CWD ({ruta_base}) como base de lectura.") # Opcional
        
        # Si la ruta base sigue sin definirse por alguna razón
        if ruta_base is None:
             ruta_base = os.path.abspath('.')
             print(f"ERROR (log_config): Fallback final a CWD ({ruta_base}) como base de lectura.")

    return ruta_base

def _obtener_ruta_base_escritura():
    """
    Retorna la ruta base absoluta para ESCRIBIR archivos (logs, datos)
    y LEER configuraciones externas (credenciales).
    - En modo empaquetado: Retorna el directorio donde está el .EXE.
    - En modo desarrollo: Retorna la raíz del proyecto (igual que lectura).
    """
    if IS_BUNDLED:
        # Escribir/leer archivos externos junto al ejecutable
        return os.path.dirname(sys.executable)
    else:
        # En desarrollo, usar la misma raíz del proyecto para escribir/leer
        return _obtener_ruta_base_lectura()

# --- Rutas Base Calculadas (disponibles para importar en otros módulos) ---
RUTA_BASE_LECTURA = _obtener_ruta_base_lectura()
RUTA_BASE_ESCRITURA = _obtener_ruta_base_escritura()

# ---------------------------------------------------------------------------
# Funciones Públicas para Obtener Rutas Específicas
# ---------------------------------------------------------------------------

def get_credentials_path():
    """
    Obtiene la ruta absoluta al archivo 'credenciales.json' EXTERNO.

    - En desarrollo: Busca en {RaízProyecto}/config/credenciales.json
    - Empaquetado: Busca en {DirectorioDelEXE}/config/credenciales.json
    """
    if IS_BUNDLED:
        # Para credenciales externas, la base es el directorio del EXE
        base_para_credenciales = RUTA_BASE_ESCRITURA
    else:
        # En desarrollo, la base es la raíz del proyecto
        base_para_credenciales = RUTA_BASE_LECTURA

    # Construir la ruta relativa a la base adecuada
    ruta_final = os.path.join(base_para_credenciales, 'config', 'credenciales.json')
    # print(f"DEBUG (get_credentials_path): IS_BUNDLED={IS_BUNDLED}, Base={base_para_credenciales}, Final={ruta_final}") # Descomentar para depuración intensa
    return ruta_final


def get_data_path(relative_path_inside_data=""):
    """
    Obtiene la ruta absoluta a un archivo/subdirectorio dentro de la carpeta 'data'.
    La carpeta 'data' SIEMPRE se considera relativa a la RUTA_BASE_ESCRITURA
    (junto al .exe o en la raíz del proyecto).
    """
    # Datos siempre en la ubicación de escritura
    return os.path.join(RUTA_BASE_ESCRITURA, 'data', relative_path_inside_data)

def get_logs_path(relative_path_inside_logs=""):
    """
    Obtiene la ruta absoluta a un archivo/subdirectorio dentro de la carpeta 'logs'.
    La carpeta 'logs' SIEMPRE se considera relativa a la RUTA_BASE_ESCRITURA
    (junto al .exe o en la raíz del proyecto).
    """
    # Logs siempre en la ubicación de escritura
    return os.path.join(RUTA_BASE_ESCRITURA, 'logs', relative_path_inside_logs)


# ---------------------------------------------------------------------------
# Función Principal de Configuración de Logging (MODIFICADA)
# ---------------------------------------------------------------------------

def configurar_logging(
    nombre_archivo_log="app.log",  # SOLO el nombre base del archivo (sin directorio)
    nivel_archivo=logging.DEBUG,
    nivel_consola=logging.INFO,
    usar_rotacion=True,
    max_bytes_rotacion=10*1024*1024, # 10 MB
    num_respaldos=5,
    log_a_consola=True,
    log_a_archivo=True
):
    """
    Configura el sistema de logging usando las rutas de escritura centralizadas.
    Crea la carpeta de logs si no existe. Limpia handlers anteriores.

    Args:
        nombre_archivo_log (str): Nombre base del archivo de log (ej: "proceso_rpa.log").
        nivel_archivo (int): Nivel mínimo para guardar en archivo.
        nivel_consola (int): Nivel mínimo para mostrar en consola.
        usar_rotacion (bool): Activar rotación de archivos de log.
        max_bytes_rotacion (int): Tamaño máximo en bytes antes de rotar.
        num_respaldos (int): Número de archivos de respaldo a mantener.
        log_a_consola (bool): Habilitar logging en consola.
        log_a_archivo (bool): Habilitar logging en archivo.
    """
    global _configuracion_realizada, _ruta_archivo_log_actual

    # --- Seguridad: Evitar Reconfiguración Múltiple ---
    if _configuracion_realizada:
        # Ya se configuró, solo avisar si se intenta de nuevo
        logging.getLogger("ConfigLog").warning("Intento de reconfigurar logging ya configurado.")
        return

    # --- Configuración Raíz y Formato ---
    logger_raiz = logging.getLogger() # Logger raíz
    logger_raiz.setLevel(logging.DEBUG) # Permitir que pasen todos los mensajes, handlers filtran
    formato_log_str = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    formateador_log = logging.Formatter(formato_log_str, datefmt='%Y-%m-%d %H:%M:%S')

    # --- Limpieza de Handlers Existentes ---
    # Esencial para prevenir logs duplicados si hay reimports o llamadas accidentales
    for handler in logger_raiz.handlers[:]:
        try:
            handler.close()
            logger_raiz.removeHandler(handler)
        except Exception as e_close:
            # Loggear error de cierre, pero no detener la configuración
            print(f"ADVERTENCIA (log_config): Error cerrando handler de log existente: {e_close}")


    # --- Manejador de Consola ---
    if log_a_consola:
        manejador_consola = logging.StreamHandler(sys.stdout)
        manejador_consola.setLevel(nivel_consola)
        manejador_consola.setFormatter(formateador_log)
        logger_raiz.addHandler(manejador_consola)

    # --- Manejador de Archivo ---
    _ruta_archivo_log_actual = None # Resetea ruta activa
    if log_a_archivo:
        try:
            # 1. Obtener la ruta COMPLETA a la carpeta de logs (centralizado)
            ruta_directorio_log = get_logs_path()

            # 2. Asegurarse que la carpeta de logs EXISTA (fundamental)
            os.makedirs(ruta_directorio_log, exist_ok=True)
            # print(f"DEBUG (log_config): Directorio Logs asegurado en: {ruta_directorio_log}") # Descomentar para debug

            # 3. Construir la ruta COMPLETA al archivo de log
            ruta_completa_archivo = os.path.join(ruta_directorio_log, nombre_archivo_log)

            # 4. Crear el handler apropiado (Rotatorio o Simple)
            if usar_rotacion:
                manejador_archivo = RotatingFileHandler(
                    ruta_completa_archivo,
                    maxBytes=max_bytes_rotacion,
                    backupCount=num_respaldos,
                    encoding='utf-8'
                )
            else:
                manejador_archivo = logging.FileHandler(ruta_completa_archivo, encoding='utf-8')

            # 5. Configurar y añadir el handler
            manejador_archivo.setLevel(nivel_archivo)
            manejador_archivo.setFormatter(formateador_log)
            logger_raiz.addHandler(manejador_archivo)
            _ruta_archivo_log_actual = ruta_completa_archivo # Guardar la ruta configurada con éxito

        except OSError as e_os:
            # Errores de permisos, disco lleno, ruta inválida, etc.
            print(f"\nERROR CRÍTICO (log_config): No se pudo crear/escribir en el directorio/archivo de log.")
            print(f"   Directorio Intentado: {ruta_directorio_log if 'ruta_directorio_log' in locals() else 'Desconocido'}")
            print(f"   Archivo Intentado: {nombre_archivo_log}")
            print(f"   Error del Sistema Operativo: {e_os}\n")
            # Loggear también si es posible (a consola si está activa)
            logging.critical(f"Fallo CRÍTICO configurando log archivo: {e_os}", exc_info=False)

        except Exception as e_gen:
            # Otros errores inesperados
            print(f"\nERROR INESPERADO (log_config): Configurando log de archivo: {e_gen}\n")
            logging.critical(f"Error inesperado configurando log archivo.", exc_info=True)


    # --- Finalizar Configuración y Loguear Estado ---
    _configuracion_realizada = True
    logger_cfg_status = logging.getLogger("ConfigLog") # Logger para estado

    # Loguear información útil sobre las rutas y estado del logging
    logger_cfg_status.info(f"Sistema Logging Configurado ({'Empaquetado' if IS_BUNDLED else 'Desarrollo'}).")
    logger_cfg_status.info(f"  Ruta Base Lectura (Código): {RUTA_BASE_LECTURA}")
    logger_cfg_status.info(f"  Ruta Base Escritura (Logs/Datos/ExtConf): {RUTA_BASE_ESCRITURA}")

    # Estado de los Handlers
    estado_consola = "OFF"
    if log_a_consola:
        estado_consola = f"ON (Nivel >= {logging.getLevelName(nivel_consola)})"

    estado_archivo = "OFF (o error en setup)"
    if _ruta_archivo_log_actual:
        estado_archivo = f"ON (Nivel >= {logging.getLevelName(nivel_archivo)}) en '{_ruta_archivo_log_actual}'"
        if usar_rotacion:
            estado_archivo += f" [Rot: {max_bytes_rotacion/(1024*1024):.1f}MB x{num_respaldos}]"

    logger_cfg_status.info(f"  Estado Salidas -> Consola: {estado_consola} | Archivo: {estado_archivo}")

# ---------------------------------------------------------------------------
# Función para Obtener la Ruta del Log Activo
# ---------------------------------------------------------------------------
def obtener_ruta_archivo_log():
    """
    Devuelve la ruta completa del archivo de log actualmente configurado (si existe).
    Retorna None si el log a archivo no se configuró o falló.
    """
    return _ruta_archivo_log_actual