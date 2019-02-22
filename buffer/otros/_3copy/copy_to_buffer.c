/**
* 
* The strcpy built-in function does not check buffer lengths and 
* may very well overwrite memory zone contiguous to the intended destination. 
* In fact, the whole family of functions is similarly vulnerable: strcpy, strcat and strcmp.
* 
*
**/

#include <stdio.h>
#include <string.h>

void copyToBuffer(char str[]){

    char buffer[20];
    strcpy(buffer,str);

}
int main( int argc, char* argv[]) {

    if (argc == 0 || argc > 2){
        printf("Error: wrong number of parameters. Use: ./copy_to_buffer <string to copy to buffer>");
        return -1;
    }

    copyToBuffer(argv[1]);
    printf("String copied succesfully!");
    return 0;

}


// Here is where we could play to insert the shell code that I was being told in the video?
// Execute a Hello CICE class?