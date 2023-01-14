

# PIO Episode 5, Example 4
# Jump if x = 0 Instruction
# Blinks LED 3 using a pull instruction
# to input a user selected delay for a variable
# frequency


from rp2 import PIO, StateMachine, asm_pio
from machine import Pin
import time

@asm_pio(set_init=PIO.OUT_LOW)
def led_blink():
    label("mainloop")
    pull(noblock)            # Loads OSR with delay value
    mov(x,osr)               # OSR contents to X to prepare for future noblock pulls
    mov(y,x)                 # Load delay value into Y
    set(pins, 0)    [31]     # Turns off LED
    label("delay_off")       # Start of off timer
    jmp(y_dec, "delay_off")   [31]  # Jumps to "delay_off" if y not 0, then decrements Y
    mov(y,x)                 # Load delay value into Y
    set(pins, 1)    [31]     # Turns LED on
    label("delay_on")        # Start of on timer
    jmp(y_dec, "delay_on")   [31]   # Jumps to "delay_on" if y not 0, then decrements Y
    jmp("mainloop")          # Jumps to the beginning of the blink routine   
    
led = Pin(2, Pin.OUT)
sm1 = StateMachine(1, led_blink, freq=2000, set_base=led) # Instantiates State Machine 1
sm1.active(1)                                                # Starts State Machine 1

while True:
      value = int(input("enter delay:"))
      sm1.put(value)         # Output the next Byte
      print(value)

