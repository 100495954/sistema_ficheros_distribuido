#include "funciones.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

pthread_mutex_t mutex_server = PTHREAD_MUTEX_INITIALIZER;

struct user *head = NULL;
struct file *head_file = NULL;

int register_user(char *username){
    struct user *new_user = (struct user *)malloc(sizeof(struct user));
    if (new_user== NULL){
        return 2;
    }
    strncpy(new_user->username , username, sizeof(new_user->username)-1);
    new_user->username[sizeof(new_user->username)-1] = '\0';

    int registrado = 0;

    pthread_mutex_lock(&mutex_server);
    if (head == NULL){
        head = new_user;
    }else{
        struct user *temp = head;
        
        while (temp!=NULL){
            if (strcmp(username, temp->username)==0){
                registrado = 1;
            }
            temp = temp->next;
        }
        if (registrado ==1){
            pthread_mutex_unlock(&mutex_server);
            return 1;
        }
    }
    pthread_mutex_unlock(&mutex_server);
    return 0;
    
}

int unregister_user(char *username){
    pthread_mutex_lock(&mutex_server);
    if (head == NULL){
        pthread_mutex_unlock(&mutex_server);
        return 1;
    }
    struct user *first = head;
    struct user *second = first->next;
    if (strcmp(first->username, username)==0){
        head = second;
        free(first);
        pthread_mutex_unlock(&mutex_server);
        return 0;
    }
    while (second!=NULL){
        if (strcmp(second->username, username)==0){
            first->next = second->next;
            free(second);
            pthread_mutex_unlock(&mutex_server);
            return 0;
        }
        first = first->next;
        second = second->next;
    }
    pthread_mutex_unlock(&mutex_server);
    return 1;
}

// Función que devuelve 1 si encuentra al usuario en 
// la estructura de datos y 2 si no
int exist_user(char *username){
    pthread_mutex_lock(&mutex_server);
    struct user *temp = head;
    while (temp != NULL) {
        if (strcmp(temp->username ,username) == 0){
            // El usuario está registrado
            pthread_mutex_unlock(&mutex_server);
            return 1;
        }
        temp = temp->next;
    }
    pthread_mutex_unlock(&mutex_server);
    return 2;
}

// Función que añade un puerto a un usuario previamente registrado
int connect_user(char *username, int port){
    pthread_mutex_lock(&mutex_server);
    struct user *temp = head;
    while (temp != NULL) {
        if (strcmp(temp->username ,username) == 0){
            // El usuario está registrado
            if (temp->port == 0) {
                // Usuario no conectado
                temp->port = port;
                pthread_mutex_unlock(&mutex_server);
                return 0;
            } else {
                // El usuario ya estaba conectado previamente
                pthread_mutex_unlock(&mutex_server);
                return 2;
            }
        }
        temp = temp->next;
    }
    pthread_mutex_unlock(&mutex_server);
    return -1;
}

// Función que borra el puerto asociado a un usuario previamente
int disconnect_user(char *username){
    pthread_mutex_lock(&mutex_server);
    struct user *temp = head;
    while (temp != NULL) {
        if (strcmp(temp->username ,username) == 0){
            // El usuario está registrado
            if (temp->port != 0) {
                // Usuario conectado
                temp->port = 0;
                pthread_mutex_unlock(&mutex_server);
                return 0;
            } else {
                // El usuario no estaba conectado previamente
                pthread_mutex_unlock(&mutex_server);
                return 2;
            }
        }
        temp = temp->next;
    }
    pthread_mutex_unlock(&mutex_server);
    return -1;
}

int is_connected(char *username) {
    pthread_mutex_lock(&mutex_server);
    struct user *temp = head;
    while (temp != NULL) {
        if (strcmp(temp->username ,username) == 0){
            // El usuario está registrado
            if (temp->port != 0) {
                // El usuario está conectado
                pthread_mutex_unlock(&mutex_server);
                return 1;
            }
            break;
        }
        temp = temp->next;
    }
    // El usuario no está registrado en el sistema
    pthread_mutex_unlock(&mutex_server);
    return 2;
}

int is_published(char *username, char *filename) {
    pthread_mutex_lock(&mutex_server);
    struct user *temp_user = head;
    while (temp_user != NULL) {
        if (strcmp(temp_user->username ,username) == 0){
            // El usuario está registrado
            struct file *temp_file = head_file;
            while (temp_file != NULL) {
                if (strcmp(temp_file->filename, filename) == 0) {
                    // Fichero ya publicado anteriormente
                    pthread_mutex_unlock(&mutex_server);
                    return 3;
                }
                temp_file = temp_file->next;
            }
        }
        temp_user = temp_user->next;
    }
    // El fichero no ha sido publicado por el usuario
    pthread_mutex_unlock(&mutex_server);
    return 1;
}

int publish_file(char *username, char *filename, char *description) {
    pthread_mutex_lock(&mutex_server);
    struct user *temp_user = head;
    while (temp_user != NULL) {
        if (strcmp(temp_user->username ,username) == 0){
            // El usuario está registrado
            struct file *new_file = (struct file *)malloc(sizeof(struct file));
            if (new_file== NULL){
                return -1;
            }
            strncpy(new_file->filename , filename, sizeof(new_file->filename)-1);
            new_file->filename[sizeof(new_file->filename)-1] = '\0';
            strncpy(new_file->description , description, sizeof(new_file->description)-1);
            new_file->description[sizeof(new_file->description)-1] = '\0';
            new_file->next = NULL;

            if (head_file == NULL){
                head_file = new_file;
            }else{
                struct file *temp_file = head_file;
                
                while (temp_file!=NULL){
                    temp_file = temp_file->next;
                }
                temp_file->next = new_file;
            }
            
            temp_user->file_list = new_file;
            pthread_mutex_unlock(&mutex_server);
            return 0;
        }
        temp_user = temp_user->next;
        }
    // El fichero no ha sido publicado por el usuario
    pthread_mutex_unlock(&mutex_server);
    return 1;
}

