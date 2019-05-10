;.............................................
; X.- Program that creates and deletes files
;     And finally removes itself to hide
;     TODO - get myself by name of proces????????????????????????????
;.............................................


; reserve space for stack
; symbol names are case-sensitive
; model statement must precede both directive

.386
.model flat, stdcall
.stack 100h
option casemap :none

; include needed for ExitProcess
include \MASM32\INCLUDE\kernel32.inc
includelib \MASM32\LIB\kernel32.lib

; include needed for MessageBoxA
includelib \MASM32\LIB\user32.lib
include \MASM32\INCLUDE\user32.inc


; include needed for ShellExecuteA
include \MASM32\INCLUDE\shell32.inc
includelib \MASM32\LIB\shell32.lib

include \MASM32\INCLUDE\windows.inc


.data
    notification_message    db  "Executable file is about to delete itself...", 0
    notification_tittle     db  "delete myself poc", 0
    cmd_exe                 db  "cmd.exe",0
    cmd_line                db  "Timeout /T 1 & /C del .\deleteMyself.exe", 0

.code

start:
    invoke MessageBoxA,0,offset notification_message,offset notification_tittle,0

    ; execute cmd_line in separated shell
    invoke ShellExecuteA, NULL, NULL, offset cmd_exe, offset cmd_line, NULL, SW_SHOWDEFAULT

    invoke ExitProcess,0

end start