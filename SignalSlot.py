from PySide6.QtCore import QObject, Signal, Slot

class MySender(QObject):
    my_signal = Signal(str)

    def do_something(self):
        print("Sender: doing something...")
        self.my_signal.emit("Hello from sender")

class MyReceiver(QObject):
    @Slot(str)
    def my_slot(self, message):
        print(f"Receiver got message: {message}")

# Setup
sender = MySender()
receiver = MyReceiver()

# Connect the signal to the slot
sender.my_signal.connect(receiver.my_slot)

# Emit the signal
sender.do_something()
