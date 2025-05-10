#ifndef FUNCIONES_H
#define FUNCIONES_H

struct file{
    char filename[255];
    char description[255];
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

int exist_user(char *username);

int connect_user(char *username, int port);

int disconnect_user(char *username);

int is_connected(char *username);

int is_published(char *username, char *filename);

int publish_file(char *username, char *filename, char *description);

int delete_file(char *username, char *filename);

int list_users(char *username, struct user **lista_usuarios);

int connected_count(char *username);

#endif