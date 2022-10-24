from datetime import datetime
import logging
import time
import psutil

logging.basicConfig(filename='converter_2.log', format='%(asctime)s %(message)s', level=logging.INFO)

def display_usage(cpu_usage, mem_usage, disk_usage):
    logging.info("; Memory Usage; {}; CPU Usage; {}; Disk_Usage; {} ".format(mem_usage.percent, cpu_usage, disk_usage.percent))

while True:
    display_usage(psutil.cpu_percent(), psutil.virtual_memory(), psutil.disk_usage("/"))
    time.sleep(1)