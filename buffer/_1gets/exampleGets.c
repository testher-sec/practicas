/**
*
*  https://security.web.cern.ch/security/recommendations/en/codetools/c.shtml
* 
* Mitigation: prefer using fgets (and dynamically allocated memory)
*
* $ gcc exampleGets.c helper.c -o example
*
**/

#include <stdio.h>
#include <string.h>
#include "helper.h"

int main() {
	char username[8];
	char allow = 0;

	int diff = username - &allow;

	char *p_username = username;
	char *p_allow = &allow;

	int difference = p_username - p_allow;	

	printf("Address Username %p\n", &username);
	printf("Address Allow %p\n", &allow);
	printf("Difference.... %i\n\n", difference);

	printf("Enter your username, please: ");
	gets(username);
	if (grantAccess(username)) {
		allow = 1;
	}

	if (allow != 0) {
		privilegedAction();
	}

	printf("Username %s\n", username);
	printf("Allow %d\n", allow);

	printf("That's it, game over....");
	return 0;
}