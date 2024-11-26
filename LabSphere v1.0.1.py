import json
import re
from datetime import datetime


#Cargar flujos del sistema desde el JSON
with open("User Data/data.json", "r") as file:
    flow = json.load(file)

def tiempoActual():
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#Clase de base de datos para conexion futura
class dataBase():
  def __init__(self):
    pass

  #retorna TRUE o False si el serial esta en la hoja SAMPLES de la base de datos (no desarrollado)
  def serialIntoDB(self, serial):
    return False


#clase conexion lab con base de datos
class conexionLab(dataBase):
    def __init__(self):
        self.dataBase=dataBase()

    #retorna TRUE o False si el serial esta en una hoja de la base de datos usando un metodo del objeto
    def serialIntoDB(self, serial):
        return self.dataBase.serialIntoDB(serial)
    
    #registar el caso y las muestras, ademas de los movimientos creados
    def registrarCaso(self,serial,modelo,tipoProceso,requisitor,MP,tiempo,componentes):
        pass
    
    def serialAndSampleIntoDB(self,serial,sample):
        return True
    
    def sampleNextFlow(self,serial,sample):
        return []
    def sampleCurrentFlow(serial,sample):
        return ""
    
    def toEndSample(self,serial,sample):
        pass

    def statusFlow(self,serial,sample):
        return "IN"
    
    def changeFlowStatus(self,serial,sample):
        pass

    def changeFlow(self,serial,sample):
        pass
    


#objetos Globales
labDB=conexionLab()


#MODO LABORATORIO
def laboratorio(proceso):
    flujo=proceso
    if flujo=="REGISTER":
        serial=input("Enter serial number: ").upper

        #salir al inicio si se presiona E
        if(serial=="E"):
            print("Saliendo")
            return

        #Comprobar si el serial esta en la base de datos
        if(labDB.serialIntoDB(serial)):
            print("Serial already in use")
        else:
            modelo=input("Enter model: ").upper()

            #salir al inicio si se presiona E
            if(modelo=="E"):
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
                while(1):
                    component=input("Enter component: ").upper()

                    #salir al inicio si se presiona E
                    if(component=="E"):
                        print("Saliendo")
                        break

                    componentes.append(component)

                labDB.registrarCaso(serial,modelo,tipoProceso,requisitor,MP,tiempo,componentes)

            else:
                print("Invalid type of process")
                return
    else:
        #extraer todos los flujos existentes
        flujos=[]
        for n in flow.keys():
           for k in flow[n].keys():
              flujos.append(k)
        
        #Comprobar si el flujo ingresado existe
        if(flujo in flujos):
            #Escanear el codigo de barras de la muestra
            muestra=input("Scan sample´s barcode:")

            #Procesar el codigo de barras
            muestra=re.split(r"[\'\-]", muestra)

            if(muestra[0]=="E"):
                print("Saliendo")
                return
           
            if len(muestra)!=2:
                print("Invalid barcode")
                return
            
            #comprobar si el serial y muestra estan en la base de datos
            serial=muestra[0]
            sample=muestra[1]
            if(labDB.serialAndSampleIntoDB(serial,sample)):
                #Extraer el actual flujo de la muestra y serial
                currentFlow=labDB.sampleCurrentFlow(serial,sample)
                #Extraer el siguiente flujo de la muestra y serial
                nextFlow=labDB.sampleNextFlow(serial,sample)
                #acciones ante los flujos
                if flujo=="END":
                    #Validar si el siguiente flujo es END
                    if flujo in nextFlow:
                        labDB.toEndSample(serial,sample)
                    else:
                        print("Serial and sample can´t to END")
                        return
                else:
                    flowStatus=labDB.statusFlow(serial,sample)
                    #validar si el flujo de la muestra es el mismo que se quiere registrar
                    if(flujo==currentFlow):
                        if flowStatus=="IN":
                            labDB.changeFlowStatus(serial,sample)
                        else:
                            print("Error, this flow is already give it")
                            return
                    #En caso que no y que la muestra tenga flujo out hacer lo siguiente
                    elif(flowStatus=="OUT"):
                        #Si esta el flujo en los siguientes flujos, hacer el cambio
                        if(flujo in nextFlow):
                            labDB.changeFlow(sample,flow)
                        else:
                            print("Error, flow is incorrect")
                            return
                    else:
                        print("Error, curretn flow needs to OUT")
                        return
                        
        
            else:
                print("Serial and sample is not into DB")
                return
           
        else:
            print("Invalid flow")
            return




while(1):
  #Solicitar un QR
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
  else:
    print("QR invalido")
    continue

  #Validar tipo
  if tipo=="LAB":
    laboratorio(proceso)
