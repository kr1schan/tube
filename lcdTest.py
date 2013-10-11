
from lcd import LCD

display = LCD("0x3f")
display.enable()
display.display("HELLO",1)
display.display("WORLD!",2)
display.display("WHATS",3)
display.display("UP?",4)
