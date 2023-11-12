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
device_file = [device_folder[0] + '/w1_slave',device_folder[1] + '/w1_slave']

blinkm = BlinkM()
blinkm.reset()

def read_temp_raw():
	catdata0 = subprocess.Popen(['cat',device_file[0]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out0,err = catdata0.communicate()
	out_decode0 = out0.decode('utf-8')
	lines0 = out_decode0.split('\n')
        lines_0 = ','.join(lines0).strip()
        lines_0 = lines_0.split(',')

        catdata1 = subprocess.Popen(['cat',device_file[1]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out1,err = catdata1.communicate()
	out_decode1 = out1.decode('utf-8')
	lines_1 = out_decode1.split('\n')
        lines_1 = ','.join(lines_1).strip()
        lines_1 = lines_1.split(',')

        print(lines_1)
	return lines_0 + lines_1

def set_led(temp):
        blinkm.reset()
	if temp > 15:    # to damn hot/makes good beer taste like vb
	     blinkm.reset()
	     blinkm.fade_to(255, 0, 0)  # solid red
	elif temp >10 and temp < 15 : # to hot
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
    print(lines[0].strip()[-3:])
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t='), lines[3].find('t=')
    temp = float(lines[1][equals_pos[0]+2:])/1000, float(lines[3][equals_pos[1]+2:])/1000
    return temp

def send_metric(val,title):
    conn_cw=cloudwatch.connect_to_region('us-east-1')
    conn_cw.put_metric_data(namespace='kegmetrics',name=title,value=val,dimensions={'temp':'c'})
	
while True:
        temp = read_temp()
	print('T1:'+str(temp[0])+' T2:'+str(temp[1]))	
        send_metric(temp[0],'T1')
        time.sleep(1)
        send_metric(temp[1],'T2')
	time.sleep(1)
