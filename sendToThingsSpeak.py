import http_client
import time
import machine
from machine import ADC


def upToWeb(data):
	data.update({'api_key':'GJA4TBA1YS1V4VRW'})
	res = http_client.post('http://api.thingspeak.com/update.json', json=data )
	res.close()

def flash(ms):
	led = machine.Pin(2, machine.Pin.OUT)
	led.low()
	time.sleep_ms(ms)
	led.high()
	time.sleep_ms(ms)

def test(n):
	for i in range(n):
		print("Test No: " + str(i))
		upToWeb({"field1":i})
		time.sleep(20)
		flash(500)

adc = ADC(0)
# configure RTC.ALARM0 to be able to wake the device
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

flash(1000)
flash(1000)
flash(1000)
while(1):                                                                                                                                         
	# check if the device woke from a deep sleep
	if machine.reset_cause() == machine.DEEPSLEEP_RESET:
		flash(500)
		flash(500)
	
	v = adc.read()*0.00496
	upToWeb({"field1":v})
	
	if v > 3.6:
		rtc.alarm(rtc.ALARM0, 20000)
	else:
		rtc.alarm(rtc.ALARM0, 60000)
	
	machine.deepsleep()