
@rp2.asm_pio(out_shiftdir=rp2.PIO.SHIFT_RIGHT,autopush=True,push_thresh=1)
def get_ir():
    wrap_target()
    
    label("next_burst")
    mov(x,30)
    wait(0, pin, 0)
    
    label("burst_loop")
    jmp(pin, "data_bit")
    jmp(x_dec,"burst_loop")
    mov(isr,null)
    wait(1, pin, 0)
    jmp("next_burst")
    
    
    label("data_bit")
    nop() [14]
    in_(pin,1)
    wrap()
    
sm_ir = rp2.StateMachine(2, get_ir,freq = 18_000, in_base= Pin(5)) #in_base= rpm,
sm_ir.active(1)


#in_base= rpm,

#sm_triac.put(115)
#sm_triac.exec("pull()")
#sm_triac.exec("mov(isr, osr)")

#sm_ir.active(0)

while True:
    
    time.sleep(1)
    print("loop")
    print(sm_ir.get())


