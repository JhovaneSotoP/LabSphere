from dataBase_module import conexionLab
import time
from rich.console import Console
from rich.table import Table
import msvcrt
from generalFuntions_module import imprimirTitulo,imprimirError, imprimirExito,serialInput,samplesInput


db=conexionLab()
def labFuntions(funcion):
    if(funcion=="SERIALDATA"):
        buscarSerialData()
    elif(funcion=="COMMENT"):
        comentarMuestra()
    elif(funcion=="INVENTORY"):
        inventory()
    elif(funcion=="SAMPLEDATA"):
        sampledata()
    elif(funcion=="LOCDETAIL"):
        locdetail()

def buscarSerialData():
    consola=Console()
    imprimirTitulo("Serial data","cyan")
    serial=serialInput(input("Enter a serial: "))
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
        tabla.add_row("Progress",f"{data["percentaje"]:.2f}%")
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
            tabla2.add_row(n,data2[n]["flujoActual"],data2[n]["estadoActual"],data2[n]["siguienteFlujo"],f"{data2[n]["porcentaje"]:.2f}%",data2[n]["comentarios"])
        
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
    data=dict(sorted(data.items()))
    for n in data.keys():
        tabla=Table(title=f"{n} ({len(data[n])})")
        tabla.add_column("Serial")
        tabla.add_column("SAP PN")

        for k in data[n]:
            tabla.add_row(*k)
        
        consola.print(tabla)

    msvcrt.getch()

def sampledata():
    consola=Console()
    imprimirTitulo("SAMPLE DATA","cyan")
    serial=serialInput(input("Enter serial number: "))
    sample=samplesInput(input("Enter sample: "))[0]
    general=db.retornarSamplesData(serial,[sample])
    detail=db.regresarMovimientosSmaple(serial,sample)

    if detail:
        imprimirTitulo(f"{serial}-{sample} DATA","cyan")
        tabla1=Table(title="GENERAL",show_header=False)
        tabla1.add_column("A")
        tabla1.add_column("B")

        tabla1.add_row("Route",general[sample]["flujoActual"])
        tabla1.add_row("Status",general[sample]["estadoActual"])
        tabla1.add_row("Next Route",general[sample]["siguienteFlujo"])
        tabla1.add_row("Percentaje",str(general[sample]["porcentaje"]))
        tabla1.add_row("Comments",general[sample]["comentarios"])
        consola.print(tabla1)

        tabla2=Table(title="DETAIL")
        tabla2.add_column("DATE")
        tabla2.add_column("ENGINEER")
        tabla2.add_column("ROUTE")
        tabla2.add_column("STATUS")

        for n in detail:
            tabla2.add_row(*n)
        
        consola.print(tabla2)
    else:
        imprimirError("There´s no information about this sample")
    msvcrt.getch()
        
def locdetail():
    imprimirTitulo("LOCDETAIL","blue")
    location=input("SCAN LOCATION: ").upper()
    data=db.consultaGeneral("SERIAL","CASES","LOCATION",location)
    consola=Console()
    salida=[]
    for n in data:
        salida.append(db.retornarSerialData(n[0]))
    
    imprimirTitulo(location,"blue")
    tabla=Table(title=f"{len(salida)} units")
    tabla.add_column("SERIAL")
    tabla.add_column("MODEL")
    tabla.add_column("SAP PN")
    tabla.add_column("SERIAL PARENT")
    tabla.add_column("PROCESS")
    tabla.add_column("ROUTE")

    for n in salida:
        tabla.add_row(n["Serial"],n["modelo"],n["sap"],n["serialPadre"],n["tipo"],n["flujoActual"])
    
    consola.print(tabla)
    msvcrt.getch()

        
    