from generalFuntions_module import serialInput,imprimirTitulo,imprimirExito,imprimirError
from dataBase_module import conexionLab

def locPrincipal(loc):
    
    ubicacion=loc
    while(1):
        imprimirTitulo(F"Register location - {ubicacion}","pink")

        temp=input("Please star to scan:").upper()
        temp1=serialInput(temp)

        if(temp1=="E"):
            break

        if temp1=="LOC":
            data=temp.split("-")
            if(len(data)>1):
                ubicacion=data[1]
        else:
            registrarUbicacion(ubicacion,temp1)

        

def registrarUbicacion(ubicacion,unidad):
    db=conexionLab()
    if db.serialIntoDB(unidad):
        db.actualizarGeneral("CASES","LOCATION",ubicacion,"SERIAL",unidad,"SERIAL",unidad)
        imprimirExito(f"{unidad} registrada con ubicacion {ubicacion}",tiempo=1)
    else:
        imprimirError("Serial is not into DB", tiempo=1)