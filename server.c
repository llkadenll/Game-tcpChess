#include <netdb.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#define PORT 4321
#define BUFFER_SIZE 4

int main(int argc, char** argv) {
    socklen_t slt;
    int sfd, client_white, client_black, on = 1;
    
    struct sockaddr_in saddr, caddr;
    saddr.sin_family = PF_INET;
    saddr.sin_addr.s_addr = INADDR_ANY;
    saddr.sin_port = htons(PORT);

    sfd = socket(PF_INET, SOCK_STREAM, 0);
    if(sfd == -1) {
        printf("Cannot create a new socket\n");
    }

    setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, (char*)&on, sizeof(on));
    if (bind(sfd, (struct sockaddr*)&saddr, sizeof(saddr)) == -1){
        printf("Cannot bind the socket\n");
    }
    
    if (listen(sfd, 2) == 0) {
        printf("Listening...\n");
    } else {
        printf("Error occured during listening\n");
    }

    slt = sizeof(caddr);
    client_white = accept(sfd, (struct sockaddr*)&caddr, &slt);
    if (client_white == -1) {
        printf("Cannot accept the connection");
    }
    printf("new connection: %s\n", inet_ntoa((struct in_addr)caddr.sin_addr));
    write(client_white,"white",6);

    client_black = accept(sfd, (struct sockaddr*)&caddr, &slt);
    if (client_black == -1) {
        printf("Cannot accept the connection");
    }
    printf("new connection: %s\n", inet_ntoa((struct in_addr)caddr.sin_addr));
    write(client_black,"black",6);

    char buffer[BUFFER_SIZE];
    int byte_counter;

    int run = 1;
    while(run) {

        // read from white
        byte_counter = 0;
        while(byte_counter != BUFFER_SIZE){
            byte_counter += read(client_white, &buffer + byte_counter, BUFFER_SIZE - byte_counter);
        }
        printf("%s\n",buffer);
        if (strncmp(buffer,"end!",BUFFER_SIZE) == 0) {
            break;
        }

        // write to black
        byte_counter = 0;
        while(byte_counter != BUFFER_SIZE){
            byte_counter += write(client_black, buffer + byte_counter, BUFFER_SIZE - byte_counter);
        }

        // read from black
        byte_counter = 0;
        while(byte_counter != BUFFER_SIZE){
            byte_counter += read(client_black, &buffer + byte_counter, BUFFER_SIZE - byte_counter);
        }
        printf("%s\n",buffer);
        if (strncmp(buffer,"end!",BUFFER_SIZE) == 0) {
            run = 0;
        }

        // write to white
        byte_counter = 0;
        while(byte_counter != BUFFER_SIZE){
            byte_counter += write(client_white, buffer + byte_counter, BUFFER_SIZE - byte_counter);
        }

    }

    printf("Game Over\n");
    
    close(client_white);
    close(client_black);
    close(sfd);
    return 0;
}