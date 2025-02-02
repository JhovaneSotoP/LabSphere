from dataBase_module import conexionLab
import time
from rich.console import Console
from rich.table import Table
import msvcrt
from generalFuntions_module import imprimirTitulo,imprimirError, imprimirExito


db=conexionLab()
def labFuntions(funcion):
    if(funcion=="SERIALDATA"):
        buscarSerialData()
    elif(funcion=="COMMENT"):
        comentarMuestra()
    elif(funcion=="INVENTORY"):
        inventory()

def buscarSerialData():
    consola=Console()
    imprimirTitulo("Serial data","cyan")
    serial=input("Enter a serial: ")
    imprimirTitulo("Serial data","cian")
    data=db.retornarSerialData(serial)


    if(data["Componentes"]!=[]):
        tabla=Table(title="General data",show_header=False)

        tabla.add_column("a")
        tabla.add_column("b")
        if serial==data["Serial"]:
            tabla.add_row("Serial",f"[black on_green]{data["Serial"]}[/black on_green]")
            tabla.add_row("Parent Serial",data["serialPadre"])
        else:
            tabla.add_row("Serial",data["Serial"])
            tabla.add_row("Parent Serial",f"[black on_green]{data["serialPadre"]}[/black on_green]")

        

        tabla.add_row("Case",data["caso"])
        tabla.add_row("Requisitor",data["requisitor"])
        tabla.add_row("Model",data["modelo"])
        tabla.add_row("SAP PN",data["sap"])
        tabla.add_row("Process",data["tipo"])
        tabla.add_row("MP/Stage",data["stage"])
        tabla.add_row("Date In",data["fechaEntrada"])
        tabla.add_row("Date Out",data["fechaSalida"])
        tabla.add_row("Status",data["flujoActual"])
        tabla.add_row("Progress",str(data["percentaje"]))
        tabla.add_row("Location",str(data["location"]))
        tabla.add_row("Comments",data["COMMENTS"])
        

        consola.print(tabla)

        data2=db.retornarSamplesData(data["Serial"],data["Componentes"])

        tabla2=Table(title=f"Components of {data["Serial"]} ({len(data["Componentes"])})")
        tabla2.add_column("Component")
        tabla2.add_column("Route")
        tabla2.add_column("Status")
        tabla2.add_column("Next Route")
        tabla2.add_column("Progress")
        tabla2.add_column("Comments")

        for n in data["Componentes"]:
            tabla2.add_row(n,data2[n]["flujoActual"],data2[n]["estadoActual"],data2[n]["siguienteFlujo"],str(data2[n]["porcentaje"]),data2[n]["comentarios"])
        
        consola.print(tabla2)


        

        msvcrt.getch()
    else:
        imprimirError("There´s no information about this serial")



def comentarMuestra():
    imprimirTitulo("Comment sample","pink")
    serial=input("Enter serial number: ").upper()

    #salir al inicio si se presiona E
    if(serial=="E"):
        print("exit...")
        return
    
    sample=input("Enter sample: ").upper()
    #salir al inicio si se presiona E
    if(sample=="E"):
        print("exit...")
        return

    if(db.serialAndSampleIntoDB(serial,sample)):
        comentario=input("Enter a comment:")

        db.agregarComentarioSample(serial,sample,comentario)
        
        
        imprimirExito(f"Comment saved into {serial}-{sample}",tiempo=0)
        msvcrt.getch()
    else:
        imprimirError(f"Sample or serial not found")



def inventory():
    imprimirTitulo("General Inventory","magenta")
    consola=Console()
    data=db.regresarUbicaciones()
    for n in data.keys():
        tabla=Table(title=f"{n} ({len(data[n])})")
        tabla.add_column("Serial")
        tabla.add_column("SAP PN")

        for k in data[n]:
            tabla.add_row(*k)
        
        consola.print(tabla)

    msvcrt.getch()


        
    