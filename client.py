from enum import Enum
import argparse
import socket
import threading

class client :

    # ******************** TYPES *********************
    # *
    # * @brief Return codes for the protocol methods
    class RC(Enum) :
        OK = 0
        ERROR = 1
        USER_ERROR = 2

    # ****************** ATTRIBUTES ******************
    _server = None
    _port = -1
    _listen_sock = None
    _listen_thread = None
    _user_connected = None
    _keep_listening = True

    # ******************** METHODS *******************

    @staticmethod
    def socket_cliente():
        try:
            ip_tuplas = client._server
            port_tuplas = client._port

            if ip_tuplas is None or port_tuplas is None:
                # print("Error en las variables de entorno")
                return -1

            # Crear socket TCP
            sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Conectar al servidor
            sd.connect((ip_tuplas, int(port_tuplas)))

            return sd  # Devuelve el socket conectado

        except Exception as e:
            # print(f"Error: {e}")
            return -1
        
    @staticmethod
    def enviar(sd, mensaje):
        try:
            sd.send(mensaje.encode())
        except Exception as e:
            print(f"Error al enviar: {e}")
            return -1
        return 0

    @staticmethod
    def recibir(sd, buffer = 1024):
        try:
            datos = sd.recv(buffer)
            return datos.decode()  # Convertir de bytes a str
        except Exception as e:
            print(f"Error al recibir: {e}")
            return None

    @staticmethod
    def register(user):
        operacion = "REGISTER\0"
        sd = client.socket_cliente()
        if sd == -1:
            return client.RC.ERROR

        # Enviar operación
        if client.enviar(sd, operacion) == -1:
            return client.RC.ERROR

        # Esperar confirmación
        #ack = client.recibir(sd, 1)
        #if ack != '0':
        #    print("c> REGISTER FAIL\n")
        #    return client.RC.ERROR

        # Enviar username
        if client.enviar(sd, (user + '\0')) == -1:
            return client.RC.ERROR

        # Recibir respuesta
        status = client.recibir(sd)
        status = int(status)

        if status == 2:
            print("c> REGISTER FAIL\n")
            return client.RC.ERROR
        elif status == 1:
            print("c> USERNAME IN USE\n")
            return client.RC.USER_ERROR

        print("c> REGISTER OK\n")
        return client.RC.OK

    
   
    @staticmethod
    def  unregister(user) :
        operacion = "UNREGISTER\0"
        sd = client.socket_cliente()
        if sd == -1:
            return client.RC.ERROR

        # Enviar operación
        if client.enviar(sd, operacion) == -1:
            return client.RC.ERROR

        # Esperar confirmación
        #ack = client.recibir(sd, 1)
        #if ack != '0':
        #    print("c> UNREGISTER FAIL\n")
        #    return client.RC.ERROR

        # Enviar username
        if client.enviar(sd, (user + '\0')) == -1:
            return client.RC.ERROR

        # Recibir respuesta
        status = client.recibir(sd)
        status = int(status)

        if status == 2:
            print("c> UNREGISTER FAIL\n")
            return client.RC.ERROR
        elif status == 1:
            print("c> USER DOES NOT EXIST\n")
            return client.RC.USER_ERROR

        print("c> UNREGISTER OK\n")
        return client.RC.OK

    @staticmethod
    def servicio_cliente():
        while client._keep_listening:
            #manejar peticiones aqui
            print("Hola")
    
    @staticmethod
    def  connect(user) :
        #1 y 2 socket de escucha del cliente, busco puerto válido libre
        client._listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client._listen_sock.bind(('', 0))
        listen_port = client._listen_sock.getsockname()[1]
        client._listen_sock.listen(5)

        #3 hilo para tratar las peticiones de escucha
        # cambiar servicio cliente, por la que realize el servidor
        # de escucha del cliente (q ahora mismo no se cual es)
        #client._listen_thread = threading.Thread(target=client.servicio_cliente, daemon=True).start()

        #4 enviar solicitud de conexión al servidor
        sd = client.socket_cliente()
        if (sd == -1):
            return client.RC.ERROR
        
        # enviar cadena indicando la operacion
        mensaje = "CONNECT\0"
        if (client.enviar(sd, mensaje) != 0):
            print("Error al enviar la operación\n")

        # enviar cadena indicando el nombre del usuario
        if (client.enviar(sd, (user + '\0')) != 0):
            print("Error al enviar el nombre del usuario\n")

        # enviar puerto de escucha del cliente como cadena
        if (client.enviar(sd, (str(listen_port) + '\0')) != 0):
            print("Error al enviar el puerto de escucha\n")

        # recibir byte del servidor
        respuesta = int(client.recibir(sd))
        if (respuesta == 0):
            client._user_connected = user
            print("c> CONNECT OK\n")
        elif (respuesta == 1):
            print("c> CONNECT FAIL, USER DOES NOT EXIST\n")
        elif (respuesta == 2):
            print("c> USER ALREADY CONNECTED\n")
        else:
            print("c> CONNECT FAIL\n")

        # cerrar la conexión con el servidor
        sd.close()

        return client.RC.ERROR
    
    @staticmethod
    def  disconnect(user) :
        #1 conectar al servidor
        sd = client.socket_cliente()
        if (sd == -1):
            return client.RC.ERROR
        
        # enviar cadena indicando la operacion
        mensaje = "DISCONNECT\0"
        if (client.enviar(sd, mensaje) != 0):
            print("Error al enviar la operación\n")

        # enviar cadena indicando el nombre del usuario
        if (client.enviar(sd, (user + '\0')) != 0):
            print("Error al enviar el nombre del usuario\n")

        # recibir byte del servidor
        respuesta = int(client.recibir(sd))
        if (respuesta == 0):
            client._user_connected = None
            print("c> DISCONNECT OK\n")
        elif (respuesta == 1):
            print("c> DISCONNECT FAIL, USER DOES NOT EXIST\n")
        elif (respuesta == 2):
            print("c> DISCONNECT FAIL, USER NOT CONNECTED\n")
        else:
            print("c> DISCONNECT FAIL\n")

        # cerrar la conexión con el servidor
        sd.close()

        # detener el hilo creado por connect
        client._keep_listening = False
        if client._listen_sock:
            try:
                # cerrar el puerto de escucha del cliente
                client._listen_sock.close()
            except Exception:
                pass

        client._listen_sock = None
        client._listen_thread = None
        client._user_connected = None

        return client.RC.ERROR

    @staticmethod
    def  publish(fileName,  description) :
        #1 conectar al servidor
        sd = client.socket_cliente()
        if (sd == -1):
            return client.RC.ERROR
        
        # enviar cadena indicando la operacion
        mensaje = "PUBLISH\0"
        if (client.enviar(sd, mensaje) != 0):
            print("Error al publicar un fichero\n")
            return

        # enviar cadena indicando el nombre del usuario
        if (client.enviar(sd, (client._user_connected + '\0')) != 0):
            print("Error al enviar el nombre del usuario\n")
            return 

        # enviar cadena con el path absoluto del fichero
        if ' ' in fileName:
            print("Error, la ruta contiene espacios en blanco")
            return
        if len(fileName.encode('utf-8')) > 256:
            print("Error, la ruta supera los 256 bytes permitidos")
            return
        if (client.enviar(sd, (fileName + '\0')) != 0):
            print("Error al enviar la ruta del fichero\n")
            return 

        # enviar cadena de caracteres con la descripción del contenido
        if len(description.encode('utf-8')) > 256:
            print("Error, la cadena de caracteres supera los 256 bytes permitidos")
            return
        if (client.enviar(sd, (description + '\0')) != 0):
            print("Error al enviar la descripción del fichero\n")
            return

        # recibir byte del servidor
        respuesta = int(client.recibir(sd))
        if (respuesta == 0):
            print("c> PUBLISH OK\n")
        elif (respuesta == 1):
            print("c> PUBLISH FAIL, USER DOES NOT EXIST\n")
        elif (respuesta == 2):
            print("c> PUBLISH FAIL, USER NOT CONNECTED\n")
        elif (respuesta == 3):
            print("c> PUBLISH FAIL, CONTENT ALREADY PUBLISHED\n")
        else:
            print("c> PUBLISH FAIL\n")

        # cerrar la conexión con el servidor
        sd.close()
        return client.RC.ERROR

    @staticmethod
    def  delete(fileName) :
        #1 conectar al servidor
        sd = client.socket_cliente()
        if (sd == -1):
            return client.RC.ERROR
        
        # enviar cadena indicando la operacion
        mensaje = "DELETE\0"
        if (client.enviar(sd, mensaje) != 0):
            print("Error al publicar un fichero\n")
            return

        # enviar cadena indicando el nombre del usuario
        if (client._user_connected == None):
            user = ""
        else:
            user = client._user_connected
        if (client.enviar(sd, (user + '\0')) != 0):
            print("Error al enviar el nombre del usuario\n")
            return 

        # enviar cadena con el path absoluto del fichero
        if ' ' in fileName:
            print("Error, la ruta contiene espacios en blanco")
            return
        if len(fileName.encode('utf-8')) > 256:
            print("Error, la ruta supera los 256 bytes permitidos")
            return
        if (client.enviar(sd, (fileName + '\0')) != 0):
            print("Error al enviar la ruta del fichero\n")
            return 

        # recibir byte del servidor
        respuesta = int(client.recibir(sd))
        if (respuesta == 0):
            print("c> DELETE OK\n")
        elif (respuesta == 1):
            print("c> DELETE FAIL, USER DOES NOT EXIST\n")
        elif (respuesta == 2):
            print("c> DELETE FAIL, USER NOT CONNECTED\n")
        elif (respuesta == 3):
            print("c> DELETE FAIL, CONTENT NOT PUBLISHED\n")
        else:
            print("c> DELETE FAIL\n")

        # cerrar la conexión con el servidor
        sd.close()
        return client.RC.ERROR

    @staticmethod
    def  listusers() :
        #  Write your code here
        return client.RC.ERROR

    @staticmethod
    def  listcontent(user) :
        #  Write your code here
        return client.RC.ERROR

    @staticmethod
    def  getfile(user,  remote_FileName,  local_FileName) :
        #  Write your code here
        return client.RC.ERROR

    # *
    # **
    # * @brief Command interpreter for the client. It calls the protocol functions.
    @staticmethod
    def shell():

        while (True) :
            try :
                command = input("c> ")
                line = command.split(" ")
                if (len(line) > 0):

                    line[0] = line[0].upper()

                    if (line[0]=="REGISTER") :
                        if (len(line) == 2) :
                            client.register(line[1])
                        else :
                            print("Syntax error. Usage: REGISTER <userName>")

                    elif(line[0]=="UNREGISTER") :
                        if (len(line) == 2) :
                            client.unregister(line[1])
                        else :
                            print("Syntax error. Usage: UNREGISTER <userName>")

                    elif(line[0]=="CONNECT") :
                        if (len(line) == 2) :
                            # Compruebo si ya hay otro usuario conectado previamente
                            if (client._user_connected == None):
                                client.connect(line[1])
                            else:
                                client.disconnect(client._user_connected)
                                client.connect(line[1])
                        else :
                            print("Syntax error. Usage: CONNECT <userName>")
                    
                    elif(line[0]=="PUBLISH") :
                        if (len(line) >= 3) :
                            #  Remove first two words
                            description = ' '.join(line[2:])
                            if client._user_connected != None:
                                client.publish(line[1], description)
                            else:
                                print("No hay ningún usuario conectado\n")
                        else :
                            print("Syntax error. Usage: PUBLISH <fileName> <description>")

                    elif(line[0]=="DELETE") :
                        if (len(line) == 2) :
                            client.delete(line[1])
                        else :
                            print("Syntax error. Usage: DELETE <fileName>")

                    elif(line[0]=="LIST_USERS") :
                        if (len(line) == 1) :
                            client.listusers()
                        else :
                            print("Syntax error. Use: LIST_USERS")

                    elif(line[0]=="LIST_CONTENT") :
                        if (len(line) == 2) :
                            client.listcontent(line[1])
                        else :
                            print("Syntax error. Usage: LIST_CONTENT <userName>")

                    elif(line[0]=="DISCONNECT") :
                        if (len(line) == 2) :
                            client.disconnect(line[1])
                        else :
                            print("Syntax error. Usage: DISCONNECT <userName>")

                    elif(line[0]=="GET_FILE") :
                        if (len(line) == 4) :
                            client.getfile(line[1], line[2], line[3])
                        else :
                            print("Syntax error. Usage: GET_FILE <userName> <remote_fileName> <local_fileName>")

                    elif(line[0]=="QUIT") :
                        if (len(line) == 1) :
                            client.disconnect(client._user_connected)
                            break
                        else :
                            print("Syntax error. Use: QUIT")
                    else :
                        print("Error: command " + line[0] + " not valid.")
            except Exception as e:
                print("Exception: " + str(e))

    # *
    # * @brief Prints program usage
    @staticmethod
    def usage() :
        print("Usage: python3 client.py -s <server> -p <port>")


    # *
    # * @brief Parses program execution arguments
    @staticmethod
    def  parseArguments(argv) :
        parser = argparse.ArgumentParser()
        parser.add_argument('-s', type=str, required=True, help='Server IP')
        parser.add_argument('-p', type=int, required=True, help='Server Port')
        args = parser.parse_args()

        if (args.s is None):
            parser.error("Usage: python3 client.py -s <server> -p <port>")
            return False

        if ((args.p < 1024) or (args.p > 65535)):
            parser.error("Error: Port must be in the range 1024 <= port <= 65535");
            return False;
        
        client._server = args.s
        client._port = args.p

        return True


    # ******************** MAIN *********************
    @staticmethod
    def main(argv) :
        if (not client.parseArguments(argv)) :
            client.usage()
            return

        #  Write code here
        client.shell()
        print("+++ FINISHED +++")
    

if __name__=="__main__":
    client.main([])