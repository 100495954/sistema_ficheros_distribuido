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
        operacion = "REGISTER"
        sd = client.socket_cliente()
        if sd == -1:
            return client.RC.ERROR

        # Enviar operación
        if client.enviar(sd, operacion) == -1:
            return client.RC.ERROR

        # Esperar confirmación
        ack = client.recivir(sd, 1)
        if ack != '0':
            print("c> REGISTER FAIL\n")
            return client.RC.ERROR

        # Enviar username
        if client.enviar(sd, user) == -1:
            return client.RC.ERROR

        # Recibir respuesta
        status = client.recivir(sd)
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
        operacion = "UNREGISTER"
        sd = client.socket_cliente()
        if sd == -1:
            return client.RC.ERROR

        # Enviar operación
        if client.enviar(sd, operacion) == -1:
            return client.RC.ERROR

        # Esperar confirmación
        ack = client.recivir(sd, 1)
        if ack != '0':
            print("c> UNREGISTER FAIL\n")
            return client.RC.ERROR

        # Enviar username
        if client.enviar(sd, user) == -1:
            return client.RC.ERROR

        # Recibir respuesta
        status = client.recivir(sd)
        status = int(status)

        if status == 2:
            print("c> UNREGISTER FAIL\n")
            return client.RC.ERROR
        elif status == 1:
            print("c> USER DORES NOT EXISTS\n")
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
        client._listen_thread = threading.Thread(target=client.servicio_cliente, daemon=True).start()

        #4 enviar solicitud de conexión al servidor
        sd = client.socket_cliente()
        if (sd == -1):
            return client.RC.ERROR
        
        # enviar cadena indicando la operacion
        mensaje = "CONNECT\0"
        if (client.send(sd, mensaje) != 0):
            print("Error al enviar la operación\n")

        # enviar cadena indicando el nombre del usuario
        if (client.send(sd, user) != 0):
            print("Error al enviar el nombre del usuario\n")

        # enviar puerto de escucha del cliente como cadena
        if (client.send(sd, str(listen_port)) != 0):
            print("Error al enviar el puerto de escucha\n")

        # recibir byte del servidor
        respuesta = ord(client.recibir(sd))
        if (respuesta == 0):
            print(f"Éxito conectando al usuario {user}\n")
            client._user_connected = user
            print("CONNECT OK\n")
        elif (respuesta == 1):
            print(f"El usuario {user} no existe\n")
            print("CONNECT FAIL, USER DOES NOT EXIST\n")
        elif (respuesta == 2):
            print(f"El usuario {user} ya está conectado\n")
            print("USER ALREADY CONNECTED\n")
        else:
            print("Error al recibir byte del servidor\n")
            print("CONNECT FAIL\n")

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
        if (client.send(sd, mensaje) != 0):
            print("Error al enviar la operación\n")

        # enviar cadena indicando el nombre del usuario
        if (client.send(sd, user) != 0):
            print("Error al enviar el nombre del usuario\n")

        # recibir byte del servidor
        respuesta = ord(client.recibir(sd))
        if (respuesta == 0):
            print(f"Éxito desconectando al usuario {user}\n")
            client._user_connected = None
            print("DISCONNECT OK\n")
        elif (respuesta == 1):
            print(f"El usuario {user} no existe\n")
            print("DISCONNECT FAIL, USER DOES NOT EXIST\n")
        elif (respuesta == 2):
            print(f"El usuario {user} no está conectado\n")
            print("DISCONNECT FAIL, USER NOT CONNECTED\n")
        else:
            print("Error al recibir byte del servidor\n")
            print("DISCONNECT FAIL\n")

        # cerrar la conexión con el servidor
        sd.close()

        # detener el hilo creado por connect
        client._keep_listening = False
        if client._listen_sock:
            try:
                client._listen_sock.close()
            except Exception:
                pass

        client._listen_sock = None
        client._listen_thread = None
        client._user_connected = None

        return client.RC.ERROR

    @staticmethod
    def  publish(fileName,  description) :
        #  Write your code here
        return client.RC.ERROR

    @staticmethod
    def  delete(fileName) :
        #  Write your code here
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
                            client.publish(line[1], description)
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