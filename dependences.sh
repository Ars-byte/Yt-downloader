#!/bin/bash

instalar_yt_dlp() {
    echo "Instalando yt_dlp..."
    pip install yt_dlp --break-system-packages
    if [ $? -eq 0 ]; then
        echo "¡yt_dlp se ha instalado correctamente!"
    else
        echo "Error al instalar yt_dlp."
        exit 1
    fi
}

verificar_tkinter() {
    echo "Verificando si tkinter está instalado..."
    python3 -c "import tkinter" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "tkinter ya está instalado."
    else
        echo "tkinter no está instalado."
        echo "Si estás en Linux, instálalo con: sudo apt-get install python3-tk"
    fi
}

instalar_yt_dlp
verificar_tkinter
