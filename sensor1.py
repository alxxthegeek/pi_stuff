import os
import glob
import time
from boto.utils import get_instance_metadata
import datetime

from boto.ec2 import cloudwatch
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

device_folder = glob.glob('/sys/bus/w1/devices/28*')
device_file = [device_folder[0] + '/w1_slave',device_folder[1] + '/w1_slave']

def read_temp_raw():
    f1 = open(device_file[0], 'r')
    lines_1 = f1.readlines()
    f1.close()
    f_2 = open(device_file[1], 'r')
    lines_2 = f_2.readlines()
    f_2.close()
    return lines_1 + lines_2

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t='), lines[3].find('t=')
    temp = float(lines[1][equals_pos[0]+2:])/1000, float(lines[3][equals_pos[1]+2:])/1000
    return temp

def send_metric():
    conn_cw=cloudwatch.connect_to_region('us-east-1')
    conn_cw.put_metric_data(namespace='my_namespace',name='my_metric',value='1',dimensions={'temp':'c'})
	
while True:
        temp = read_temp()
	print('T1:'+str(temp[0])+' T2:'+str(temp[1]))	
	time.sleep(5)
