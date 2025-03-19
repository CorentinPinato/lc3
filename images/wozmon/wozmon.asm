; TODO: Description
; Author: Corentin Pinato
; \ => backslah to start command
; [Enter] => enter command
; \3000 => lookup bytes on address 0x3000
;  #=> 3000: 00 0A 11 BE
; \3000.300A => lookup bytes in addresses from 0x3000 to 0x300A
; #=> repeat above for each address
; \3000:AA => write to addr. 0x3000 value AA
;  #=> 3000: AA .....
;
.ORIG x3000
BR MAIN

STKPTR .FILL x3001
STACK  .BLKW #10

STKINC
  LD R5, STKPTR
  ADD R5, R5, #1
  ST R5, STKPTR
  RET
STKDEC
  LD R5, STKPTR
  ADD R5, R5, #-1
  ST R5, STKPTR
  RET
GET_STKPTR
  LEA R0, STKPTR
  RET

BUFSTRT .FILL x3018
BUFPTR .FILL x3017
BUFFER .BLKW #8
; Buffer size requirement:
; 3000 = 4
; 3000.3000 = 4 + 4 = 8
; 3000: AA AA = 4 + 4 = 8

BUFINC
  LD R5, BUFPTR
  ADD R5, R5, #1
  ST R5, BUFPTR
  RET
BUFPUSH
  ADD R6, R7, #0
  JSR BUFINC
  ADD R7, R6, #0
  STI R0, BUFPTR
  RET
BUFCLEAR
  LEA R5, BUFPTR
  ST R5, BUFPTR
  LEA R5, BUFFER
  ST R5, BUFSTRT
  RET
BUFPRINT
  ADD R6, R7, #0

  LD R3, BUFSTRT
  LD R4, BUFPTR
  NOT R4, R4

  BUFPRTLOOP
    LDR R0, R3, #0
    OUT

    ADD R3, R3, #1
    ADD R5, R3, R4
    BRnp BUFPRTLOOP
  ADD R7, R6, #0
  RET

MAIN
  JSR CHECK_COMMAND

MONITOR_ENTER
  LD R0, CH_NEWLN
  OUT

MONITOR
  GETC

  NOT R2, R0
  ADD R2, R2, #1 ; R2 = -R0

  LD R1, CH_BSLASH
  ADD R1, R2, R1
  BRz EXIT_COMMAND

  LD R1, CH_NEWLN
  ADD R1, R2, R1
  BRz EXIT

CHECK_MODE
  LD R1, MODE
  ADD R1, R1, #0
  BRnp CHECK_CHAR

  NOT R2, R0
  ADD R2, R2, #1 ; R2 = -R0

  LD R1, CH_DOT
  ADD R1, R2, R1
  BRz SAVE_MODE

  LD R1, CH_COLON
  ADD R1, R2, R1
  BRz SAVE_MODE

CHECK_CHAR
  LD R1, CH_ZERO
  NOT R1, R1
  ADD R1, R1, #1
  ADD R1, R0, R1
  BRn MONITOR

  LD R1, CH_ZERO
  ADD R1, R1, #9
  NOT R1, R1
  ADD R1, R1, #1
  ADD R1, R0, R1
  BRnz TAKE_CHAR

  LD R1, CH_F
  ADD R1, R1, #-5
  NOT R1, R1
  ADD R1, R1, #1
  ADD R1, R0, R1
  BRn MONITOR

  LD R1, CH_F
  NOT R1, R1
  ADD R1, R1, #1
  ADD R1, R0, R1
  BRp MONITOR

TAKE_CHAR
  OUT
  JSR BUFPUSH
  BR MONITOR

SAVE_MODE
  OUT
  ST R0, MODE
  BR MONITOR

CHAR2NUM
  ; Expecting char to be in R0
  ADD R2, R0, #0   ; Saving R0 value

  LD R1, CH_A_OFF  ; 55
  NOT R1, R1
  ADD R1, R1, #1   ; -55
  ADD R0, R0, R1   ; CHAR - 65

  ADD R1, R0, #-10
  BRzp RETCHAR2NUM ; if char >= 65

  ADD R0, R2, #0   ; Reset value of R0 to original

  ; To reach this point char should be < 55
  ; relying on input code to only allow valid
  ; characters: therefore this char should be
  ; in the range of 48 to 57 inclusive.
  LD R1, CH_ZERO
  NOT R1, R1
  ADD R1, R1, #1 ; -48
  ADD R0, R0, R1 ; char - 48 
RETCHAR2NUM
  RET            ; Result returned in R0

NUM2CHAR ; Convert a number to ASCII char, using R0
  ADD R3, R0, #0

  ADD R0, R0, #-10 ; num - 10
  BRzp RETNUM2CHAR ; if num >= 10

  LD R0, CH_ZERO
  ADD R0, R0, R3
  RET
RETNUM2CHAR
  LD R0, CH_A_OFF
  ADD R0, R0, R3
  RET

ROTATE4 ; Rotate four times to the left R0.
  ST R7, TEMP
  JSR ROTATE
  JSR ROTATE
  JSR ROTATE
  JSR ROTATE
  LD R7, TEMP

  ADD R1, R1, #0
  BRnp ENDROTATE
  RET

ROTATE
  LD R1, MASK

  AND R1, R1, R0
  ADD R0, R0, R0

  ADD R1, R1, #0
  BRz ENDROTATE

  ADD R0, R0, #1
ENDROTATE
  RET

MEM2HEX
  ADD R4, R7, #0
 
  JSR BUFCLEAR
  AND R1, R1, #0 ; Set to 0 to accumulate answer
  ADD R2, R0, #0 ; copy R0 for future use.

  JSR ROTATE4
  AND R0, R0, #15
  JSR NUM2CHAR
  JSR BUFPUSH

  ADD R0, R2, #0
  JSR ROTATE4
  JSR ROTATE4
  AND R0, R0, #15
  JSR NUM2CHAR
  JSR BUFPUSH

  ADD R0, R2, #0
  JSR ROTATE4
  JSR ROTATE4
  JSR ROTATE4
  AND R0, R0, #15
  JSR NUM2CHAR
  JSR BUFPUSH

  ADD R0, R2, #0
  AND R0, R0, #15
  JSR NUM2CHAR
  JSR BUFPUSH

  ADD R0, R2, #0
  ADD R7, R4, #0
  RET

HEX2MEM ; Take values from buffer and return addr. in R0
  LD R3, BUFSTRT  ; Starting point
  AND R5, R5, #0 ; Set to 0, use R3 for final addr.

  LDR R0, R3, #0 ; LOAD into R0 memory pointed by R1
  JSR CHAR2NUM   ; Convert R0 from char to number 
  JSR SHIFT4
  JSR SHIFT4
  JSR SHIFT4
  ADD R5, R5, R0 ; Store result at 1st (leftmost byte)
  ADD R3, R3, #1 ; increment buffer addr.

  LDR R0, R3, #0 ; LOAD into R0 memroy pointed by R1
  JSR CHAR2NUM   ; Convert R0 from char to number 
  JSR SHIFT4
  JSR SHIFT4
  ADD R5, R5, R0 ; Store result at 1st (leftmost byte)
  ADD R3, R3, #1 ; increment buffer addr.

  LDR R0, R3, #0 ; LOAD into R0 memroy pointed by R1
  JSR CHAR2NUM   ; Convert R0 from char to number 
  JSR SHIFT4
  ADD R5, R5, R0 ; Store result at 1st (leftmost byte)
  ADD R3, R3, #1 ; increment buffer addr.

  LDR R0, R3, #0 ; LOAD into R0 memroy pointed by R1
  JSR CHAR2NUM   ; Convert R0 from char to number 
  ADD R5, R5, R0 ; Store result at 1st (leftmost byte)

  ADD R0, R5, #0
  LDI R6, STKPTR
  JSR STKDEC
  ADD R7, R6, #0
  RET

EXIT_COMMAND
  JSR BUFCLEAR
  OUT
  LDI R0, CH_NEWLN
  OUT
  AND R0, R0, #0
  ST R0, MODE

CHECK_COMMAND
  GETC              ; Get char. into R0
  OUT               ; Output char. in R0

  LD R1, CH_Q
  NOT R1, R1
  ADD R1, R1, #1
  ADD R1, R0, R1
  BRz QUIT

  LD R1, CH_BSLASH
  NOT R1, R1
  ADD R1, R1, #1
  ADD R1, R0, R1
  BRz MONITOR_ENTER
  BR CHECK_COMMAND

EXIT 
  ; CHECK_READ
  LD R0, MODE
  ADD R1, R0, #0
  BRnp CHECK_READM
  LD R0, CH_NEWLN
  OUT
  BR HDL_READ

CHECK_READM
  LD R1, CH_DOT
  NOT R1, R1
  AND R1, R0, R1
  ; BRnp CHECK_RUN
  BRnp CHECK_WRITE
  LD R0, CH_NEWLN
  OUT
  BR HDL_READM

; CHECK_RUN
;   LD R1, CH_R
;   NOT R1, R1
;   ADD R1, R1, #0
;   BRnp CHECK_WRITE
;   LD R0, CH_NEWLN
;   OUT
;   BR HDL_RUN

CHECK_WRITE
  LD R0, CH_NEWLN
  OUT
  BR HDL_WRITE

SHIFT4 ; Shift four times what is located in R0
  ; It would take as much to make a loop
  ; so why bother?
  ADD R0, R0, R0 ; N = N + N => Left Shift
  ADD R0, R0, R0 ; N = N + N => Left Shift
  ADD R0, R0, R0 ; N = N + N => Left Shift
  ADD R0, R0, R0 ; N = N + N => Left Shift

  RET

HDL_WRITE ; Handle Write
  ; ADDR: DATA
  ; e.g 3159: AA00
  ; So read first 4 values in buffer for addr. to write to.
  ; Parse next 4 balues in buffer for value.
  ; so, eseentially move the pointer +4 positions.

  LD R0, BUFPTR
  ADD R0, R0, #-4
  ST R0, BUFPTR
  JSR BUFPRINT
  LD R0, CH_COLON
  OUT
  LD R0, CH_SPACE
  OUT

  LEA R6, HDL_WRITE_L1
  JSR STKINC
  STI R6, STKPTR
  JSR HEX2MEM ; Read four values in buffer
HDL_WRITE_L1

  JSR STKINC
  STI R0, STKPTR ; store result in stack

  LD R0, BUFPTR
  ADD R0, R0, #4
  ST R0, BUFPTR
  LD R0, BUFSTRT
  ADD R0, R0, #4
  ST R0, BUFSTRT

  LEA R6, HDL_WRITE_L2
  JSR STKINC
  JSR GET_STKPTR
  LDR R0, R0, #0
  STR R6, R0, #0
  JSR HEX2MEM ; Read four values in buffer

HDL_WRITE_L2

  ADD R2, R0, #0 ; copy result in R2
  ; R0 is the new value
  ; R1 is the address
  JSR GET_STKPTR
  LDR R1, R0, #0 ; Pop address off the stack
  LDR R1, R1, #0
  JSR STKDEC

  STR R2, R1, #0
  JSR BUFPRINT
  LD R0, CH_NEWLN
  OUT

  LEA R0, MSG_WRITE
  BR END_COMMAND

HDL_READM ; Handle MULTI READ
  ; Read the address of the first four and
  ; the address of the last four inputs
  ; substract first on last
  ; if result is neg. EXIT
  ; else loop
  ; increment address, convert, print
  ; get value, convert, print

  LEA R0, MSG_READM
  BR END_COMMAND

HDL_READ ; Handle Read
  JSR BUFPRINT
  LD R0, CH_COLON
  OUT
  LD R0, CH_SPACE
  OUT

  JSR STKINC
  JSR GET_STKPTR
  LDR R0, R0, #0
  LEA R7, LAB
  STR R7, R0, #0
  JSR HEX2MEM    ; Buffer to mem. addr.
LAB
  LDR R0, R0, #0 ; Load value from add.r
  JSR MEM2HEX    ; Mem. value to Buffer
  JSR BUFPRINT   ; Print buffer content
  LEA R0, MSG_READ

END_COMMAND
  PUTS
  AND R0, R0, #0
  ST R0, MODE
  JSR BUFCLEAR
  BR MAIN

QUIT
HALT

MODE      .FILL x0000 ; READ on start
CH_A      .FILL x0041
CH_A_OFF  .FILL x0037
CH_BKSPC  .FILL x0008
CH_BSLASH .FILL x005C
CH_COLON  .FILL x003A
CH_DOT    .FILL x002E
CH_F      .FILL x0046
CH_NEWLN  .FILL x000A
CH_SPACE  .FILL x0020
CH_Q      .FILL x0051
CH_R      .FILL x0052
CH_ZERO   .FILL x0030
MASK      .FILL x8000

TEMP .FILL x0000

MSG_READ  .STRINGZ "\nYou were in READ MODE\n"
MSG_READM .STRINGZ "\nYou were in READ MULTI MODE\n"
MSG_WRITE .STRINGZ "\nYou were in WRITE MODE\n"
.END
