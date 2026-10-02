# -*- coding: utf-8 -*-
"""
Script utilitário para instalar o plugin AGERH Hidro Dados diretamente
no diretório de plugins do QGIS do usuário e gerar um arquivo .ZIP para distribuição.
"""

import os
import sys
import shutil
import zipfile

PLUGIN_FOLDER_NAME = "agerh_hidro"
SOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

APPDATA = os.environ.get("APPDATA", "")
QGIS_PLUGINS_DIR = os.path.join(APPDATA, "QGIS", "QGIS3", "profiles", "default", "python", "plugins")
TARGET_DIR = os.path.join(QGIS_PLUGINS_DIR, PLUGIN_FOLDER_NAME)

FILES_TO_COPY = [
    "metadata.txt",
    "__init__.py",
    "agerh_plugin.py",
    "agerh_dialog.py",
    "agerh_service.py",
    "icon.png",
    "README.md",
]


def install():
    print(f"Instalando plugin '{PLUGIN_FOLDER_NAME}'...")
    print(f"Origem:  {SOURCE_DIR}")
    print(f"Destino: {TARGET_DIR}")

    if not os.path.exists(QGIS_PLUGINS_DIR):
        os.makedirs(QGIS_PLUGINS_DIR, exist_ok=True)

    os.makedirs(TARGET_DIR, exist_ok=True)

    for fname in FILES_TO_COPY:
        src = os.path.join(SOURCE_DIR, fname)
        dst = os.path.join(TARGET_DIR, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  [OK] Copiado: {fname}")
        else:
            print(f"  [AVISO] Arquivo não encontrado: {fname}")

    print("\n✅ Plugin instalado com sucesso no QGIS!")


def create_zip():
    zip_path = os.path.join(SOURCE_DIR, f"{PLUGIN_FOLDER_NAME}.zip")
    print(f"\nGerando pacote ZIP para distribuição: {zip_path}")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in FILES_TO_COPY:
            fpath = os.path.join(SOURCE_DIR, fname)
            if os.path.exists(fpath):
                arcname = os.path.join(PLUGIN_FOLDER_NAME, fname)
                zf.write(fpath, arcname)
                print(f"  [ZIP] Adicionado: {arcname}")
    print(f"✅ Pacote ZIP criado com sucesso: {zip_path}")
    return zip_path


if __name__ == "__main__":
    install()
    create_zip()

