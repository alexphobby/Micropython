import utime
from utime import ticks_ms, ticks_diff
from sys import platform
if (platform == "esp32"):
    try:
        from umqtt.simple import MQTTClient
    except:
        from umqtt import MQTTClient
elif platform == "rp2":
    print("Pi Pico")
    from umqtt import MQTTClient
else:
    print("unknown")

import asyncio
_SOCKET_POLL_DELAY = const(5)
from uerrno import EINPROGRESS, ETIMEDOUT
BUSY_ERRORS = [EINPROGRESS, ETIMEDOUT, 118, 119,-113]
class MQTTQueue(MQTTClient):
    DELAY = 2
    DEBUG = False
    _response_time = 2000
   
    def delay(self, i):
        utime.sleep(self.DELAY)

    def log(self, in_reconnect, e):
        if self.DEBUG:
            if in_reconnect:
                print("mqtt reconnect: %r" % e)
            else:
                print("mqtt: %r" % e)

    def reconnect(self):
        i = 0
        while 1:
            try:
                return super().connect(False)
            except OSError as e:
                self.log(True, e)
                i += 1
                self.delay(i)
    
    def subscribe(self,topic):
        print("SUBSCR_")
        super().subscribe(topic)
        print("SUBSCR_DONE")
        
    def connect(self):
        print("CONN_")
        super().connect()
    
    def ping(self):
        #print("PING")
        super().ping()
        
    def check_msg(self, attempts=2):
        while attempts:
            self.sock.setblocking(False)
            try:
                return super().wait_msg()
            except OSError as e:
                print(f"err on check: {e}")
                self.log(False, e)
            self.reconnect()
            attempts -= 1
    
    async def _recv_len(self):
        n = 0
        sh = 0
        while 1:
            res = await self._as_read(1)
            b = res[0]
            n |= (b & 0x7F) << sh
            if not b & 0x80:
                return n
            sh += 7
    
    def _timeout(self, t):
        return ticks_diff(ticks_ms(), t) > self._response_time      
    
    async def _as_read(self, n, sock=None):  # OSError caught by superclass
        if sock is None:
            sock = self.sock
        # Declare a byte array of size n. That space is needed anyway, better
        # to just 'allocate' it in one go instead of appending to an
        # existing object, this prevents reallocation and fragmentation.
        data = bytearray(n)
        buffer = memoryview(data)
        size = 0
        t = ticks_ms()
        while size < n:
            if self._timeout(t):
                print("timeout ")
                return "nada"
            #if  not self.isconnected(): #self._timeRLOout(t) or
            #    raise OSError(-1, "Timeout on socket read")
            try:
                msg_size = sock.readinto(buffer[size:], n - size)
            except OSError as e:  # ESP32 issues weird 119 errors here
                msg_size = None
                if e.args[0] not in BUSY_ERRORS:
                    raise
            if msg_size == 0:  # Connection closed by host
                raise OSError(-1, "Connection closed by host")
            if msg_size is not None:  # data received
                size += msg_size
                t = ticks_ms()
                self.last_rx = ticks_ms()
            await asyncio.sleep_ms(_SOCKET_POLL_DELAY)
        return data
    
    async def a_wait_msg(self,queue):
        try:
            res=None
            self.sock.setblocking(False)
            #sent = self.sock.write(b"1")
            #print(f"Send dummy, {sent}")
            res = self.sock.read(1)  # Throws OSError on WiFi fail
            #if res is not None:
                #print(f"Sock read:{res}")
        except Exception as ex:
            if ex.args[0] in BUSY_ERRORS:  # err 113
                print(f'Err, msg in busy_errs {ex.args[0]}')
                await asyncio.sleep_ms(0.2)
            else:
                print(f"a_wait_msg error: {ex}")

        if res is None:
            return
        if res == b"":
            #raise OSError(-1, "Empty response")
            print("Empty response")

        if res == b"\xd0":  # PINGRESP
            #print("pingresp")
            await self._as_read(1)  # Update .last_rx time
            return
        op = res[0]
        
        if op == 0x40:  # PUBACK: save pid
            sz = await self._as_read(1)
            if sz != b"\x02":
                raise OSError(-1, "Invalid PUBACK packet")
            rcv_pid = await self._as_read(2)
            pid = rcv_pid[0] << 8 | rcv_pid[1]
            if pid in self.rcv_pids:
                self.rcv_pids.discard(pid)
            else:
                raise OSError(-1, "Invalid pid in PUBACK packet")

        if op == 0x90:  # SUBACK
            resp = await self._as_read(4)
            if resp[3] == 0x80:
                raise OSError(-1, "Invalid SUBACK packet")
            pid = resp[2] | (resp[1] << 8)
            if pid in self.rcv_pids:
                self.rcv_pids.discard(pid)
            else:
                raise OSError(-1, "Invalid pid in SUBACK packet")

        if op == 0xB0:  # UNSUBACK
            resp = await self._as_read(3)
            pid = resp[2] | (resp[1] << 8)
            if pid in self.rcv_pids:
                self.rcv_pids.discard(pid)
            else:
                raise OSError(-1)

        if op & 0xF0 != 0x30:
            print("return1")
            return
        print("await len")
        sz = await self._recv_len()
        topic_len = await self._as_read(2)
        #print(topic_len)
        topic_len = (topic_len[0] << 8) | topic_len[1]
        topic = await self._as_read(topic_len)
        print(topic)
        sz -= topic_len + 2
        if op & 6:
            pid = await self._as_read(2)
            pid = pid[0] << 8 | pid[1]
            sz -= 2
        #print("await msg _as_read")
        msg = await self._as_read(sz)
        #print(f"msg: {msg}")
        retained = op & 0x01
        queue._put(msg)
        if op & 6 == 2:  # qos 1
            pkt = bytearray(b"\x40\x02\0\0")  # Send PUBACK
            struct.pack_into("!H", pkt, 2, pid)
            await self._as_write(pkt)
        elif op & 6 == 4:  # qos 2 not supported
            raise OSError(-1, "QoS 2 not supported")
        return True 