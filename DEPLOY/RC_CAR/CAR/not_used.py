def master():
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    #if cfg["spi"] == -1:
    spi = SPI(1)
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
    #else:
    #    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=8)

    nrf.open_tx_pipe(pipes[0])
    nrf.open_rx_pipe(1, pipes[1])
    nrf.start_listening()

    num_needed = 10006
    num_successes = 0
    num_failures = 0
    led_state = 0

    print("NRF24L01 master mode, sending %d packets..." % num_needed)

    while num_successes < num_needed and num_failures < num_needed:
        # stop listening and send packet
        nrf.stop_listening()
        millis = utime.ticks_ms()
        led_state = max(1, (led_state << 1) & 0x0F)
        print("sending:", millis, led_state)
        try:
            nrf.send(struct.pack("ii", millis, led_state))
        except OSError:
            pass

        # start listening again
        nrf.start_listening()

        # wait for response, with 250ms timeout
        start_time = utime.ticks_ms()
        timeout = False
        while not nrf.any() and not timeout:
            if utime.ticks_diff(utime.ticks_ms(), start_time) > 250:
                timeout = True

        if timeout:
            print("failed, response timed out")
            num_failures += 1

        else:
            # recv packet
            (got_millis,) = struct.unpack("i", nrf.recv())

            # print response and round-trip delay
            print(
                "got response:",
                got_millis,
                "(delay",
                utime.ticks_diff(utime.ticks_ms(), got_millis),
                "ms)",
            )
            num_successes += 1

        # delay then loop
        utime.sleep_ms(250)

    print("master finished sending; successes=%d, failures=%d" % (num_successes, num_failures))
