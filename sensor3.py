import os
import glob
import time
from boto.utils import get_instance_metadata
import datetime
import subprocess
from pyblinkm import BlinkM, Scripts
from boto.ec2 import cloudwatch

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
os.system('modprobe i2c-bcm2708')
os.system('modprobe i2c-dev')

device_folder = glob.glob('/sys/bus/w1/devices/28*')
device_file = [device_folder[0] + '/w1_slave',device_folder[1] + '/w1_slave', device_folder[2] + '/w1_slave', device_folder[3] + '/w1_slave', device_folder[4] + '/w1_slave', device_folder[5] + '/w1_slave']

blinkm = BlinkM()
blinkm.reset()

def read_temp_raw():
    f0 = open(device_file[0], 'r')
    lines_0 = f0.readlines()
    f0.close()
    f_1 = open(device_file[1], 'r')
    lines_1 = f_1.readlines()
    f_1.close()
    f_2 = open(device_file[2], 'r')
    lines_2 = f_2.readlines()
    f_2.close()
    f_3 = open(device_file[3], 'r')
    lines_3 = f_3.readlines()
    f_3.close()
    f_4 = open(device_file[4], 'r')
    lines_4 = f_4.readlines()
    f_4.close()
    f_5 = open(device_file[5], 'r')
    lines_5 = f_5.readlines()
    f_5.close()
    return lines_0 + lines_1 + lines_2 + lines_3 + lines_4 + lines_5

def set_led(temp):
        blinkm.reset()
	if temp > 15:    # to hot/makes good beer taste like vb
	     blinkm.reset()
	     blinkm.fade_to(255, 0, 0)  # solid red
	elif temp >10 and temp < 15 : # still to hot
	     blinkm.reset()
	     blinkm.play_script(Scripts.RED_FLASH)
	elif temp < 10 and temp> 5:   # nearly cold enough 
	     blinkm.reset()
	     blinkm.play_script(Scripts.GREEN_FLASH)
	elif temp < 5 and temp > 2:  # just right
	     blinkm.reset()
	     blinkm.fade_to(0, 255, 0)
	elif temp <2 and temp > 0:   #  to cold
	     blinkm.reset()
	     blinkm.fade_to(0, 0, 255)
	elif temp < 0:  #  to fing cold
	     blinkm.reset()
	     blinkm.play_script(Scripts.BLUE_FLASH)
	else:
             blinkm.reset()
             blinkm.play_script(Scripts.THUNDERSTORM)

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t='), lines[3].find('t='),  lines[5].find('t='), lines[7].find('t='), lines[9].find('t='),lines[11].find('t=')
    temp = float(lines[1][equals_pos[0]+2:])/1000, float(lines[3][equals_pos[1]+2:])/1000 ,float(lines[5][equals_pos[2]+2:])/1000, float(lines[7][equals_pos[2]+2:])/1000,float(lines[9][equals_pos[2]+2:])/1000 ,float(lines[11][equals_pos[2]+2:])/1000



    return temp

def send_metric(val,title):
    conn_cw=cloudwatch.connect_to_region('us-east-1')
    conn_cw.put_metric_data(namespace='kegmetrics',name=title,value=val,dimensions={'temp':'c'})
	
while True:
        temp = read_temp()
        set_led(temp[0])
	print('T1:'+str(temp[0])+' T2:'+str(temp[1])+' T3:'+str(temp[2])+' T4:'+str(temp[3]) +' T5:'+str(temp[4]) +' T6:'+str(temp[5]))	
        send_metric(temp[0],'T1')
        time.sleep(1)
        send_metric(temp[1],'T2')
	time.sleep(1)
        send_metric(temp[2],'T3')
        time.sleep(1)
        send_metric(temp[3],'T4')
        time.sleep(1)
        send_metric(temp[4],'T5')
        time.sleep(1)
        send_metric(temp[5],'T6')

