#include "funciones.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

pthread_mutex_t mutex_server = PTHREAD_MUTEX_INITIALIZER;

struct user *head = NULL;

int register_user(char *username){
    
}