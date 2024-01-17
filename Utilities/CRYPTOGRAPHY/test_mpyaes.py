#from: https://github.com/iyassou/mpyaes
import mpyaes
key = mpyaes.generate_key(32)
IV = mpyaes.generate_IV(16)
print(f"key: {key}")
#bytearray(b'\xe5\x82\xe7\xc1\xcfP9\xab\x9e4-(\\}\xab\xaa\xf3\xe2S\x054d\xdf"\x82\xd0\xd8\'\x9ee\xc6\x1b')
# IV = mpyaes.generate_IV(16)
print(f"IV: {IV}")
# bytearray(b"\xfeYD\x91\xf2\xcd\xf1\xc6\xc9\xd0\x9c#\xf1\xad'\x9a")

aes = mpyaes.new(key, mpyaes.MODE_CBC, IV)

cmdcmmessage = bytearray("test","UTF-8") #bytearray("This is an example string.","UTF-8")          # alternatively b'This is an example bytes.'
aes.encrypt(message)                  # mpyaes.AES.encrypt([bytes, str]) returns a bytearray
message
#bytearray(b'^"\x06u\x95\xcb\xb4\xf6\xf0\x90\xd6\xc7T\xd0)\xe1\xf6GMh\xf9\x0b\xd5\xbf\xb3\x12n\x037\xa0K\xfb')
message_dec = aes.decrypt(message)                  # zero-copy
message_dec
#bytearray(b'This is an example string.')