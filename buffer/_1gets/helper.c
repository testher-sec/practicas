#include <stdio.h>
#include <string.h>

void privilegedAction() {
	printf("If you got here you are a VIP\n");
}

int grantAccess(char *username) {
	return !strcmp("vipuser", username); //If two strings are same then strcmp() returns 0
}