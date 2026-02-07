import serial 
import time
arduino=serial.Serial(port="COM11",baudrate=9600,timeout=1)
def send_trigger(Trigger):
    print("\n\n***********Sending Trigger***********")
    time.sleep(2)
    if Trigger==True:
        arduino.write(b'1')
    if Trigger== False:
        print("Stopping Trigger")
        arduino.write(b'0')
while(True):
    Tr=input("Enter R for run and S for stop:")
    if Tr=="R":
        send_trigger(True)
    elif Tr=="S":
        send_trigger(False)
        break
    else:
        print("Invalid input")
        continue
        
        
             