#include <stdio.h>
#include <string.h>
int main(int argc, char *argv[]){
	int i, j;
	char c;
	int result;
	if (argc== 4) {
		i = atoi(argv[1]);
		j = atoi(argv[2]);
		c = atoi(argv[3]);
		if (i<=0 || j<=0 || c<=0) {
			printf("Valores invalidos\n");
		}else {
			result = i + j + c;
			printf("i: %d | j: %d | c: %d | resultado: %d\n", i, j, c, result);
			if (result == 0) {
				printf("Área protegida\n");
			}
		}
	}else {
		printf("Se necesitan tres parametros\n");
		printf("Uso: sample1 param1 param2 param3\n");
	}
	return(0);
}