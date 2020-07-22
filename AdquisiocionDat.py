import RPi.GPIO as GPIO
import datetime
import time
from time import sleep
from Adafruit_CharLCD import Adafruit_CharLCD
import os
import Adafruit_MCP3008
from ina219 import INA219

################################################################################################################
##### IMPORTANTE CAMBIAR NUMERO DEL ARCHIVO LINEA 25 #####
################################################################################################################

ina = INA219(shunt_ohms=0.1,
             max_expected_amps = 0.6,
             address=0x40)
ina.configure(voltage_range=ina.RANGE_16V,
              gain=ina.GAIN_AUTO,
              bus_adc=ina.ADC_128SAMP,
              shunt_adc=ina.ADC_128SAMP)

lcd = Adafruit_CharLCD(rs=21, en=20, d4=16, d5=12, d6=7, d7=8,
                       cols=16, lines=2)

archivo = open("ConjuntodeDatos7.txt", "w+")
GPIO.setmode(GPIO.BCM)
GPIO.setup(15,GPIO.IN)  
GPIO.setup(14,GPIO.IN)
Wind_PIN = 15

WindCount=0
HallCount = 0

# Software SPI configuration:
CLK  = 25
MISO = 24
MOSI = 23
CS   = 18
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


def velocidad(channel):
    global WindCount
    WindCount += 1

def HALL(Rain_PIN):
    global HallCount
    HallCount += 1

def main():
    #archivo.write("| Vel Viento |   Direccion |   V    |   I     |   P    |  RPM   |  \n")
    global WindCount 
    global HallCount
    WindSpeed = 0.00
    try:
        GPIO.add_event_detect(15, GPIO.RISING, callback=velocidad, bouncetime=50)
        GPIO.add_event_detect(14, GPIO.RISING, callback=HALL)
        print('| Vel Viento |   Direccion |   V    |   I     |   P    |  RPM   |    Fecha    |   Hora      |')
        while 1:
            #  V E L O C I D A D
            sleep(3)
            lcd.clear()            
            # convert to mp/h using the formula V=P(2.25/T)
            # V = P(2.25/3) = P * 0.75
            WindSpeed = WindCount*1.0058375/3
            #lcd.message('{0:0.2f}  Pulsos\n'.format(WindCount))
            #lcd.message('{0:0.2f}  m/s'.format(WindSpeed))
            #lcd.message('\n')
            WindCount = 0.00
            archivo.write('%4.5f    ' % WindSpeed)
            
            # D I R E C C I O N
           
            #print('| {0:>4} '.format(mcp.read_adc(0)))
            direccion=float(mcp.read_adc(7))*360/1024
            
            if direccion < 22:
                direccionStr = 'Norte'
            elif direccion < 67:
                direccionStr = 'Norte-Este'
            elif direccion < 112:
                direccionStr = 'Este'
            elif direccion < 157:
                direccionStr = 'Sur-Este'
            elif direccion < 212:
                direccionStr = 'Sur'
            elif direccion < 247:
                direccionstr = 'Sur-Oeste'
            elif direccion < 292:
                direccionStr = 'Oeste'
            elif direccion < 337:
                direccionStr = 'Norte-Oeste'
            else:
                direccionStr = 'Norte'
            #lcd.message("Algo")
            archivo.write('%s    ' % direccionStr)            
            # C O R R I E N T E

            v=ina.voltage()
            i=ina.current()
            p=ina.power()
            #print(v, i, p)
            archivo.write('%4.5f    ' % v)
            archivo.write('%4.5f    ' % i)
            archivo.write('%4.5f    ' % p)	
            
            #V E L O C I D A D   A N G U L A R
            
            RPM=2.5*HallCount
            #print('RPM: ', RPM)
            HallCount = 0
            archivo.write('%4.5f    ' % RPM)
            
			# M O S T R A R   E N   P A N T A L L A
            
            hora = time.strftime("%H:%M:%S")
            fecha = time.strftime("%d/%m/%y")
            archivo.write('%s   ' % hora)
            archivo.write('%s   \n' % fecha)
            print('| {0:>10.4f} | {1:>11} | {2:>6.4f} | {3:>6.4f} | {4:>6.4f} | {5:>6.4f} | {6:>11} | {7:>11} |'.format(WindSpeed, direccionStr, v,i,p, RPM, fecha, hora))
            lcd.message('{0:0.1f} V {1:0.1f} rpm'.format(v, RPM))
            lcd.message('\n{0:0.1f} mW {1:0.1f} m/s'.format(p, WindSpeed))
            
    except KeyboardInterrupt:
        archivo.close()
        lcd.clear
        print ("\nCtrl-C..")
        lcd.message('Ctrl-c... \nAdios')
        sleep(1)
        lcd.clear
        
    finally:
        lcd.clear
        GPIO.cleanup()
        print('Finally')
        sleep(1)
        lcd.clear
        archivo.close()

##############################################################

if __name__ == "__main__":
   main()

