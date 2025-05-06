#include "funciones.h"
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <signal.h>
#include <ifaddrs.h>
#include <netinet/in.h>

pthread_mutex_t sync_mutex;
pthread_cond_t sync_cond;
int sync_copied = 0;


void *tratar_peticion(void *arg) {
    char operacion[1024];
    int status = 2;

    pthread_mutex_lock(&sync_mutex);
    int sc = *(int *)arg;
    sync_copied = 1;
    pthread_cond_signal(&sync_cond);
    pthread_mutex_unlock(&sync_mutex);

    memset(operacion, 0, sizeof(operacion));
    int rcv = recv(sc, operacion, sizeof(operacion), 0);
    if (rcv <= 0) {
        printf("Error al recibir la operación\n");
        close(sc);
        pthread_exit(NULL);
    }

    operacion[rcv] = '\0';

    // Enviar '0' para solicitar username
    char ack = '0';
    if (send(sc, &ack, 1, 0) < 0) {
        printf("Error al enviar ACK\n");
        close(sc);
        pthread_exit(NULL);
    }


    // Lógica según operación
    if (strcmp(operacion, "REGISTER") == 0) {
        char username[255];
        memset(username, 0, sizeof(username));
        rcv = recv(sc, username, sizeof(username), 0);
        if (rcv <= 0) {
            printf("Error al recibir el username\n");
            close(sc);
            pthread_exit(NULL);
        }

        username[rcv] = '\0';
        status = register_user(username);
    } else if (strcmp(operacion, "UNREGISTER") == 0) {
        char username[255];
        memset(username, 0, sizeof(username));
        rcv = recv(sc, username, sizeof(username), 0);
        if (rcv <= 0) {
            printf("Error al recibir el username\n");
            close(sc);
            pthread_exit(NULL);
        }

        username[rcv] = '\0';
        status = unregister_user(username);
    } else {
        printf("Operación no reconocida\n");
    }

    char respuesta[10];
    sprintf(respuesta, "%d", status);
    send(sc, respuesta, strlen(respuesta), 0);

    close(sc);
    pthread_exit(NULL);
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

char *get_local_ip(char *operacion, size_t buflen) {
    struct ifaddrs *ifaddr, *ifa;
    if (getifaddrs(&ifaddr) == -1) return NULL;

    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (!ifa->ifa_addr || ifa->ifa_addr->sa_family != AF_INET) continue;
        if (strcmp(ifa->ifa_name, "lo") == 0) continue; // Ignorar loopback

        struct sockaddr_in *sa = (struct sockaddr_in *)ifa->ifa_addr;
        inet_ntop(AF_INET, &(sa->sin_addr), operacion, buflen);
        freeifaddrs(ifaddr);
        return operacion;
    }

    freeifaddrs(ifaddr);
    return NULL;
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
    if (argc < 3 || strcmp("-p", argv[1])) {
        printf("Uso: %s -p <puerto>\n", argv[0]);
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

    int sd = socketServer(INADDR_ANY, argv[2], SOCK_STREAM);
    if (sd < 0) {
        printf("Error al crear el socket del servidor\n");
        return -1;
    }

    char ip[INET_ADDRSTRLEN];
    if (get_local_ip(ip, sizeof(ip)) != NULL) {
        printf("s > init server %s:%s\n", ip, argv[2]);
    } else {
        printf("s > init server <IP no disponible>:%s\n", argv[2]);
    }
    printf("s>\n");

    while (1) {
        int sc = serverAccept(sd);
        if (sc < 0) {
            perror("Error al aceptar conexión");
            continue;  // Reintentar aceptar otra conexión
        }

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