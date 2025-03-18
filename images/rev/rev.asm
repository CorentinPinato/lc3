; Reverse a string
; Author: Corentin Pinato
  .ORIG x3000

REV
  LEA R0, FILE    ; R0 is beginning of STRINGZ
  AND R1, R1, #0  ; Set R1 to x0
  ADD R6, R0, #0  ; R0 backup

LOOP1             ; while (char != x0)
  LDR R2, R0, #0  ; Load character value
  ADD R2, R2, #0  ; set flag
  BRz END1        ; if zero flag end

  STR R2, R1, #1  ; push char value on stack
  ADD R0, R0, #1  ; increment R0 / String pointer
  ADD R1, R1, #1  ; increment R1 / stack pointer
  BR LOOP1        ; Jump back to beginning of loop
END1

ADD R0, R6, #0    ; set back start
LOOP2             ; while (stack_pointer != 0)
  ADD R1, R1, #0  ; Set flag
  BRz END2        ; if zero flag end

  LDR R2, R1, #0  ; Load stack value into R2
  STR R2, R0, #0  ; Store stack value at R0
  ADD R0, R0, #1  ; increment R0 / String pointer
  ADD R1, R1, #-1 ; Decrement R1 / stack pointer
  BR LOOP2        ; Jump back at beginning of loop
END2
ADD R0, R6, #0    ; set back start

DONE
  PUTS
  HALT

FILE .STRINGZ "Corentin Pinato"
     .END
