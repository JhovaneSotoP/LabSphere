from generalFuntions_module import imprimirError,imprimirExito,imprimirTitulo, tiempoActual
from rich.console import Console
from dataBase_module import conexionLab
import json
import re



#Cargar flujos del sistema desde el JSON
with open("User Data/data.json", "r") as file:
    flow = json.load(file)

#MODO LABORATORIO


labDB=conexionLab()
def laboratorio(proceso):
    console=Console()
    flujo=proceso
    if flujo=="REGISTER":
        imprimirTitulo("Laboratory","magenta")
        console.print(f"[magenta]Complete the following fields to [bold]REGISTER[/bold] a case[/magenta]")
        serial=input("Enter serial number: ").upper()

        #salir al inicio si se presiona E
        if(serial=="E"):
            print("Saliendo")
            return

        #Comprobar si el serial esta en la base de datos
        if(labDB.serialIntoDB(serial)):
            imprimirError("Serial already in use")
        else:
            
            modelo=input("Enter model: ").upper()

            #salir al inicio si se presiona E
            if(modelo=="E"):
                print("Saliendo")
                return
            
            sap=input("Enter SAP PN: ").upper()

            #salir al inicio si se presiona E
            if(sap=="E"):
                print("Saliendo")
                return
            

            

            tipoProceso=input("Enter type of process: ").upper()

            #salir al inicio si se presiona E
            if(tipoProceso=="E"):
                print("Saliendo")
                return

            #comprobar si el tipo de proceso es las llaves de Flow
            if(tipoProceso in flow.keys()):
                requisitor=input("Enter requisitor: ").upper()

                #salir al inicio si se presiona E
                if(requisitor=="E"):
                    print("Saliendo")
                    return

                MP=input("Enter stage or MP: ").upper()

                #salir al inicio si se presiona E
                if(MP=="E"):
                    print("Saliendo")
                    return

                #Fecha y hora actual
                tiempo=tiempoActual()

                #definir lista de componentes
                componentes=[]

                print("")
                print("Enter componentes separated by , or enter E to finish")

                while(1):
                    component=input("Enter component: ").upper()
                    component=component.split(",")

                    #salir al inicio si se presiona E
                    if(component[0]=="E"):
                      break
                    
                    for n in component:
                        componentes.append(n)

                componentes=list(set(componentes))

                comentario=input("Enter a comment: ")

                #salir al inicio si se presiona E
                if(comentario=="E"):
                    print("Saliendo")
                    return

                if(len(componentes)>0):
                    labDB.registrarCaso(serial,sap,modelo,tipoProceso,requisitor,MP,tiempo,componentes,comentario)
                else:
                    imprimirError("Invalid quantity of components")
                    return

            else:
                imprimirError("Invalid type of process")
                return
    else:
        #extraer todos los flujos existentes
        flujos=[]
        for n in flow.keys():
           for k in flow[n].keys():
              flujos.append(k)

        #Comprobar si el flujo ingresado existe
        if(flujo in flujos):
            imprimirTitulo("Laboratory","magenta")
            console.print(f"[magenta] ➤ [bold]{flujo}[/bold][/magenta]")
            #Escanear el codigo de barras de la muestra
            muestra=input("Scan sample´s barcode:").upper()

            #Procesar el codigo de barras
            muestra=re.split(r"[\'\-]", muestra)

            if(muestra[0]=="E"):
                print("Saliendo")
                return

            if(len(muestra)==1):
                sample=input("Enter sample: ").upper()
                if(sample=="E"):
                    print("Saliendo")
                    return
                muestra.append(sample)
            elif len(muestra)!=2:
                imprimirError("Invalid barcode")
                return

            #comprobar si el serial y muestra estan en la base de datos
            serial=muestra[0]
            sample=muestra[1]

            #Si sample es ALL extraer los nombres de todas las muestras asociadas al serial y tratar de darles el pase


            if(labDB.serialAndSampleIntoDB(serial,sample)):
                #Extraer el actual flujo de la muestra y serial
                currentFlow=labDB.sampleCurrentFlow(serial,sample)
                #Extraer el siguiente flujo de la muestra y serial
                nextFlow=labDB.sampleNextFlow(serial,sample)

                flowStatus=labDB.statusFlow(serial,sample)

                #acciones ante los flujos
                if flujo=="END":
                    #Validar si el siguiente flujo es END
                    if flujo in nextFlow:
                        if flowStatus=="IN":
                          labDB.changeFlowStatus(serial,sample)
                        labDB.toEndSample(serial,sample)
                    else:
                        imprimirError("Serial and sample can´t to END")
                        return
                else:

                    #validar si el flujo de la muestra es el mismo que se quiere registrar

                    if(flujo==currentFlow):
                        if flowStatus=="IN":
                            labDB.changeFlowStatus(serial,sample)
                            imprimirExito(f"Sample {sample} moved to {flujo} OUT")
                        else:
                            imprimirError("Error, this flow is already give it")
                            return
                    #En caso que no y que la muestra tenga flujo out hacer lo siguiente
                    elif(flowStatus=="OUT"):
                        #Si esta el flujo en los siguientes flujos, hacer el cambio
                        if(flujo in nextFlow):
                            labDB.changeFlow(serial,sample,flujo)
                            imprimirExito(f"Sample {sample} moved to {flujo}")
                        else:
                            imprimirError("Error, flow is incorrect")
                            return
                    elif(flowStatus=="IN"):
                        #Si esta el flujo en los siguientes flujos, hacer el cambio aunque no este salida del flujo y hacer el cambio de flujo
                        if(flujo in nextFlow):
                            labDB.changeFlowStatus(serial,sample)
                            labDB.changeFlow(serial,sample,flujo)
                            imprimirExito(f"Sample {sample} moved to {flujo}")
                        else:
                            imprimirError("Error, flow is incorrect")
                            return
                    elif(flowStatus=="N/A"):
                        imprimirError("Error, flow is incorrect")
                        return
                    else:
                        imprimirError("Error, current flow needs to OUT")
                        return


            else:
                imprimirError("Serial and sample is not into DB")
                return

        else:
            imprimirError("Invalid flow")
            return


