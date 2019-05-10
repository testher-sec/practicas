;.............................................
; 2.- Program that creates and deletes files
;.............................................

; reserve space for stack
; symbol names are case-sensitive
; model statement must precede both directive

.386
.model flat, stdcall
;.stack 100h ; to find out whats the use of this
option casemap :none

; includes for ExitProcess
include \MASM32\INCLUDE\kernel32.inc
includelib \MASM32\LIB\kernel32.lib

; include needed for CreateFileA and DeleteFileA : fileapi.h (include Windows.h)
include \MASM32\INCLUDE\windows.inc


.data
    file_handler    dd  0, 0            ; Define double word. Generally 4 bytes on a typical x86 32-bit system
    file_name       db  ".\temp", 0     ; declares 7 bytes starting at the address of 'file_name'
    lpFileName      dd  0, 0
    errorCode       dd  0, 0

.code

start:
    ; Creates a new file, always.
    ; If the specified file exists and is writable, the function overwrites the file, the function succeeds, and last-error code is set to ERROR_ALREADY_EXISTS (183).
    ; If the specified file does not exist and is a valid path, a new file is created, the function succeeds, and the last-error code is set to zero.
    invoke CreateFileA, offset file_name, GENERIC_READ Or GENERIC_WRITE, TRUE, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL

    cmp eax, INVALID_HANDLE_VALUE       ; If the function fails, the return value is INVALID_HANDLE_VALUE
    jz _clear_leave                     ; If we face a problem creating the file do a clean exit
    mov file_handler, eax               ; keep the handler of the file
    invoke CloseHandle, file_handler


    invoke Sleep,5000                   ; sleep for 5 seconds so we can check the file was created
    
    invoke DeleteFileA, offset file_name    ; delete file just created
    invoke ExitProcess,0

_clear_leave:
    invoke GetLastError
    mov errorCode, eax                  ; Could be used to promp with error message
    invoke CloseHandle, file_handler
    invoke ExitProcess,0

end start