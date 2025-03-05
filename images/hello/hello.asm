; Project: Simple Hello World.
; Author: Corentin Pinato
;
;-----------------------------------
.ORIG x3000                                 ; this is the address in memory where the program will be loaded
;-----------------------------------
WELCOME
  LEA R0, WELCOME_STR                       ; load the address of the HELLO_STR string into R0
  PUTS                                      ; output the string pointed to by R0 to the console
  GETC                                      ; get input from keyboard and load into R0
  BRnzp MAIN                                ; branch onto MAIN on any input

WELCOME_STR
  .STRINGZ "Hello World!\n"       ; store this string here in the program

MAIN
  LEA R0, MESSAGE_STR                       ; load the address of the MESSAGE_STR string into R0
  PUTS                                      ; output the string pointed to by R0 to the console
  HALT                                      ; halt program

MESSAGE_STR
  .STRINGZ "This is a message\n"  ; store this string here in the program
.END                                        ; mark the end of the file
