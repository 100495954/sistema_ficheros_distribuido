#ifndef FUNCIONES_H
#define FUNCIONES_H

struct file{
    char filename[255];
    char descripcion[255];
    struct file *next;
};

struct user{
    char username[255];
    char ip_route[255];
    int port;
    struct file *file_list;
    struct user *next;
};

int register_user(char *username);

int unregister_user(char *username);

#endif