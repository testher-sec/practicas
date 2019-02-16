/**
* 
* ./format  %d%d%d
*
*//

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[]) {

  char buffer[64];

  if(argc != 2){
    printf("Error: Wrong number of arguments. Use: format_string.exe <argument>");
	return -1;
  }

  strcpy(buffer, argv[1]);

  printf("Modo correcto:\n");
  printf("%s\n", buffer);

  printf("Modo incorrecto:\n");
  printf(buffer);

  printf("\n");

  return 0;
}