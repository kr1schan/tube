from button import Button

def callback():
	print("Hello Button")

button = Button(60, "pi11", 1, "pg3", callback)
button.enable()
