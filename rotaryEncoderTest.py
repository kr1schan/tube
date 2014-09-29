from rotaryEncoder import RotaryEncoder

def callback(direction):
        print("Hello Rotary Encoder - " + direction)

rotaryEncoder = RotaryEncoder(62, "pi10", 64, "pb13", 61, "pi13", 66, "pb10", callback)
rotaryEncoder.enable()

