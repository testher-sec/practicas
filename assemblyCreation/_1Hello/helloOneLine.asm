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
	INVOKE MessageBoxA,0,offset hello_world,offset world_tittle,0
	INVOKE ExitProcess,0

end start