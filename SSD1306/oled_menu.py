import writer
import freesans20
from ssd1306 import SSD1306_I2C
from machine import Pin, I2C, SPI

class oled_menu:
    def __init__(self,oled,font_writer,lines=3):
        self._oled = oled
        
        self._writer = font_writer
        self._lines = lines
        self._font_size= 20 #self._writer.char_height
        self._line_sizes = {1:self._font_size *0,2:self._font_size *1+2,3:self._font_size *2+2}
        self._message = ""
        self.selected = ""
    
    def print_on_line(self,line,message, clear= True):
        if clear:
            #oled.fill(0)
            _left_corner = self._line_sizes[line]
            _right_corner = self._line_sizes[line]+ self._font_size
            self._oled.fill_rect(0,_left_corner,self._oled.width,self._font_size,0)
            #self._oled.show()
        self._writer.set_textpos(self._oled,self._line_sizes[line],1)
        #print("{}, {}, {}".format(_left_corner,_right_corner,self._oled.width))
        self._writer.printstring(message)
        self._oled.show()
        #print("Done")
    
    def set_array(self,message):
        self._message = message
        
    def print_array(self,message,start,lines, clear= True):
        self.set_array(message)
        if clear:
            self._oled.fill(0)
            #_left_corner = self._lines[1]
            #_right_corner = self._lines[lines]+ self._font_size
            #self._oled.fill_rect(0,_left_corner,self._oled.width,self._font_size,0)
            #self._oled.show()
        _line_pos = 1
        for line in self._message[start:start+lines]:
            self._writer.set_textpos(self._oled,self._line_sizes[_line_pos],1)
            if _line_pos == 1:
                self.selected = line
                line = line + " <"
            self._writer.printstring(line)
            _line_pos += 1
        self._oled.show()
        #print("Done")

    
    def rotate(self, shift = 1):
        if shift == 1:
            self._message.insert(len(self._message),self._message[0]) #la final primul
            #myarray.insert(0,myarray[-1]) # 
            self._message.pop(0) #delete primul
        
        if shift == -1:
            self._message.insert(0,self._message[-1]) #la inceput ultimul
            self._message.pop() #delete ultimul
    def display_array(self,start=0):
        self._oled.fill(0)
            #_left_corner = self._lines[1]
            #_right_corner = self._lines[lines]+ self._font_size
            #self._oled.fill_rect(0,_left_corner,self._oled.width,self._font_size,0)
            #self._oled.show()
        _line_pos = 1
        for line in self._message[start:start+self._lines]:
            if _line_pos == 1:
                self.selected = line
                line = line + " <"
                
            self._writer.set_textpos(self._oled,self._line_sizes[_line_pos],1)
            self._writer.printstring(line)
            _line_pos += 1
        self._oled.show()
