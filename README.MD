# 🤖 Automatización RPA con Python

Este repositorio presenta una **plantilla técnica reutilizable** para construir bots de RPA robustos y portables utilizando Python, con un enfoque en mantenibilidad, estructura modular y empaquetado profesional con PyInstaller.

> ⚠️ Las URLs, credenciales y lógica de negocio han sido anonimizadas para fines de demostración. No se incluye ningún dato confidencial ni propiedad de terceros.

---

## 🏗️ Arquitectura del Proyecto

La estructura de carpetas sigue principios de separación de responsabilidades, facilitando el mantenimiento y la escalabilidad de cualquier bot:

├── config/         # Configuración de logs y parámetros (ej: credenciales)
├── data/           # Carpeta de salida para informes generados por el bot
├── drivers/        # WebDrivers necesarios para Selenium
├── logs/           # Archivos .log detallados por ejecución
├── scripts/        # Código fuente del bot (main.py y módulos auxiliares)
└── main_rpa.spec   # Archivo de empaquetado PyInstaller (.exe)


## ⚙️ Descripción de los Componentes

### `config/`
- `log_config.py`: Módulo clave que configura el logging y gestiona rutas según se ejecute desde código fuente o `.exe`.
- `credenciales_ejemplo.json`: Archivo ficticio con estructura esperada para credenciales (no contiene datos reales).

### `scripts/`
- `main.py`: Punto de entrada del bot. Orquesta el flujo completo: login, descarga, procesamiento, exportación.
- Modularidad basada en funciones (`realizar_login`, `procesar_reporte_con_pandas`, etc.)

### `drivers/`
- Contiene `chromedriver.exe` necesario para automatización web con Selenium.

### `logs/`
- Se generan automáticamente. Cada ejecución crea un log con timestamp para facilitar la trazabilidad y debugging.

---

## ✨ Características del Código

- ✅ **Modularidad clara**: cada paso de la automatización está separado en funciones específicas.
- ✅ **Manejo de errores robusto** con `try-except-finally`.
- ✅ **Interacción básica con el usuario** mediante `tkinter` (ej: ingreso de fecha).
- ✅ **Procesamiento avanzado con `pandas`**: limpieza, enriquecimiento y exportación de datos.
- ✅ **Logging profesional** en consola y archivo `.log`.

---

## 🧩 Empaquetado como ejecutable (`.exe`)

Este proyecto incluye un archivo `main_rpa.spec` simplificado para crear un ejecutable usando PyInstaller.

### ¿Qué empaqueta?

- El bot principal: `scripts/main.py`
- Configuración: `log_config.py`, `credenciales_ejemplo.json`
- WebDriver: `chromedriver.exe`
- Librerías internas necesarias (ej: `certifi`)
- Soporte para `selenium`, `pandas`, `tkinter`, `numpy`, etc.


