Type    Description
------  ----------------------------------------
RO      Read-only
RW      Read/Write
WO      Write-only
W1C     Write 1 to clear
W1S     Write 1 to set (all other bits remain the same)
WP(A)   Write Pulse (acknowledge)
RP(A)   Read Pulse (acknoldeg)
COR     Clear on read
IOR(S)  Increment on read (saturate)
DOR(S)  Decrement on read (saturate)
SUB(n)  Used to concatenate several registers into a single field
SHADOW  
RAM

Reset Value
Field Bit-Width
Field Position

Signals      Width          Direction  Description
-----------  -----          ---------  -----------------------------------
clk          1
rst          1
rd           1               M --> S
wr           1               M --> S
addr         1-64            M --> S
wdata        2^N, N=3 to 10  M --> S
rdata        2^N, N=3 to 10  S --> M
rddata_valid 1               S --> M
lock         1               M --> S   Allows master A to RmodW, before master B can update
waitrequest  1               S --> M   Asserted by slave when it is unable to respond to master access
byte_enable  2^N, N=1 to 7   M --> S
response     2               S --> M   00: OKAY, 01: RESERVERD, 10:SLAVE_ERROR, 11: DECODE_ERROR
burst_count  1-11            M --> S
burst_start
burst_end
