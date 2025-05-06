from enum import Enum
import argparse
import socket

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
    def recivir(sd, buffer = 1024):
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
    def  connect(user) :
        #  Write your code here
        return client.RC.ERROR


    
    @staticmethod
    def  disconnect(user) :
        #  Write your code here
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