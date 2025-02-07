from generalFuntions_module import serialInput,imprimirTitulo,imprimirExito,imprimirError
from dataBase_module import conexionLab

def locPrincipal(loc):
    
    ubicacion=loc
    imprimirTitulo(F"Register location - {ubicacion}","pink")
    while(1):
        

        temp=input("Please star to scan:").upper()
        temp1=serialInput(temp)

        if(temp1=="E"):
            break

        if temp1=="LOC":
            data=temp.split("-")
            if(len(data)>1):
                ubicacion=data[1]
            
            imprimirTitulo(F"Register location - {ubicacion}","pink")
        else:
            imprimirTitulo(F"Register location - {ubicacion}","pink")
            registrarUbicacion(ubicacion,temp1)

        

def registrarUbicacion(ubicacion,unidad):
    db=conexionLab()
    consulta=db.consultaGeneral("SERIAL","CASES","SERIALPARENT",unidad)
    if db.serialIntoDB(unidad):
        db.actualizarGeneral("CASES","LOCATION",ubicacion,"SERIAL",unidad,"SERIAL",unidad)
        imprimirExito(f"{unidad} registered in {ubicacion}",tiempo=0)
    elif(consulta):
        db.actualizarGeneral("CASES","LOCATION",ubicacion,"SERIALPARENT",unidad,"SERIALPARENT",unidad)
        imprimirExito(f"{unidad} registered in {ubicacion}",tiempo=0)
    else:
        imprimirError(f"{unidad} is not into DB", tiempo=0)