# Sistema de Intercambio de Archivos Cliente-Servidor

## Descripción

Este proyecto implementa un sistema de intercambio de archivos que consta de un **servidor concurrente escrito en C** y un **cliente escrito en Python**. El sistema permite a los usuarios **registrarse, conectarse, publicar archivos y descargar archivos** de otros usuarios conectados.

La arquitectura es **híbrida**:

* **Servidor Central**: Gestiona la administración de usuarios (registro, estado de conexión) y la publicación de metadatos de los archivos.
* **Peer-to-Peer (P2P)**: Las transferencias de archivos (`GET_FILE`) ocurren directamente entre clientes. La aplicación cliente abre un socket de escucha para servir archivos a otros pares.

---

## Estructura del Proyecto

* **`server.c`**: Punto de entrada principal del servidor. Maneja la creación de hilos y las conexiones entrantes.
* **`funciones.c` / `funciones.h`**: Implementación de la lógica interna del servidor, incluyendo la gestión de listas enlazadas para usuarios y archivos, y la sincronización con mutex.
* **`client.py`**: Aplicación cliente. Maneja la entrada del usuario, se comunica con el servidor central mediante comandos tipo RPC y ejecuta un hilo en segundo plano para atender solicitudes de archivos P2P.
* **`Makefile`**: Script para compilar el servidor en C.

---

## Requisitos Previos

### Servidor

* Compilador **GCC**
* **Make**
* Entorno **Linux/Unix** (utiliza Pthreads y sockets POSIX)

### Cliente

* **Python 3**
* Librería **requests** (para la interacción con el servicio web de fecha y hora)

---

## Compilación

Para compilar el servidor, navega al directorio del proyecto y ejecuta:

```bash
make
```

Para limpiar los archivos objeto compilados y el ejecutable:

```bash
make clean
```

---

## Ejecución

### 1. Iniciar el Servidor

Ejecuta el binario del servidor especificando el puerto de escucha con la bandera `-p`:

```bash
./servidor -p <puerto>
```

Ejemplo:

```bash
./servidor -p 8080
```

### 2. Iniciar el Cliente

Ejecuta el script del cliente en Python especificando la dirección IP del servidor (`-s`) y el puerto (`-p`):

```bash
python3 client.py -s <ip_servidor> -p <puerto_servidor>
```

Ejemplo:

```bash
python3 client.py -s 127.0.0.1 -p 8080
```

---

## Comandos Soportados

Una vez que el cliente está en ejecución, aparecerá un prompt `c>`. Se soportan los siguientes comandos:

### Gestión de Usuarios

* **`REGISTER <nombreUsuario>`**
  Registra un nuevo usuario en el servidor.

* **`UNREGISTER <nombreUsuario>`**
  Elimina el registro de un usuario del servidor.

* **`CONNECT <nombreUsuario>`**
  Conecta a un usuario registrado. También inicia un hilo en segundo plano en el cliente para escuchar solicitudes de archivos.

* **`DISCONNECT <nombreUsuario>`**
  Desconecta al usuario actual y detiene el hilo de escucha.

* **`QUIT`**
  Desconecta al usuario y sale de la aplicación.

### Gestión de Archivos

* **`PUBLISH <nombreArchivo> <descripcion>`**
  Publica un archivo en el servidor. Solo se publican los metadatos (nombre y descripción). El archivo permanece localmente en el cliente.

* **`DELETE <nombreArchivo>`**
  Elimina los metadatos del archivo del servidor.

* **`LIST_USERS`**
  Lista todos los usuarios conectados actualmente.

* **`LIST_CONTENT <nombreUsuario>`**
  Lista los archivos publicados por un usuario específico.

* **`GET_FILE <nombreUsuario> <nombreArchivo_remoto> <nombreArchivo_local>`**
  Descarga un archivo directamente de otro usuario. El archivo remoto se guarda localmente con el nombre indicado.

---

## Detalles Técnicos

### Concurrencia

* **Servidor**: Utiliza un modelo de *pool de hilos* (hilos *detached*) para manejar múltiples conexiones de clientes simultáneamente. La sincronización se gestiona utilizando `pthread_mutex` y `pthread_cond` para proteger las estructuras de datos compartidas.

* **Cliente**: Utiliza el módulo `threading` de Python para ejecutar un socket de escucha en segundo plano (`tratar_peticion`), permitiendo al cliente servir archivos a sus pares mientras emite comandos al servidor central.

### Estructuras de Datos

El servidor mantiene el estado utilizando **listas enlazadas dinámicas**:

* **Lista de Usuarios**: Almacena nombre de usuario, IP, puerto y estado de conexión.
* **Lista de Archivos**: Anidada dentro de cada nodo de usuario, almacenando nombres de archivo y descripciones.

---

## Protocolo

La comunicación utiliza un **protocolo personalizado basado en cadenas sobre TCP**. Las cadenas terminan en carácter nulo (`\0`).

* **Cliente a Servidor**: Envía códigos de operación (ej. `"REGISTER"`, `"CONNECT"`) seguidos de argumentos.
* **Cliente a Cliente**: Para transferencias de archivos, el cliente receptor se conecta a la IP y puerto de escucha del cliente hospedador (obtenidos vía `LIST_USERS`) y solicita el contenido del archivo.

---

## Notas / Problemas Conocidos

* El cliente intenta contactar un servicio web local en `http://127.0.0.1:5000/datetime` durante las operaciones. Si este servicio no está en ejecución, el cliente maneja la excepción pero podría no enviar datos de marca de tiempo.
* Las rutas de los archivos **no deben contener espacios**.
* La longitud máxima para nombres de archivos y descripciones está limitada a **256 bytes**.

