;..................................................
; X.- MUTEX. Program that creates a key in registry
;..................................................

; reserve space for stack
; symbol names are case-sensitive
; model statement must precede both directive

.386
.model flat, stdcall
.stack 100h
option casemap :none

; needed to be able to use constant HKEY_LOCAL_MACHINE
include \masm32\INCLUDE\windows.inc

include \masm32\INCLUDE\kernel32.inc
includelib\masm32\lib\kernel32.lib

; Needed for key management functions
include \masm32\INCLUDE\advapi32.inc
includelib\masm32\lib\advapi32.lib

; include needed for MessageBoxA
includelib \MASM32\LIB\user32.lib
include \MASM32\INCLUDE\user32.inc

.data
    handle_problem  db "Sorry, there was a problem editing the key",0
    key_name        db "NESKA",0
    key_name_2      db "Charlie",0
    key_value       db "valuelalala", 0
    phkResult           dd  ?
    hRegistryResponse   dd ?
.code


setKey PROC value:DWORD
    invoke RegCreateKeyExA,HKEY_CURRENT_USER,offset key_name,0,0,REG_OPTION_NON_VOLATILE,KEY_ALL_ACCESS,0,offset phkResult,offset hRegistryResponse
    cmp eax,ERROR_SUCCESS
    jnz _back       ; jump if not 0 == jump if not equal

    invoke RegSetValueExA,phkResult,offset key_name_2,0,REG_SZ,value, 12 ; we'll use a fixed value but length should be calculated or parameter
    cmp eax, ERROR_SUCCESS
    jnz _back
    
    ret

_back:
    invoke MessageBoxA,0,offset handle_problem,offset 0,0
    ret

setKey ENDP


start:
    invoke setKey,offset key_value 
    invoke ExitProcess,0

end start





