;........................................................
;
; 1.- Program that prints Hellow Epasan using Message Box
;
;........................................................


; reserve space for stack
; symbol names are case-sensitive
; model statement must precede both directive

.386
.model flat, stdcall
.stack 100h
option casemap :none

include \masm32\INCLUDE\user32.inc
include \masm32\INCLUDE\kernel32.inc

includelib \masm32\lib\user32.lib
includelib\masm32\lib\kernel32.lib

.data
	hello_world	   db	'Hello, Epasan!',0
	world_tittle   db	'Epasan Finde', 0

.code

start:
	push 0                     ; uType - MB_OK (0x00000000L) message box contains one push button: OK.
	push offset world_tittle   ; lpCaption - dialog box title
	push offset hello_world    ; lpText - message to be displayed
	push 0                     ; hWnd - message box has no owner window
	call MessageBoxA

	push 0
	call ExitProcess

end start