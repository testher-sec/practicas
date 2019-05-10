;.............................................
; 6.- Program that groups all scripts from project
;       - query url get the value
;       - Show pop up window with message retrieved
;       - Store in a registry key
;       - Create a file and delete it
;       - Delete itself
;.............................................

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

include \masm32\INCLUDE\wininet.inc
includelib\masm32\lib\wininet.lib

include \masm32\INCLUDE\windows.inc

include \masm32\INCLUDE\advapi32.inc
includelib\masm32\lib\advapi32.lib

include \MASM32\INCLUDE\shell32.inc
includelib \MASM32\LIB\shell32.lib

.data
    ; step 1
    all_together_nessage   db	'Program sponsored by WT Solutions ;)',0
    all_together_tittle           db	'Hello, Epasan!', 0

    ; step 2
    hidden_url          db    'http://192.168.119.26:83/hiddenFile.txt', 0  
    lpszAgent           db    'fake Agent 1.1',0      
    no_connection	      db	'Sorry, there is no connectivity',0

    bytes_read          dd  ?

    internet_handle     dd  ?
    url_handle          dd  ?
    response            db 100 DUP(0)

    ; step 3
    handle_problem  db "Sorry, there was a problem editing the key",0
    key_name        db "NESKA",0
    key_name_2      db "Charlie",0
    phkResult           dd  ?
    hRegistryResponse   dd ?

    ; step 4
    file_handler    dd  0, 0            
    file_name       db  ".\temp", 0     
    lpFileName      dd  0, 0
    errorCode       dd  0, 0

    ; step 5
    all_together_nessage_bye   db	'It was a pleasure... WT Solutions ;)',0
    cmd_exe                 db  "cmd.exe",0
    cmd_line                db  "Timeout /T 2 & /C del .\AllTogetherEduProject.exe", 0


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

_no_internet:
    invoke MessageBoxA,0,offset no_connection,offset 0,0
    jmp _exit_clean

getValueFromUrl ENDP


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

createDeleteFile PROC
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
    ret

_clear_leave:
    invoke GetLastError
    mov errorCode, eax                  ; Could be used to promp with error message
    invoke CloseHandle, file_handler
    ret

createDeleteFile ENDP


start:
    invoke MessageBoxA,0,offset all_together_nessage,offset all_together_tittle,0

    invoke getValueFromUrl, offset response
    invoke MessageBoxA,0,offset response,offset all_together_tittle,0

    invoke setKey,offset response 
    invoke createDeleteFile

    ; Farewell box and delete myself :)
    invoke MessageBoxA,0,offset all_together_nessage_bye,offset all_together_tittle,0

    ; execute cmd_line in separated shell
    invoke ShellExecuteA, NULL, NULL, offset cmd_exe, offset cmd_line, NULL, SW_SHOWDEFAULT

_exit_clean:
    invoke ExitProcess,0

end start