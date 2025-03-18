#!/bin/bash

instalar_yt_dlp() {
    echo "Installing yt_dlp..."
    pip install yt_dlp --break-system-packages
    if [ $? -eq 0 ]; then
        echo "¡yt_dlp has been installed correctly"
    else
        echo "Error"
        exit 1
    fi
}

verificar_tkinter() {
    echo "Checking if tkinter is installed..."
    python3 -c "import tkinter" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "Tkinter is already installed"
    else
        echo "tkinter is not installed"
        echo "If you're on Linux, install it with: sudo apt-get install python3-tk"
    fi
}

instalar_yt_dlp
verificar_tkinter
