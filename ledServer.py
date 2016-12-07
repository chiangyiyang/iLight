def runLedServer():
	import sys
	import socket
	
	doSetup = False
	if sys.platform == 'esp8266':
		# import network
		# ap_if = network.WLAN(network.AP_IF)
		# ap_if.config(essid="iLight", authmode=network.AUTH_WPA_WPA2_PSK, password="12345678")
		from machine import Pin, PWM
		doSetup = (Pin(14, Pin.IN, Pin.PULL_UP).value() == 0)
	html = ""
	if doSetup:
		html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>iLight Setup</title>
</head>
<body>
<form method="post">
<h1>iLight Setup</h1><hr>
Link: <a href="/icontrol/">Control</a><hr>
SSID:<input name="id" type="text" value=""><br><br>
PASSWORD:<input  name="pw" type="password" value=""><br><br>
<button type="submit">OK</button>
<button type="reset">Reset</button>
</form>
</body>
</html>"""
	else:
		# HTML to send to browsers
		html = """<!DOCTYPE html>
<html>
<head> <title>iLight</title> </head>
<form>
<h1>iLight Control</h1><hr>
Link: <a href="/isetup/">Setup</a><hr>
LED0: 
<button name="LED" value="ON0" type="submit">LED ON</button>
<button name="LED" value="OFF0" type="submit">LED OFF</button><br><br>
LED2: 
<button name="LED" value="ON2" type="submit">LED ON</button>
<button name="LED" value="OFF2" type="submit">LED OFF</button>
</form>
</html>
"""
	# Setup PINS
	# LED0 = machine.Pin(0, machine.Pin.OUT)
	# LED2 = machine.Pin(2, machine.Pin.OUT)
	LedR = PWM(Pin(5), freq=500, duty=0)  # D1
	LedG = PWM(Pin(4), freq=500, duty=0)  # D2
	LedB = PWM(Pin(0), freq=500, duty=0)  # D3
	# Setup Socket WebServer
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 80))
	s.listen(5)
	while True:
		try:
			conn, addr = s.accept()
			print("Got a connection from %s\n\n" % str(addr))
			request = conn.recv(1024)
			print("Content = %s\n\n" % str(request))
			request = str(request)
			LEDON0 = request.find('/?LED=ON0')
			LEDOFF0 = request.find('/?LED=OFF0')
			LEDON2 = request.find('/?LED=ON2')
			LEDOFF2 = request.find('/?LED=OFF2')
			LedRGB = request.find('/?RGB=')
			if LEDON0 == 6:
				print('TURN LED0 ON')
				# LED0.low()
				LedR.duty(0)
			if LEDOFF0 == 6:
				print('TURN LED0 OFF')
				# LED0.high()
				LedR.duty(1024)
			if LEDON2 == 6:
				print('TURN LED2 ON')
				# LED2.low()
				LedG.duty(0)
			if LEDOFF2 == 6:
				print('TURN LED2 OFF')
				# LED2.high()
				LedG.duty(1024)
			if LedRGB == 6:
				endInx = request.find(' HTTP/1.1')
				Vs = [int(s) for s in str(request)[LedRGB + 6:endInx + 1].split(',')]
				LedR.duty(Vs[0])
				LedG.duty(Vs[1])
				LedB.duty(Vs[2])
			print('\n\n\n')
			response = html
			conn.send(response)
			conn.close()
		except KeyboardInterrupt:
			print("Stop server")
			LedR.deinit()
			LedG.deinit()
			LedB.deinit()
			# sta_if = network.WLAN(network.STA_IF)
			# sta_if.active(True)
			# sta_if.connect("YY WIFI", "mary1234")
			break
