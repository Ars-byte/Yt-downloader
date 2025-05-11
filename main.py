
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import yt_dlp

ventana = tk.Tk()
ventana.title("YTDOWNLOADER")
ventana.configure(bg='#000000')


ttk.Style().configure('Etiqueta.TLabel', font=('Arial', 12), foreground='black', background='gray')
ttk.Style().configure('Entry.TEntry', font=('Arial', 12), foreground='black', background='gray')
ttk.Style().configure('Boton.TButton', font=('Arial', 12), foreground='red', background='gray')

etiqueta_url = ttk.Label(ventana, text="Enter the URL (Only Youtube):", style='Etiqueta.TLabel')
etiqueta_url.pack(pady=10)

entrada_url = ttk.Entry(ventana, width=30, style='Entry.TEntry')
entrada_url.pack()

def descargar_video():
    url = entrada_url.get()
    try:
        yt_dlp.YoutubeDL().download([url])
        messagebox.showinfo("Éxito", "Descarga completa")
    except Exception as e:
        messagebox.showerror("Error", str(e))

boton_descargar = ttk.Button(ventana, text="Descargar", command=descargar_video, style='Boton.TButton')
boton_descargar.pack(pady=10)

ventana.mainloop()
