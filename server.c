
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <signal.h>

pthread_mutex_t sync_mutex;
pthread_cond_t sync_cond;
int sync_copied = 0;


void *tratar_peticion(void *arg) {
    char buffer[1024];
    pthread_mutex_lock(&sync_mutex);
    int sc = *(int *)arg;
    pthread_cond_signal(&sync_cond);
    pthread_mutex_unlock(&sync_mutex);

    memset(buffer, 0, sizeof(buffer));
    int rcv = recv(sc, buffer, sizeof(buffer),0);
    if (rcv<0){
        printf("Error al recibir\n");
    }

    
}

int serverAccept(int sd){
    int sc;
    struct sockaddr_in client_addr;
    socklen_t size;

    size = sizeof(client_addr);
    sc = accept(sd, (struct sockaddr *)&client_addr, (socklen_t *)&size);
    if (sc<0){
        perror("accept: ");
        return -1;
    }

    return sc;
}

int socketServer(unsigned int addr, char *port, int type){
    struct sockaddr_in server_addr;
    int sd = socket(AF_INET, type, 0);
    
    if (sd == -1){
        perror("Error al crear el socket");
        return -1;
    }

    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = addr;
    server_addr.sin_port = htons(atoi(port));

    if(bind(sd,(struct sockaddr*)&server_addr, sizeof(server_addr))<0){
        perror("Error al ejecutar bind");
        close(sd);
        return -1;
    }

    if (listen(sd, SOMAXCONN)<0){
        perror("Error al ejecutar listen");
        close(sd);
        return -1;
    }

    return sd;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Uso: %s <puerto>\n", argv[0]);
        return -1;
    }

    pthread_t thid;
    pthread_attr_t attr;

    if (pthread_mutex_init(&sync_mutex, NULL) != 0) {
        //perror("Error al inicializar el mutex\n");
        return -1;
    }

    if (pthread_cond_init(&sync_cond, NULL)!=0){
        //perror("Error al inicializar la condición\n");
        return -1;
    }

    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);

    int sd = socketServer(INADDR_ANY, argv[1], SOCK_STREAM);
    if (sd < 0) {
        printf("Error al crear el socket del servidor\n");
        return -1;
    }

    printf("Servidor iniciado en el puerto %s\n", argv[1]);

    while (1) {
        int sc = serverAccept(sd);
        if (sc < 0) {
            perror("Error al aceptar conexión");
            continue;  // Reintentar aceptar otra conexión
        }

        printf("Cliente conectado\n");

        if(pthread_create(&thid, &attr, tratar_peticion, (void *)&sc) == -1){
            //perror("Error al crear el hilo.\n");
            close(sc);
            continue;
        }

        pthread_mutex_lock(&sync_mutex);
        while (sync_copied == 0){
            pthread_cond_wait(&sync_cond, &sync_mutex);
        }
        sync_copied = 0;
        pthread_mutex_unlock(&sync_mutex);
    }

    close(sd);  // Esto nunca se ejecuta en este ejemplo, pero es buena práctica
    return 0;
}