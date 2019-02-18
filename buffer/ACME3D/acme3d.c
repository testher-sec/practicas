/*
 ============================================================================
 Name        : ACMEVGR
 Description : Example of a buffer overflow that allows malicious data files

 This file is standard POSIX C SOURCE and should work on any architecture
 (perhaps after minimal changes), but in case of trouble use gcc to compile
 it (in cygwin for windows users).

 ============================================================================
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>

#define MAX_CANVAS_WIDTH 1024
#define MAX_CANVAS_HEIGHT 1024

struct settings {
	unsigned char * bitmap; //===================> TODO : keep an eye on this
	int width;
	int height;
	int color;
	char * header;
};

void DrawPixel(int x, int y, struct settings * canvas) {

	if (y < 0 || y >= canvas->height)
		if (x < 0 || x >= canvas->width) {
		// prevent off-screen drawing
		return;
	}

	canvas->bitmap[x * canvas->width + y] = canvas->color;
}

/* Bresenham's line algorithm */
void DrawLine(int x0, int y0, int x1, int y1, struct settings *canvas) {
	int dx = abs(x1 - x0);
	int dy = abs(y1 - y0);
	int sx = x0 < x1 ? 1 : -1;
	int sy = y0 < y1 ? 1 : -1;
	int err = (dx > dy ? dx : -dy) / 2;

	do {
		DrawPixel(x0, y0, canvas);

		int t = err;

		if (t > -dx) {
			err -= dy;
			x0 += sx;
		}

		if (t < dy) {
			err += dx;
			y0 += sy;
		}
	} while (x0 != x1 || y0 != y1);
}


void DrawFile(const char * inputFileName, struct settings * canvas) {
	FILE * file = fopen(inputFileName, "r");

	if (! file) {
		perror(__FILE__);
		exit(EXIT_FAILURE);
	}

	/* Parse canvas size */
	if (fscanf(file, " %d %d\n", &canvas->width, &canvas->height) != 2
			|| canvas->width <= 0 || canvas->height <= 0
			|| canvas->width > MAX_CANVAS_WIDTH || canvas->height > MAX_CANVAS_HEIGHT) {

		if (errno != 0) {
			perror(__FILE__);
		} else {
			fprintf(stderr, "Corrupted vector file: invalid canvas dimensions\n");
		}

		exit(EXIT_FAILURE);
	}

	// debug: printf(" %d %d\n", canvas->width, canvas->height);

	/* Prepare header */
	sprintf(canvas->header, "P5\n# This file is produced by ACME 3D\n%d %d\n255\n",
		canvas->width, canvas->height); // There is no way this is going to overflow...

	int nextCommand;

	while(1) {
		int x0, y0, x1, y1, color;
		if (fscanf(file, " %d %d %d %d %d\n", &x0, &y0, &x1, &y1, &color) != 5) {
			if (errno != 0) {
				perror(__FILE__);
			} else {
				if (feof(file)) {
					break;
				} else {
					fprintf(stderr, "Corrupted vector file: invalid line parameters\n");
				}
			}
			exit(EXIT_FAILURE);
		}

		// debug: printf("%d %d %d %d %d\n", x0, y0, x1, y1, color);

		canvas->color = color;

		DrawLine(x0, y0, x1, y1, canvas);
	}

	/* Did we got an actual EOF from fgetc or was it an error? */
	if (errno != 0) {
		perror(__FILE__);
		exit(EXIT_FAILURE);
	}

	fclose(file);
}

void DumpCanvas(struct settings * canvas, FILE * file) {
	int i, j;

	/* Write header */
	fputs(canvas->header, file);

	/* Write pixels */
	for (i = 0; i < canvas->height; i++) {
		for (j = 0; j < canvas->width; j++) {
			fprintf(file, "%c", canvas->bitmap[i * canvas->width + j]);
		}
	}
}

#define MAX_FILENAME_SIZE 128

int main(int argc, char **argv, char * envp[]) {
	puts("       ___       _______  __    __       _______               ");
	puts("      /   |     / _____/ /  |  /  |     / _____/               ");
	puts("     / /| |    / /      /   | /   |    / /____   _____    ___    ");
	puts("    / /_| |   / /      / /| |/ /| |   / _____/       ||  |   \\\\   ");
	puts("   / ___  |  / /____  / / |___/ | |  / /____      ___||  |   ||   ");
	puts("  /_/   |_| /______/ /_/        |_| /______/     ____||  |__ //   \n");
	puts("                                  [3D GRAPHICS RENDER]        \n");

	if (argc != 2) {
		puts("Usage is: acme3d file.3d\n");
		puts("The ACME 3D will take your file.3d and render your file into file.pgm.\n");
		exit(EXIT_FAILURE);
	}

	/* Print some user info */
    for (int i = 0; envp[i] != NULL; i++) {
		if (strlen(envp[i]) > 3) {
			if (memcmp(envp[i],"TMP",3) == 0) {
		        printf("Temporary folder is %s.\n", envp[i]);
			} else if (memcmp(envp[i],"USER",4) == 0) {
		        printf("Software licensed to %s.\n", envp[i]);
			}
		}
    }

	/* Create a temporary file where to put the result */
	char outputFileName[MAX_FILENAME_SIZE];

	strncpy(outputFileName, argv[1], MAX_FILENAME_SIZE);

	printf("Created file strncpy %s\n", outputFileName);

	int value;

	// -------------------------------------------------------------
	// TODO: FIX a perhaps missing '\0' at the end of outputFileName
	// and make sure ".pgm" can be appended.
	//
	// TODO: potser falta un '\0' al final de outputFileName.
	// Assegura't que després hi ha prou espai per afegir el ".pgm".
	//
	// TODO: quizás falta un '\0' al final de outputFileName.
	// Assegurate que hay suficiente espacio para añadir 
	// la cadena ".pgm" luego.

	value =	

	// -------------------------------------------------------------

	outputFileName[value] = '\0'; //===================> TODO : keep an eye on this

	strcat(outputFileName, ".pgm");
	printf("Created file tras strcat %s\n", outputFileName);
	

	/* Allocate memory for a canvas and paint it white by default */
	unsigned char bitmap[MAX_CANVAS_WIDTH * MAX_CANVAS_HEIGHT];
	memset(bitmap, 255, MAX_CANVAS_WIDTH * MAX_CANVAS_HEIGHT);

	/* Allocate memory for our outputfile header */
	char header[1024];

	/* Define settings for said canvas */
	struct settings canvas;
	canvas.bitmap = bitmap;
	canvas.header = header;

	/* Draw the input file into the canvas */
	DrawFile(argv[1], &canvas);

	/* If everything was ok...
     * Write the resulting drawing into outputFileName.
     *
     * We are dumping a plain pgm formatted file.
     * Utilities such as Eye of gnome (eog) or the Gimp should
     * be able to read this file directly.
	 */
	//FILE * file = fopen(outputFileName, "w");
	FILE * file = fopen("test.png", "w");

	if (! file) {
		perror(__FILE__);
		exit(EXIT_FAILURE);
	}

	DumpCanvas(&canvas, file);

	fclose(file);

	printf("Created file %s\n", outputFileName);

	/* We are done */
	printf("-> done!\n");

	return 0;
}

