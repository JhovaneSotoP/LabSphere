from collections import deque
import json


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

#print(bfs_shortest_path("DNP","REGISTER","END"))

