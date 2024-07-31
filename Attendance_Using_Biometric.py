import time
import board
import busio
from digitalio import DigitalInOut, Direction
import adafruit_fingerprint

led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

uart = busio.UART(board.TX, board.RX, baudrate=57600)

# If Using With A Computer Such As Linux/RaspberryPi, Mac, Windows With USB/Serial Converter:
# import serial
# uart = serial.Serial("/dev/ttyUSB0", baudrate=57600, timeout=1)

# If Using With Linux/RaspberryPi And Hardware UART:
# import serial
# uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)

finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)


def get_fingerprint():
    """Get A Finger Print Image, Template It, And See If It Matches"""
    print("Waiting For Image")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True

def get_fingerprint_detail():
    """Get A Finger Print Image, Template It, And See If It Matches
    This Time, Print Out Each Error Instead Of Just Returning On Failure"""
    print("Getting Image", end="")
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Image Taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No Finger Detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging Error")
        else:
            print("Other Error")
        return False

    print("Templating", end="")
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image To Messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could Not Identify Features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image Invalid")
        else:
            print("Other Error")
        return False

    print("Searching", end="")
    i = finger.finger_fast_search()
    
    # This Block Needs To Be Refactored When It Can Be Tested
    if i == adafruit_fingerprint.OK:
        print("Found Fingerprint")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No Match Found")
        else:
            print("Other Error")
        return False

def enroll_finger(location):
    """Take A 2 Finger Images And Template It Then Store In 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place Finger On Sensor", end="")
        else:
            print("Place Same Finger Again", end="")

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint.OK:
                print("Image Taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging Error")
                return False
            else:
                print("Other Error")
                return False

        print("Templating", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image To Messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could Not Identify Features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image Invalid")
            else:
                print("Other Error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating Model", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints Did Not Match")
        else:
            print("Other Error")
        return False

    print("Storing Model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad Storage Location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash Storage Error")
        else:
            print("Other Error")
        return False

    return True


def get_num():
    """Use input() To Get A Valid Number From 1 To 127 And Retry Till Success"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Enter Id # from 1-127: "))
        except ValueError:
            pass
    return i


while True:
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates:", finger.templates)
    print("e) Enroll Print")
    print("f) Find Print")
    print("d) Delete Print")
    print("----------------")
    c = input("> ")

    if c == "e":
        enroll_finger(get_num())
    if c == "f":
        if get_fingerprint():
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        else:
            print("Finger Not Found")
    if c == "d":
        if finger.delete_model(get_num()) == adafruit_fingerprint.OK:
            print("Deleted")
        else:
            print("Failed To Delete")
