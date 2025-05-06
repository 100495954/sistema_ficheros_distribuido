# necesario para la biblioteca compartida
CC = gcc
CFLAGS = -Wall -Wextra -fPIC
# Opciones de enlace para cuando enlazo los archivos objeto
# para generar la biblioteca
LDFLAGS = -lrt -lpthread 
OBJ_SERVER = server.o funciones.o

all: servidor

servidor: $(OBJ_SERVER)
	$(CC) -o servidor $(OBJ_SERVER) $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f *.o servidor

rebuild: clean all
 