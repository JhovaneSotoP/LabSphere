import json
import re
from datetime import datetime
import sqlite3
from collections import deque


usuario="XXXXXX"

#Cargar flujos del sistema desde el JSON
with open("User Data/data.json", "r") as file:
    flow = json.load(file)

def tiempoActual():
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def bfs_shortest_path(flow_type, start, end):
    with open("User Data/data.json", "r") as file:
        graph = json.load(file)
    
    graph=graph[flow_type]
    # Cola para nodos pendientes de visitar: (nodo_actual, distancia)
    queue = deque([(start, 0)])
    visited = set()  # Nodos visitados

    while queue:
        node, distance = queue.popleft()

        if node == end:
            return distance  # Retornar la distancia al destino

        if node not in visited:
            visited.add(node)
            # Agregar vecinos no visitados a la cola
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    queue.append((neighbor, distance + 1))

    return -1  # Retornar -1 si no hay ruta
#Clase de base de datos para conexion futura
class dataBase():
  def __init__(self):
    #crear base de daros con tabla CASES, SAMPLES y SAMPLES_CHANGES
    self.conn = sqlite3.connect('User Data/data.db')
    self.conn.execute("""CREATE TABLE IF NOT EXISTS CASES(
      SERIAL TEXT PRIMARY KEY,
      CASE_NAME TEXT,
      MODEL TEXT,
      TYPE TEXT,
      SAMPLES_NO INTEGER,
      REQUISITOR TEXT,
      MP TEXT,
      DATE_IN TEXT,
      DATE_OUT TEXT,
      STATUS TEXT,
      PERCENTAGE FLOAT,
      COMMENTS TEXT
    )""")

    self.conn.execute("""CREATE TABLE IF NOT EXISTS SAMPLES(
      ID INTEGER PRIMARY KEY AUTOINCREMENT,
      SERIAL TEXT,
      COMPONENT TEXT,
      DATE_IN TEXT,
      DATE_OUT TEXT,
      FLOW_CUR TEXT,
      FLOW_CUR_STATUS TEXT,
      NEXT_FLOW TEXT,
      PERCENTAGE FLOAT,
      ON_HOLD BOOLEAN,
      PRIORITY BOOLEAN,
      COMMENTS TEXT
    )""")

    self.conn.execute("""CREATE TABLE IF NOT EXISTS SAMPLES_CHANGES(
      ID INTEGER PRIMARY KEY AUTOINCREMENT,
      SAMPLE INTEGER,
      FLOW TEXT,
      FLOW_STATUS TEXT,
      DATE TEXT,
      USER TEXT
    )""")

    self.conn.commit()
    self.conn.close()

  def serialIntoDB(self, serial):
    return False

  def consultarTodo(self,tabla,columna,valor):
    try:
      self.conn = sqlite3.connect('User Data/data.db')
      cursor = self.conn.cursor()
      cursor.execute(f"SELECT * FROM {tabla} WHERE {columna} = '{valor}'")
      result = cursor.fetchone()
      self.conn.close()
      return result
    except:
      return None

  #Pausado
  def registrarCaso(self,serial,case_name,model,type1,samples_no,requisitor,mp,date_in,date_out,status,percentage,comments):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("INSERT INTO CASES VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (serial, case_name, model, type1, samples_no, requisitor, mp, date_in, date_out, status, percentage, comments))
    self.conn.commit()
    self.conn.close()

  def registrarMuestras(self,serial,component,date_in,date_out,flow_cur,next_flow,percentage,on_hold,priority,comments):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("INSERT INTO SAMPLES (SERIAL, COMPONENT, DATE_IN, DATE_OUT, FLOW_CUR,FLOW_CUR_STATUS, NEXT_FLOW, PERCENTAGE, ON_HOLD, PRIORITY, COMMENTS) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (serial, component, date_in,date_out, flow_cur,"OUT", next_flow, percentage, on_hold, priority, comments))
    self.conn.commit()
    self.conn.close()

  def registrarCambio(self,sample,flow,flow_status,date,user):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("INSERT INTO SAMPLES_CHANGES (SAMPLE, FLOW, FLOW_STATUS, DATE, USER) VALUES (?,?,?,?,?)", (sample, flow, flow_status, date, user))
    self.conn.commit()
    self.conn.close()

  #retorna el ultimo case_name que comenzara con RL dentro de la tabla CASES
  def ultimoRL(self):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT CASE_NAME FROM CASES WHERE CASE_NAME LIKE 'RL%' ORDER BY CASE_NAME DESC LIMIT 1")
    result = cursor.fetchone()
    self.conn.close()
    if result:
      return result[0]
    else:
      return None
  def ultimoIDAgregadoSample(self):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT ID FROM SAMPLES ORDER BY ID DESC LIMIT 1")
    result = cursor.fetchone()
    self.conn.close()
    if result:
      return result[0]
    else:
      return None

  #Imprimir toda la informacion de las 3 tablas
  def reporte(self):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT * FROM CASES")
    result = cursor.fetchall()
    print("CASES")
    for row in result:
      print(row)
    cursor.execute("SELECT * FROM SAMPLES")
    result = cursor.fetchall()
    print("SAMPLES")
    for row in result:
      print(row)
    cursor.execute("SELECT * FROM SAMPLES_CHANGES")
    result = cursor.fetchall()
    print("SAMPLES_CHANGES")
    for row in result:
      print(row)
    self.conn.close()

  def consultarSiguienteFlujo(self,serial,sample):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT NEXT_FLOW FROM SAMPLES WHERE SERIAL = ? AND COMPONENT = ?", (serial, sample))
    result = cursor.fetchone()
    print(result)
    self.conn.close()
    if result:
      return result[0]
    else:
      return None

  def flujoActual(self,serial,sample):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT FLOW_CUR FROM SAMPLES WHERE SERIAL = ? AND COMPONENT = ?", (serial, sample))
    result = cursor.fetchone()
    self.conn.close()
    if result:
      return result[0]
    else:
      return None

  def estatusActual(self,serial,sample):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT FLOW_CUR_STATUS FROM SAMPLES WHERE SERIAL = ? AND COMPONENT = ?", (serial, sample))
    result = cursor.fetchone()
    self.conn.close()
    if result:
      return result
    else:
      return None

  def actualizarFlujoSample(self,serial,sample,flow):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("UPDATE SAMPLES SET FLOW_CUR = ? WHERE SERIAL = ? AND COMPONENT = ?", (flow, serial, sample))
    self.conn.commit()
    self.conn.close()

  def actualizarStatusSample(self,serial,sample,status):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("UPDATE SAMPLES SET FLOW_CUR_STATUS = ? WHERE SERIAL = ? AND COMPONENT = ?", (status, serial, sample))
    self.conn.commit()
    self.conn.close()

  def actualizarDateSalida(self,serial,sample,date):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("UPDATE SAMPLES SET DATE_OUT = ? WHERE SERIAL = ? AND COMPONENT = ?", (date, serial, sample))
    self.conn.commit()
    self.conn.close()

  def actualizarSiguienteFlujo(self,serial,sample,flow):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("UPDATE SAMPLES SET NEXT_FLOW = ? WHERE SERIAL = ? AND COMPONENT = ?", (flow, serial, sample))
    self.conn.commit()
    self.conn.close()

  def regresarID(self,serial,sample):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT ID FROM SAMPLES WHERE SERIAL = ? AND COMPONENT = ?", (serial, sample))
    result = cursor.fetchone()
    self.conn.close()
    if result:
      return result[0]
    else:
      return None

  def regresarTipo(self,serial):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT TYPE FROM CASES WHERE SERIAL = ?", (serial,))
    result = cursor.fetchone()
    self.conn.close()
    if result:
      return result[0]
    else:
      return None
  
  def retornarFlujos(self,id):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT FLOW FROM SAMPLES_CHANGES WHERE SAMPLE = ?", (id,))
    result = cursor.fetchall()
    self.conn.close()
    salida=[]
    if result:
      for n in result:
        salida.append(n[0])
    
    vistos=set()
    resultado=[]

    for n in salida:
       if n not in vistos:
          vistos.add(n)
          resultado.append(n)

    return resultado
  
  def actualizarPorcentajeMuestra(self,serial,sample,percentaje):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("UPDATE SAMPLES SET PERCENTAGE = ? WHERE SERIAL = ? AND COMPONENT = ?", (percentaje, serial, sample))
    self.conn.commit()
    self.conn.close()

  def cerrar(self):
    self.conn.close()


#clase conexion lab con base de datos
class conexionLab(dataBase):
    def __init__(self):
        self.dataBase=dataBase()

    #retorna TRUE o False si el serial esta en una hoja de la base de datos usando un metodo del objeto
    def serialIntoDB(self, serial):
        data=self.dataBase.consultarTodo("CASES","SERIAL",serial)
        if data:
            return True
        else:
            return False

    #registar el caso y las muestras, ademas de los movimientos creados
    def registrarCaso(self,serial,modelo,tipoProceso,requisitor,MP,tiempo,componentes):
      #Enviar  SERIAL, CASE_NAME,MODEL, TYPE, SAMPLES_NO, REQUISITOR, MP, DATE_IN, DATE_OUT, STATUS, PERCENTAGE ,COMMENTS
        if str(MP).startswith("MP"):
          case_name=self.dataBase.ultimoRL()
          if case_name:
              case_number=int(case_name[2:])+1
              case_name = "RL" + f"{case_number:03}"
          else:
              case_name="RL001"
        else:
          case_name=MP

        fechaActual=tiempoActual()
        self.dataBase.registrarCaso(serial,case_name,modelo,tipoProceso,len(componentes),requisitor,MP,tiempo,fechaActual,"REGISTER",0.0,"")

        #Registar samples and samples changes
        #SERIAL, COMPONENT ,DATE_IN , DATE_OUT , FLOW_CUR ,NEXT_FLOW ,PERCENTAGE ,ON_HOLD ,PRIORITY ,COMMENTS
        flujosSiguientes=flow[tipoProceso]["REGISTER"]
        flujoConcatenados=""
        for flujo in flujosSiguientes:
          flujoConcatenados+=flujo+", "
        flujoConcatenados=flujoConcatenados[:-2]

        #registrar componentes de la muestra
        for component in componentes:
          fechaActual=tiempoActual()

          #agregar cambios a tabla muestras
          self.dataBase.registrarMuestras(serial,component,tiempo,fechaActual,"REGISTER",flujoConcatenados,0.0,0,0,"")
          id=self.dataBase.ultimoIDAgregadoSample()
          #agregar movimiento in y out en los cambios
          self.dataBase.registrarCambio(id,"REGISTER","IN",tiempo,usuario)
          self.dataBase.registrarCambio(id,"REGISTER","OUT",fechaActual,usuario)


    def serialAndSampleIntoDB(self,serial,sample):
        data=self.dataBase.consultarTodo("SAMPLES","SERIAL",serial)
        if data:
            return True
        else:
            return False

    def sampleNextFlow(self,serial,sample):
        data=self.dataBase.consultarSiguienteFlujo(serial,sample)
        if data:
          return data.split(", ")
        else:
          print("The sample´s flow is already finished")
          return []
    def sampleCurrentFlow(self,serial,sample):
        return self.dataBase.flujoActual(serial,sample)

    def toEndSample(self,serial,sample):
        actual=tiempoActual()
        self.dataBase.actualizarStatusSample(serial,sample,"N/A")
        self.dataBase.actualizarFlujoSample(serial,sample,"END")
        self.dataBase.actualizarDateSalida(serial,sample,actual)
        self.dataBase.actualizarSiguienteFlujo(serial,sample,"")
        id=self.dataBase.regresarID(serial,sample)
        self.dataBase.registrarCambio(id,"END","N/A",actual,usuario)
        self.actualizarPorcentajes(serial,sample)

    def statusFlow(self,serial,sample):
        return self.dataBase.estatusActual(serial,sample)[0]

    def changeFlowStatus(self,serial,sample):
        actual=tiempoActual()
        self.dataBase.actualizarStatusSample(serial,sample,"OUT")

        flujoActual=self.dataBase.flujoActual(serial,sample)
        id=self.dataBase.regresarID(serial,sample)
        self.dataBase.registrarCambio(id,flujoActual,"OUT",actual,usuario)

    def changeFlow(self,serial,sample,newFlow):

        tipo=self.dataBase.regresarTipo(serial)

        siguienteFlujo=flow[tipo][newFlow]
        siguienteConcatenado=""
        for flujo in siguienteFlujo:
          siguienteConcatenado+=flujo+", "
        siguienteConcatenado=siguienteConcatenado[:-2]

        self.dataBase.actualizarFlujoSample(serial,sample,newFlow)
        self.dataBase.actualizarSiguienteFlujo(serial,sample,siguienteConcatenado)
        self.actualizarStatusSample(serial,sample,"IN")

        actual=tiempoActual()
        id=self.dataBase.regresarID(serial,sample)
        self.dataBase.registrarCambio(id,newFlow,"IN",actual,usuario)

        self.actualizarPorcentajes(serial,sample)
    
    def actualizarPorcentajes(self, serial,sample):
       id=self.dataBase.regresarID(serial,sample)
       flujosMuestra=self.dataBase.retornarFlujos(id)
       tipo=self.dataBase.regresarTipo(serial)
       num1=len(flujosMuestra)-1
       num2=bfs_shortest_path(tipo,flujosMuestra[num1],"END")
       promedio=(num1/(num1+num2))*100
       self.dataBase.actualizarPorcentajeMuestra(serial,sample,promedio)
       #Falta modificar el porcentaje del caso, ademas de actualizar el flujo del caso segun el flujo mas bajo






#objetos Globales
labDB=conexionLab()


#MODO LABORATORIO
def laboratorio(proceso):
    flujo=proceso
    if flujo=="REGISTER":
        serial=input("Enter serial number: ").upper()

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
                componentes=list(set(componentes))
                if(len(componentes)>0):
                    labDB.registrarCaso(serial,modelo,tipoProceso,requisitor,MP,tiempo,componentes)
                else:
                    print("Invalid quantity of components")
                    return

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
            muestra=input("Scan sample´s barcode:").upper()

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

                flowStatus=labDB.statusFlow(serial,sample)

                #acciones ante los flujos
                if flujo=="END":
                    #Validar si el siguiente flujo es END
                    if flujo in nextFlow:
                        if flowStatus=="IN":
                          labDB.changeFlowStatus(serial,sample)
                        labDB.toEndSample(serial,sample)
                    else:
                        print("Serial and sample can´t to END")
                        return
                else:

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
                            labDB.changeFlow(serial,sample,flujo)
                        else:
                            print("Error, flow is incorrect")
                            return
                    elif(flowStatus=="IN"):
                        #Si esta el flujo en los siguientes flujos, hacer el cambio aunque no este salida del flujo y hacer el cambio de flujo
                        if(flujo in nextFlow):
                            labDB.changeFlowStatus(serial,sample)
                            labDB.changeFlow(serial,sample,flujo)
                        else:
                            print("Error, flow is incorrect")
                            return
                    elif(flowStatus=="N/A"):
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
    elif(data[0]=="R"):
      tipo=""
      proceso=""
      labDB.dataBase.reporte()
    else:
      print("QR invalido")
      continue

    #Validar tipo
    if tipo=="LAB":
      laboratorio(proceso)
