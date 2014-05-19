import subprocess

Out = "out"
In = "in"

Rising = "rising"
Falling = "falling"
Both = "both"

PullDown = "pulldown"
PullUp = "pullup"

EDGE = 1

def gpio_admin(subcommand, pin, suffix="", pull=None):
    if pull:
        subprocess.check_call(["gpio-admin", subcommand, str(pin), pull, suffix])
    else:
        subprocess.check_call(["gpio-admin", subcommand, str(pin), "nopull", suffix])

class PinAPI(object):
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    value = property(lambda p: p.get(),
                     lambda p,v: p.set(v),
                     doc="""The value of the pin: 1 if the pin is high, 0 if the pin is low.""")

class Pin(PinAPI):
    """Controls a GPIO pin."""

    __trigger__ = EDGE

    def __init__(self, soc_pin_number, direction=In, interrupt=None, pull=None, suffix=""):
        self._soc_pin_number = soc_pin_number
        self._file = None
        self._direction = direction
        self._interrupt = interrupt
        self._pull = pull
        self._suffix = suffix

    @property
    def soc_pin_number(self):
        return self._soc_pin_number

    def open(self):
        gpio_admin("export", self.soc_pin_number, self._suffix, self._pull)
        self._file = open(self._pin_path("value"), "r+")
        self._write("direction", self._direction)
        if (self._direction == In) and (self._interrupt != None):
            self._write("edge", self._interrupt if self._interrupt is not None else "none")

    def close(self):
        if not self.closed:
            if self.direction == Out:
                self.value = 0
            self._file.close()
            self._file = None
            self._write("direction", In)
            if (self._interrupt != None):
                self._write("edge", "none")
            gpio_admin("unexport", self.soc_pin_number)

    def get(self):
        self._check_open()
        self._file.seek(0)
        v = self._file.read()
        return int(v) if v else 0

    def set(self, new_value):
        self._check_open()
        if self._direction != Out:
            raise ValueError("not an output pin")
        self._file.seek(0)
        self._file.write(str(int(new_value)))
        self._file.flush()

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, new_value):
        self._write("direction", new_value)
        self._direction = new_value

    @property
    def interrupt(self):
        return self._interrupt

    @interrupt.setter
    def interrupt(self, new_value):
        self._write("edge", new_value)
        self._interrupt = new_value

    @property
    def pull(self):
        return self._pull

    def fileno(self):
        """Return the underlying file descriptor.  Useful for select, epoll, etc."""
        return self._file.fileno()

    @property
    def closed(self):
        """Returns if this pin is closed"""
        return self._file is None or self._file.closed

    def _check_open(self):
        if self.closed:
            raise IOError(str(self) + " is closed")

    def _write(self, filename, value):
        with open(self._pin_path(filename), "w+") as f:
            f.write(value)

    def _pin_path(self, filename=""):
        return "/sys/class/gpio/gpio%i%s/%s" % (self.soc_pin_number, self._suffix, filename)

    def __repr__(self):
        return self.__module__ + "." + str(self)

    def __str__(self):
        return "{type})".format(
            type=self.__class__.__name__)
