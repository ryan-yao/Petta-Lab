import serial
from serial import rs485
import sys
import fileAndDataTree
import time
import os


OFFSET = -14.5
LOG_TIME_SECONDS = 60
MEASURE_TIME_SECONDS = 1

MIN_DIFF_PRESSURE_PSI = 5
MIN_DIFF_PRESSURE_TIMER_SEC = 5

## TODO: Move to config file, make simple startup GUI
PRESSURE_IN_ADDRESS = 123
PRESSURE_OUT_ADDRESS = 124

## Expected input format: port #, [addr1,addr2,addr3, ..]
## if no addr is indicated, default to 123
##
## params:
## port - integer value indicating the port # the RS485 is connected to
## addrX - the address number identifying each PX459

def isAddressOutOfRange(address):
    if(address < 1  or address > 127):
                print("Address must be between 001 and 127")
                sys.exit()
            
def dataInput(inputs):
    addressArr = []

    if len(inputs) >= 3:
        for i in range(2,len(inputs)):
            isAddressOutOfRange(int(inputs[i]))
            addressArr.append(int(inputs[i]))
    else:
        addressArr.append(123)
        
    return addressArr

def sendCommand(COM_PORT, command):
    if not COM_PORT.is_open:
        COM_PORT.open()
    COM_PORT.write(command)
    COM_PORT.flush()
    return COM_PORT.readline().decode().split()

def getPressure(COM_PORT, addressArr):
    for i in range(len(addressArr)):
        binaryReadCommand = '#' + addressArr[i] +'P\r\n'
        rawVal = sendCommand(COM_PORT, binaryReadCommand)
        print(int(pressureByte))
    COM_PORT.close()

def parseRawPressure(outputString,offset):
    aSplit = outputString[0].split('@')
    pressureVal = float(aSplit[1][3:]) + offset
    return str(pressureVal)

if __name__ == "__main__":

    portNum = 'COM' + str(sys.argv[1])
    addresses = dataInput(sys.argv)
    
    print(addresses)
    COM_PORT = serial.Serial(port = portNum, baudrate = 115200,
                             bytesize = 8, parity = 'N', stopbits = 1, timeout = 3)

    COM_PORT.rs485_mode = serial.rs485.RS485Settings()
    collectData = True

    switchedToCity = False
    
    loopNumber = -1
    diffPressureWarningTimer = 0
    while(collectData):
        differentialPressure = 0
        pressureIn = 0
        pressureOut = 0
        loopNumber += 1
        for i in range(len(addresses)):
        
            strcommand = '#' + str(addresses[i]) + 'P\r\n'
            command = strcommand.encode()

            spacesplit = sendCommand(COM_PORT,command)

            pressureStr = parseRawPressure(spacesplit,OFFSET)
            if addresses[i] ==PRESSURE_IN_ADDRESS :
                pressureIn = float(pressureStr)
            else:
                pressureOut = float(pressureStr)
                
        differentialPressure = pressureIn-pressureOut
        #print(differentialPressure)
        if differentialPressure < MIN_DIFF_PRESSURE_PSI:
            diffPressureWarningTimer += 1
        else:
            diffPressureWarningTimer = 0

        if diffPressureWarningTimer >= MIN_DIFF_PRESSURE_TIMER_SEC and not switchedToCity:
            os.system("C:\Python27\python.exe C:\Chilled_Water_Relay\Run_City_Water.py 1")
            switchedToCity = True
            ## switch water supply        
        
        if loopNumber%LOG_TIME_SECONDS == 0 or loopNumber == 0:
            fileAndDataTree.logData(str(PRESSURE_IN_ADDRESS),str(pressureIn))
            fileAndDataTree.logData(str(PRESSURE_OUT_ADDRESS),str(pressureOut))
            loopNumber=0 #reset the loop counter

        time.sleep(MEASURE_TIME_SECONDS-11/60)
        
    COM_PORT.close()

    
    
