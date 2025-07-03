# main_rpa.spec — PyInstaller SPEC simplificado para bots RPA en Python

import os
from PyInstaller.utils.hooks import collect_data_files

# Archivo principal del bot
script_entry_point = os.path.join('scripts', 'main.py')

# Datos del proyecto a incluir manualmente
datas = [
    ('config/log_config.py', 'config'),                  # Módulo de logging
    ('drivers/chromedriver.exe', '.'),                   # WebDriver para Selenium
    ('config/credenciales_ejemplo.json', 'config'),      # Ejemplo de credenciales (sin datos reales)
]

# Agrega datos internos de librerías que los necesitan (como certifi)
datas += collect_data_files('certifi', include_py_files=False)

a = Analysis(
    [script_entry_point],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'selenium',
        'selenium.webdriver.common.by',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'pandas',
        'numpy',
        'tkinter',
    ],
    excludes=[],
)

pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RPA_Ventas',
    debug=False,
    strip=False,
    upx=True,
    console=True  # Cambiar a False si no quieres ventana de consola
)
