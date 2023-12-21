import requests
import time

first_time = time.time()

x = requests.get('http://192.168.1.129:5000/')

print(time.time() - first_time)