from pandas import read_excel as pd
from dataBase_module import dataBase
from generalFuntions_module import tiempoActual,imprimirExito
import json

with open("User Data/data.json", "r") as file:
    flow = json.load(file)

df=pd("User Data/DATA_lab.xlsx",skiprows=0,usecols="A,B,C,D,E,F,G,H,I,J")
db=dataBase()
for n in df.values:
    serial=n[0]
    caso=n[1]
    modelo=n[2]
    sap=n[3]
    proceso=n[4]
    muestrasNo=n[5]
    requisitor=n[6]
    mp=n[7]
    serialPadre=n[8]
    componentes=n[9].split(",")

    try:
        db.registrarCaso(serial,serialPadre,caso,sap,modelo,proceso,muestrasNo,requisitor,mp,tiempoActual(),"","REGISTER",0.0,"")
        for n in componentes:

            flujosSiguientes=flow[proceso]["REGISTER"]
            flujoConcatenados=""
            for flujo in flujosSiguientes:
                flujoConcatenados+=flujo+", "
            
            flujoConcatenados=flujoConcatenados[:-2]

            db.registrarMuestras(serial,n,tiempoActual(),"","REGISTER",flujoConcatenados,0.0,0,0,"")

            id=db.ultimoIDAgregadoSample()
            #agregar movimiento in y out en los cambios
            db.registrarCambio(id,"REGISTER","IN",tiempoActual(),"SYSTEM")
            db.registrarCambio(id,"REGISTER","OUT",tiempoActual(),"SYSTEM")
            imprimirExito(f"Serial {serial} Sample {n} registered, next route {flujoConcatenados}", tiempo=0)
    except Exception as e:
        db.conn.close()
        print(f"Error en {serial}: {e}")

    
