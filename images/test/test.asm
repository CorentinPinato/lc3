; Simple program for testing purposes.
; Author: Corentin Pinato
.ORIG x3000

BR MAIN

STACK .BLKW #128
STACKPNT .FILL x3000

INC_PTR
  LD R5, STACKPNT
  ADD R5, R5, #1
  ST R5, STACKPNT
  RET

DEC_PTR
  LD R5, STACKPNT
  ADD R5, R5, #-1
  ST R5, STACKPNT
  RET

PUSH_R6
  ST R7, TEMP
  JSR INC_PTR
  LD R7, TEMP
  STI R6, STACKPNT
  RET

POP_R6
  LDI R6, STACKPNT
  ST R7, TEMP
  JSR DEC_PTR
  LD R7, TEMP
  RET

PEEK_R6
  LDI R6, STACKPNT
  RET

MAIN

LEA R0, HELLO
PUTS
JSR PRT_NEWLINE

LD R4, STACKPNT
NOT R4, R4

LEA R1, HELLO

LD R2, ZERO
LOOP
  LDR R6, R1, #0
  ADD R0, R2, R6
  BRz END

  JSR PUSH_R6
  ADD R1, R1, #1
  BR LOOP
END

LOOP2
  LDI R0, STACKPNT
  AND R1, R0, R4
  BRz END2 

  JSR POP_R6
  OUT
  BR LOOP2
END2

BR QUIT                ; Unconditional branch to quit.

PRT_NEWLINE            ; Routine to write '\n'
  ST R7, TEMP          ; Temporary store R7 (subroutine return addr.)
  LD R0, NEWLINE      ; Load NEWLINE ('\n') Addr,
  OUT                  ; Print '\n' character; Overwrites R7 as it is a routine
  LD R7, TEMP          ; Load back return addr. into R7.
  RET                  ; Return from subroutine.

QUIT
HALT                   ; Stop

HELLO .STRINGZ "Hello World"
NEWLINE .FILL x000A
TEMP .FILL x0000
ZERO .FILL x0000
.END
