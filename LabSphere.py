import json
import re
import os
import shutil
from datetime import datetime
import sqlite3
from collections import deque
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.markdown import Markdown
from rich.tree import Tree
from rich.json import JSON
from rich.panel import Panel
from rich.syntax import Syntax
from rich.spinner import Spinner
from rich.layout import Layout
from rich.align import Align
from rich.bar import Bar
from rich.text import Text
from rich.rule import Rule
import time


from laboratorio_module import laboratorio
from dataBase_module import conexionLab,actualizarUsuario
from labFuntions_module import labFuntions
from locFuntions_module import locPrincipal
from generalFuntions_module import imprimirError,imprimirExito, imprimirTitulo, tiempoActual

usuario="XXXXXX"


console=Console()

def modoUsuario(data):
  if data=="SYSTEM":
    return data
  else:
    return None

with open("User Data/general_data.json", "r") as file:
    generalData = json.load(file)
#FUNCIONES DE VISTA

def imprimirInicio():
  os.system("CLS")
  titulo = Text("◆ LabSphere " + generalData["version"] + " ◆", style="bold cyan", justify="center")

  desarrollador=Text("● Support: ", style="green",justify="left")
  desarrollador.append("jhovane.soto@fii-na.com", style="white")

  manual=Text("Click ",style="white", justify="left")
  manual.append("here", style=f"magenta link {generalData["userManual"]}")
  manual.append(" to open user manual", style="white")

  usuario_cad = Text("\n ‣ User: " + usuario, style="white", justify="left")

  layout = Layout()

  layout.split(
      Layout(name="titulo", ratio=1),
      Layout(name="desarollador", ratio=1),
      Layout(name="manual", ratio=1),
      Layout(name="usuario_cad", ratio=1),
  )

  layout["titulo"].update(titulo)
  layout["manual"].update(manual)
  layout["desarollador"].update(desarrollador)
  layout["usuario_cad"].update(usuario_cad)

  # Crear el panel con el layout ya creado
  panel = Panel(layout, height=10)
  console.print(panel)



#Cargar flujos del sistema desde el JSON
with open("User Data/data.json", "r") as file:
    flow = json.load(file)




def respaldo():
  os.makedirs("User Data/Respaldo/",exist_ok=True)
  try:
    shutil.copy("User Data/data.db",f"User Data/Respaldo/database_{tiempoActual()[0:10]}.db")
  except Exception as e:
    print(e)
    time.sleep(3)

#objetos Globales
labDB=conexionLab()



respaldo()
while(1):
    #Solicitar un QR
    while(usuario=="XXXXXX"):
      imprimirInicio()
      data=input("Scan a user code to continue: ").upper()
      data=re.split(r"[\'\-]", data)

      if(len(data)==2):
        tipo=data[0]
        proceso=data[1]
        if(tipo=="USR"):
            temp=modoUsuario(proceso)
            if temp:
              usuario=proceso
              actualizarUsuario(proceso)
            else:
              imprimirError("User no recognized")
      elif(data[0]=="E"):
        print("Saliendo")
        break

    if(data[0]=="E"):
        print("Saliendo")
        break

    imprimirInicio()
    data=input("Scan a QR to continue: ").upper()
    #Procesar QR
    data=re.split(r"[\'\-]", data)

    #validar dato leido al inicio
    if(len(data)==2):
      tipo=data[0]
      proceso=data[1]
    elif(data[0]=="E"):
      print("Saliendo")
      break
    elif(data[0]=="R"):
      tipo=""
      proceso=""
      labDB.dataBase.reporte()
      time.sleep(5)
    else:
      imprimirError("Invalid QR")
      continue



    if tipo=="LAB":
      laboratorio(proceso)
    elif(tipo=="LAF"):
      labFuntions(proceso)
    elif(tipo=="LOC"):
      locPrincipal(proceso)
    elif(tipo=="USR"):
      temp=modoUsuario(proceso)
      if temp:
        usuario=proceso
        actualizarUsuario(proceso)
      else:
        imprimirError("User no recognized")

