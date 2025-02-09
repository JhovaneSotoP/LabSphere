# LabSphere v1.5.3
LabSphere es un software enfocado a realizar una administracion de casos y muestras en un laboratorio donde se desarrolla DnP y XS. Actualmente se encuentra en desarrollo.

# Codigo de color en QR

  ![#800080](https://placehold.co/15x15/800080/800080.png) `#800080` para flujos del laboratorio (LAB).

![#008080](https://placehold.co/15x15/008080/008080.png) `#008080` para funciones del laboratorio (LAF).

![#FAA500](https://placehold.co/15x15/FAA500/FAA500.png) `#FAA500` para ubicaciones fisicas (LOC).

![#FF0000](https://placehold.co/15x15/FF0000/FF0000.png) `#FF0000` para códigos de usuarios (USR).


# Funciones definidas

- `LAF-SERIALDATA` muestra información sobre la unidad y el proceso de sus muestras.
- `LAF-SAMPLEDATA` muestra información sobre la muestra y los movimientos que ha tenido a traves del tiempo.
- `LAF-INVENTORY` muestra todas las unidades y su respectiva ubicación.
- `LAF-COMMENT` agrega un comentario a la muestra elegida.

# Mejoras
- [ ] Agregar data de usuarios (Cada usuario debe tener un codigo unico).
- [x] Generar copia de seguridad.
- [ ] Corregir error en asignacion de porcentaje de casos.
- [x] Agregar URL del manual a archivo JSON de información general.
- [ ] Generar buffer de registro con opcion para imprimir etiquetas.
- [ ] Generar archivo de inventario al consultar inventario general.
- [ ] Crear funcion para fichar las unidades por EVA.
- [ ] Crear función que evite que el equipo dónde se ejecute entre en modo suspención.