from generalFuntions_module import imprimirError,imprimirExito,imprimirTitulo, tiempoActual,serialInput
from rich.console import Console
from dataBase_module import conexionLab
import json
import re
import time



#Cargar flujos del sistema desde el JSON
with open("User Data/data.json", "r") as file:
    flow = json.load(file)

with open("User Data/general_data.json", "r") as file:
    generalData = json.load(file)

#MODO LABORATORIO


labDB=conexionLab()
def laboratorio(proceso):
    console=Console()
    flujo=proceso
    if flujo=="REGISTER":
        imprimirTitulo("Laboratory","magenta")
        console.print(f"[magenta]Complete the following fields to [bold]REGISTER[/bold] a case[/magenta]")
        serial=serialInput(input("Enter or scan serial number: "))

        #salir al inicio si se presiona E
        if(serial=="E"):
            print("Saliendo")
            return

        #Comprobar si el serial esta en la base de datos
        if(labDB.serialIntoDB(serial)):
            imprimirError("Serial already in use")
        else:
            answer=input("This serial has a serial parent (YES/NO)? ").upper()

            if(answer=="YES"):
                serialParent=serialInput(input("Enter or scan serial parent: "))

                if(serialParent=="E"):
                    print("Saliendo")
                    return
                
                
            elif(answer=="NO"):
                serialParent="N/A"

            
            imprimirTitulo("Laboratory","magenta")
            console.print(f"[magenta] Enter a valid model:[/magenta]")
            for n in generalData["models"]:
                print(f" - {n}")
            print("")
            modelo=input("Enter model: ").upper()

            #salir al inicio si se presiona E
            if(modelo=="E"):
                print("Saliendo")
                return
            
            if not(modelo in generalData["models"]):
                imprimirError("Wrong model")
                return
            
            sap=input("Enter SAP PN: ").upper()

            #salir al inicio si se presiona E
            if(sap=="E"):
                print("Saliendo")
                return
            

            imprimirTitulo("Laboratory","magenta")
            console.print(f"[magenta] Enter a valid process:[/magenta]")
            for n in flow.keys():
                print(f" - {n}")


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
                print("Enter componentes separated by , :")

                
                componentes=input("Enter component: ").upper()
                componentes=componentes.replace(" ","")
                componentes=componentes.split(",")

                #salir al inicio si se presiona E
                if(componentes[0]=="E"):
                    return
                
                while "" in componentes:
                    componentes.remove("")
                
                if len(componentes)==0:
                    imprimirError("Invalid number of samples")
                    return


                componentes=list(set(componentes))

                comentario=input("Enter a comment: ")

                #salir al inicio si se presiona E
                if(comentario=="E"):
                    print("Saliendo")
                    return

                if(len(componentes)>0):
                    labDB.registrarCaso(serial,serialParent,sap,modelo,tipoProceso,requisitor,MP,tiempo,componentes,comentario)
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
            
            #serial

            serial=serialInput(input("Enter serial:"))

            if(serial=="E"):
                print("Saliendo")
                return
            #Escanear el codigo de barras de la muestra
            muestra=input("Scan sample´s:").upper()

            #Procesar el codigo de barras
            muestra=muestra.replace(" ","")
            muestra=muestra.split(",")

            if(muestra[0]=="E"):
                print("Saliendo")
                return


            #Si sample es ALL extraer los nombres de todas las muestras asociadas al serial y tratar de darles el pase

            for sample in muestra:
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
                            imprimirError("Serial and sample can´t to END",tiempo=0)
                            continue
                    else:

                        #validar si el flujo de la muestra es el mismo que se quiere registrar

                        if(flujo==currentFlow):
                            if flowStatus=="IN":
                                labDB.changeFlowStatus(serial,sample)
                                imprimirExito(f"Sample {sample} moved to {flujo} OUT",tiempo=0)
                            else:
                                imprimirError("Error, this flow is already give it",tiempo=0)
                                continue
                        #En caso que no y que la muestra tenga flujo out hacer lo siguiente
                        elif(flowStatus=="OUT"):
                            #Si esta el flujo en los siguientes flujos, hacer el cambio
                            if(flujo in nextFlow):
                                labDB.changeFlow(serial,sample,flujo)
                                imprimirExito(f"Sample {sample} moved to {flujo}",tiempo=0)
                            else:
                                imprimirError("Error, flow is incorrect",tiempo=0)
                                continue
                        elif(flowStatus=="IN"):
                            #Si esta el flujo en los siguientes flujos, hacer el cambio aunque no este salida del flujo y hacer el cambio de flujo
                            if(flujo in nextFlow):
                                labDB.changeFlowStatus(serial,sample)
                                labDB.changeFlow(serial,sample,flujo)
                                imprimirExito(f"Sample {sample} moved to {flujo}",tiempo=0)
                            else:
                                imprimirError("Error, flow is incorrect",tiempo=0)
                                continue
                        elif(flowStatus=="N/A"):
                            imprimirError("Error, flow is incorrect",tiempo=0)
                            continue
                        else:
                            imprimirError("Error, current flow needs to OUT",tiempo=0)
                            continue
                else:
                    imprimirError(f"{serial} and {sample} is not into DB",tiempo=0)
                    continue
            time.sleep(3)


        else:
            imprimirError("Invalid flow")
            return


