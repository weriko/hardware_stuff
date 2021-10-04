import RPi.GPIO as GPIO
import time

def parse_msg(x):
    x = [bin(ord(i))[2:] for i in x]

    return x
def show_led(x,pins, show_time = 2):
    for i,t in enumerate(x):
        GPIO.output(pins[i],bool(int(t)))
    time.sleep(show_time)
    for i,t in enumerate(x):
        GPIO.output(pins[i],False)
def show_msg(msg,pins,show_time=2, entry= 26, final=22, on_time=4, between_time= 0.5, entry_char = "1010", final_char = "101"):

    for i in pins:
        GPIO.output(i,False)
    msg = parse_msg(msg)
    msg = [entry_char] + msg + [final_char]

    for m in msg:
        if m == "1010":
            GPIO.output(entry,True)
        elif m=="101":
            print("BUENAS")
            GPIO.output(final,True)
            time.sleep(on_time)
            GPIO.output(entry,False)
            GPIO.output(final,False)
        else:
            show_led(m,pins,show_time=show_time)
            time.sleep(between_time)

def main():
    pins = [19,13,6,5,0,11,9,10]
    entry = 26
    final = 22
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(entry,GPIO.OUT)
    GPIO.setup(final,GPIO.OUT)
    for i in pins:
        GPIO.setup(i,GPIO.OUT)
    msg = "Ciencia de datos - Edge computing"
    show_msg(msg,pins,entry=entry,final=final,show_time=1)
    GPIO.cleanup()

main()
