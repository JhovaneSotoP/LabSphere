import json
import os
from datetime import datetime
from collections import deque
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import time
import re

def imprimirTitulo(text,color):
  console=Console()
  os.system("CLS")
  imprimir=Text(text,style=f"Bold {color}",justify="center")
  panel=Panel(imprimir,height=3)
  console.print(panel)

def imprimirError(text,tiempo=2):
  console=Console()
  console.print(f"[bold red]❌ {text}[/bold red]")
  time.sleep(tiempo)

def imprimirExito(text,tiempo=2):
  console=Console()
  console.print(f"[bold green]✅ {text}[/bold green]")
  time.sleep(tiempo)


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

def serialInput(serial):
  serial=re.split(r"[-, ']", serial)
  return(serial[0])

if __name__=="__main__":
  print(serialInput(input("Prueba de serial: ")))