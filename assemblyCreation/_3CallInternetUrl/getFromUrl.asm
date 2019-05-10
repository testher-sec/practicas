;.............................................
; X.- Program that checks internet connection
;     Gets content from url
;     Logic in a separated function
;.............................................

; reserve space for stack
; symbol names are case-sensitive
; model statement must precede both directive

.386
.model flat, stdcall
.stack 100h
option casemap :none

include \masm32\INCLUDE\windows.inc

include \masm32\INCLUDE\kernel32.inc
includelib\masm32\lib\kernel32.lib

include \masm32\INCLUDE\wininet.inc
includelib\masm32\lib\wininet.lib

; include needed for MessageBoxA
includelib \MASM32\LIB\user32.lib
include \MASM32\INCLUDE\user32.inc

.data

    hidden_url          db    'http://192.168.119.26:83/hiddenFile.txt', 0  
    lpszAgent           db    'fake Agent 1.1',0      
    no_connection	      db	'Sorry, there is no connectivity',0

    bytes_read          dd  ?

    internet_handle     dd  ?
    url_handle          dd  ?
    response            db 100 DUP(0)
.code


getValueFromUrl PROC resp:DWORD

    local my_local:DWORD    ; This part is not useful. Just to distract
    mov my_local, 33        ; added so we can see difference between parameter and local variables
                            ; when reversing

    invoke InternetGetConnectedState, 0,0  ; dwReserved parameter is reserved and must be 0.
    cmp eax, 0
    jz _no_internet  ; if return value is 0, we do NOT have internet

    invoke InternetOpenA, offset lpszAgent, 1, 0, 0, 0
    mov [internet_handle], eax
    cmp internet_handle, 0
    je _exit_clean
    
    invoke InternetOpenUrlA,internet_handle, offset hidden_url ,0,0,INTERNET_FLAG_RELOAD,0
    mov [url_handle], eax
    cmp url_handle, 0
    je _exit_clean

    invoke InternetReadFile, url_handle, resp, 100 , offset bytes_read
    cmp eax, 0   
    je _exit_clean
    
    invoke InternetCloseHandle,  [internet_handle]  
    invoke InternetCloseHandle,  [url_handle]
    mov eax,1
    ret

getValueFromUrl ENDP

_no_internet:
    invoke MessageBoxA,0,offset no_connection,offset 0,0
    jmp _exit_clean    

start:
    invoke getValueFromUrl, offset response
    invoke MessageBoxA,0,offset response,offset 0,0

_exit_clean:
    invoke ExitProcess,0

end start





