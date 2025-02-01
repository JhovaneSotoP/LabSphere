import sqlite3
from datetime import datetime
import time
import json



from generalFuntions_module import imprimirExito,imprimirError,bfs_shortest_path


usuario=""

with open("User Data/data.json", "r") as file:
    flow = json.load(file)

def actualizarUsuario(user):
  global usuario
  usuario=user

def tiempoActual():
  return datetime.now().strftime('%Y-%m-%d %H:%M:%S')



#Clase de base de datos para conexion futura
class dataBase():
  def __init__(self):
    #crear base de daros con tabla CASES, SAMPLES y SAMPLES_CHANGES
    self.conn = sqlite3.connect('User Data/data.db')
    self.conn.execute("""CREATE TABLE IF NOT EXISTS CASES(
      SERIAL TEXT PRIMARY KEY,
      SERIALPARENT TEXT,
      CASE_NAME TEXT,
      MODEL TEXT,
      PN_SAP TEXT,
      TYPE TEXT,
      SAMPLES_NO INTEGER,
      REQUISITOR TEXT,
      MP TEXT,
      DATE_IN TEXT,
      DATE_OUT TEXT,
      STATUS TEXT,
      PERCENTAGE FLOAT,
      COMMENTS TEXT,
      LOCATION TEXT
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
      USER TEXT,
      COMMENTS TEXT
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
  
  def consultaGeneral(self,datoBuscado,tabla,columnaValor,valor):
    try:
      self.conn = sqlite3.connect('User Data/data.db')
      cursor = self.conn.cursor()
      cursor.execute(f"SELECT {datoBuscado} FROM {tabla} WHERE {columnaValor} = '{valor}'")
      result = cursor.fetchall()
      self.conn.close()
      return result
    except:
      return None
  
  def consultaGeneralDos(self,datoBuscado,tabla,columnaValor1,valor1,columnaValor2,valor2):
    try:
      self.conn = sqlite3.connect('User Data/data.db')
      cursor = self.conn.cursor()
      cursor.execute(f"SELECT {datoBuscado} FROM {tabla} WHERE {columnaValor1} = '{valor1}' AND {columnaValor2} = '{valor2}'")
      result = cursor.fetchall()
      self.conn.close()
      return result
    except:
      return None
  
  def consultaTodo3columnas(self,columnas1,columna2,columna3,tabla):
    try:
      self.conn = sqlite3.connect('User Data/data.db')
      cursor = self.conn.cursor()
      cursor.execute(f"SELECT {columnas1},{columna2},{columna3} FROM {tabla}")
      result = cursor.fetchall()
      self.conn.close()
      return result
    except Exception as e:
      print(e)
      return None
  
  def actualizarGeneral(self,tabla,columna,dato,columnaCondicion1,valorCondicion1,columnaCondicion2,valorCondicion2):
    try:
      self.conn = sqlite3.connect('User Data/data.db')
      cursor = self.conn.cursor()
      query = f"UPDATE {tabla} SET {columna} = ? WHERE {columnaCondicion1} = ? AND {columnaCondicion2} = ?"
      params = (dato, valorCondicion1, valorCondicion2)
      cursor.execute(query, params)
      self.conn.commit()
      self.conn.close()
    except Exception as e:
      print(e)
      self.conn.close()

  #Pausado
  def registrarCaso(self,serial,serialParent,case_name,sap,model,type1,samples_no,requisitor,mp,date_in,date_out,status,percentage,comments):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("INSERT INTO CASES VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (serial,serialParent, case_name, model,sap, type1, samples_no, requisitor, mp, date_in, date_out, status, percentage, comments,"UNDEFINED"))
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
    cursor.execute("SELECT CASE_NAME FROM CASES WHERE CASE_NAME LIKE 'RMP%' ORDER BY CASE_NAME DESC LIMIT 1")
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

  def actualizarPorcentajeCaso(self,serial,percentaje):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("UPDATE CASES SET PERCENTAGE = ? WHERE SERIAL = ?", (percentaje, serial))
    self.conn.commit()
    self.conn.close()

  def muestrasPorcentaje(self,serial):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT PERCENTAGE FROM SAMPLES WHERE SERIAL = ?", (serial,))
    result = cursor.fetchall()
    self.conn.close()

    salida=[]
    for n in result:
       salida.append(result[0])

    return salida

  def extraerFlujoMenor(self,serial):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("SELECT FLOW_CUR FROM SAMPLES WHERE SERIAL = ? ORDER BY PERCENTAGE ASC LIMIT 1", (serial,))
    result = cursor.fetchall()
    self.conn.close()
    return result

  def actualizarFlujoCaso(self,serial,flujo):
    self.conn = sqlite3.connect('User Data/data.db')
    cursor = self.conn.cursor()
    cursor.execute("UPDATE CASES SET STATUS = ? WHERE SERIAL = ?", (flujo, serial))
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
    def registrarCaso(self,serial,serialParent,sap,modelo,tipoProceso,requisitor,MP,tiempo,componentes,comentario):
      #Enviar  SERIAL, CASE_NAME,MODEL, TYPE, SAMPLES_NO, REQUISITOR, MP, DATE_IN, DATE_OUT, STATUS, PERCENTAGE ,COMMENTS
        if str(MP).startswith("MP"):
          case_name=self.dataBase.ultimoRL()
          if case_name:
              print(case_name)
              case_number=int(case_name[3:])+1
              case_name = "RMP" + f"{case_number:03}"
          else:
              case_name="RMP001"
        else:
          case_name=MP

        fechaActual=tiempoActual()
        self.dataBase.registrarCaso(serial,serialParent,case_name,sap,modelo,tipoProceso,len(componentes),requisitor,MP,tiempo,"","REGISTER",0.0,comentario)
        imprimirExito(f"Case {case_name} registered", tiempo=0)

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
          self.dataBase.registrarMuestras(serial,component,tiempo,"","REGISTER",flujoConcatenados,0.0,0,0,"")
          id=self.dataBase.ultimoIDAgregadoSample()
          #agregar movimiento in y out en los cambios
          self.dataBase.registrarCambio(id,"REGISTER","IN",tiempo,usuario)
          self.dataBase.registrarCambio(id,"REGISTER","OUT",fechaActual,usuario)
          imprimirExito(f"Sample {component} registered", tiempo=0)
        time.sleep(2)

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
          imprimirError("The sample´s flow is already finished")
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
      total=0
      data=self.dataBase.muestrasPorcentaje(serial)
      for n in data:
        total+=n[0]
      promedio=total/len(data)

      self.dataBase.actualizarPorcentajeCaso(serial,promedio)
      self.dataBase.actualizarFlujoCaso(serial,self.dataBase.extraerFlujoMenor(serial)[0][0])



    def retornarSerialData(self,serial):
      dict={}
      dict.update({"Serial":serial})

      #extraer caso
      temp=self.dataBase.consultaGeneral("CASE_NAME","CASES","SERIAL",serial)
      if temp:
        dict.update({"caso":temp[0][0]})
      
      #extraer sap
      temp=self.dataBase.consultaGeneral("PN_SAP","CASES","SERIAL",serial)
      if temp:
        dict.update({"sap":temp[0][0]})
      
      #extraer modelo
      temp=self.dataBase.consultaGeneral("MODEL","CASES","SERIAL",serial)
      if temp:
        dict.update({"modelo":temp[0][0]})
      
      #extraer TIPO
      temp=self.dataBase.consultaGeneral("TYPE","CASES","SERIAL",serial)
      if temp:
        dict.update({"tipo":temp[0][0]})

      #extraer requisitor
      temp=self.dataBase.consultaGeneral("REQUISITOR","CASES","SERIAL",serial)
      if temp:
        dict.update({"requisitor":temp[0][0]})
      
      #extraer a que pertenece
      temp=self.dataBase.consultaGeneral("MP","CASES","SERIAL",serial)
      if temp:
        dict.update({"stage":temp[0][0]})



      #extraer componentes
      componentes=[]
      for n in self.dataBase.consultaGeneral("COMPONENT","SAMPLES","SERIAL",serial):
        componentes.append(n[0])

      dict.update({"Componentes":componentes})

      #extraer fecha de registro
      date=self.dataBase.consultaGeneral("DATE_IN","CASES","SERIAL",serial)
      if date:
        dict.update({"fechaEntrada":date[0][0]})

      #extraer fecha de salida
      date=self.dataBase.consultaGeneral("DATE_OUT","CASES","SERIAL",serial)
      if date:
        dict.update({"fechaSalida":date[0][0]})
      else:
        dict.update({"fechaSalida":"- - -"})
      
      #extraer flujo actual
      flou=self.dataBase.consultaGeneral("STATUS","CASES","SERIAL",serial)
      if flou:
        dict.update({"flujoActual":flou[0][0]})
      
      #extraer comentrarios
      percentaje=self.dataBase.consultaGeneral("PERCENTAGE","CASES","SERIAL",serial)
      if percentaje:
        dict.update({"percentaje":percentaje[0][0]})

      #extraer comentrarios
      comment=self.dataBase.consultaGeneral("COMMENTS","CASES","SERIAL",serial)
      if comment:
        dict.update({"COMMENTS":comment[0][0]})
      
      #extraer ubicacion
      temp=self.dataBase.consultaGeneral("LOCATION","CASES","SERIAL",serial)
      if temp:
        dict.update({"location":temp[0][0]})

      #extraer serial padre
      temp=self.dataBase.consultaGeneral("SERIALPARENT","CASES","SERIAL",serial)
      if temp:
        dict.update({"serialPadre":temp[0][0]})

      return dict
    
    def retornarSamplesData(self,serial,samples):
      salida={}
      for n in samples:
        temp={}

        #Extraer flujo
        data=self.dataBase.consultaGeneralDos("FLOW_CUR","SAMPLES","SERIAL",serial,"COMPONENT",n)
        if data:
          temp.update({"flujoActual":data[0][0]})
        
        #Extraer estado
        data=self.dataBase.consultaGeneralDos("FLOW_CUR_STATUS","SAMPLES","SERIAL",serial,"COMPONENT",n)
        if data:
          temp.update({"estadoActual":data[0][0]})
        
        #Extraer siguiente flujo
        data=self.dataBase.consultaGeneralDos("NEXT_FLOW","SAMPLES","SERIAL",serial,"COMPONENT",n)
        if data:
          temp.update({"siguienteFlujo":data[0][0]})
        
        #Extraer porcentaje
        data=self.dataBase.consultaGeneralDos("PERCENTAGE","SAMPLES","SERIAL",serial,"COMPONENT",n)
        if data:
          temp.update({"porcentaje":data[0][0]})
        
        #Extraer comentarios
        data=self.dataBase.consultaGeneralDos("COMMENTS","SAMPLES","SERIAL",serial,"COMPONENT",n)
        if data:
          temp.update({"comentarios":data[0][0]})
        
        
        
        

        salida.update({n:temp})
      
      return salida
    
    def agregarComentarioSample(self,serial,sample,comentario):
      self.dataBase.actualizarGeneral("SAMPLES","COMMENTS",comentario,"SERIAL",serial,"COMPONENT",sample)
    
    def regresarUbicaciones(self):
      consulta=self.dataBase.consultaTodo3columnas("SERIAL","LOCATION","PN_SAP","CASES")
      salida={}
      if consulta:
        for n in consulta:
          try:
            salida[n[1]]+=[[n[0],n[2]]]
          except:
            salida.update({n[1]:[[n[0],n[2]]]})
        return salida
      else:
        return None


    




