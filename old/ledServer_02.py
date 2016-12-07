def runLedServer():
	# import network
	# ap_if = network.WLAN(network.AP_IF)
	# ap_if.config(essid="iLight", authmode=network.AUTH_WPA_WPA2_PSK, password="12345678")
	import socket
	# import machine
	# from machine import Pin, PWM
	# setButton = Pin(14, Pin.IN, Pin.PULL_UP)
	# doSet = setButton.value()
	doSet = 0
	setup_htm = """
	<!DOCTYPE html>
	<html lang="en">
	<head>
	<meta charset="UTF-8">
	<title>iLight Setup</title>
	</head>
	<body>
	<form method="post">
	<h1>iLight Setup</h1><hr>
	SSID:<input name="id" type="text" value=""><br>
	PASSWORD:<input  name="pw" type="password" value=""><br>
	<button type="submit">OK</button>
	<button type="reset">Cancel</button>
	</form>
	</body>
	</html>"""
	normal_htm = """<!DOCTYPE html>
	<html>
	<head> <title>iLight</title> </head>
	<form>
	LED0:
	<button name="LED" value="ON0" type="submit">LED ON</button>
	<button name="LED" value="OFF0" type="submit">LED OFF</button><br><br>
	LED2:
	<button name="LED" value="ON2" type="submit">LED ON</button>
	<button name="LED" value="OFF2" type="submit">LED OFF</button>
	<button name="SET" value="1" type="submit">Setup</button>
	</form>
	</html>
	"""
	html = ""
	# if doSet == 0:
	# 	html = setup_htm
	# else:
	# 	# HTML to send to browsers
	# 	html = normal_htm
	# Setup PINS
	# LedR = PWM(Pin(5), freq=500, duty=0)  # D1
	# LedG = PWM(Pin(4), freq=500, duty=0)  # D2
	# LedB = PWM(Pin(0), freq=500, duty=0)  # D3
	# Setup Socket WebServer
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 8080))
	s.listen(5)
	while True:
		try:
			conn, addr = s.accept()
			print("Got a connection from %s\n\n" % str(addr))
			request = conn.recv(1024)
			print("Content = %s\n\n" % (request))
			try:
				if doSet == 0:
					sInx = request.find('\r\n\r\nid=')
					if sInx > -1:
						kv = dict(s.split('=') for s in request[sInx + 4:].split('&'))
						ssid = kv['id']
						pw = kv['pw']
						print ("ESSID: '%s'  PW: '%s'" % (ssid, pw))
						doSet = 1
				else:
					SET_INX = request.find('/?SET=1')
					if SET_INX > -1:
						doSet = 0
						continue
					LedRGB = request.find('/?RGB=')
					if LedRGB == 6:
						endInx = request.find(' HTTP/1.1')
						Vs = [int(s) for s in str(request)[LedRGB + 6:endInx + 1].split(',')]
						# LedR.duty(Vs[0])
						# LedG.duty(Vs[1])
						# LedB.duty(Vs[2])

			except ValueError:
				print('ValueError\n\n\n')
			print('\n\n\n')
			if doSet == 0:
				html = setup_htm
			else:
				html = normal_htm
			response = html
			conn.send(response)
			conn.close()
		except KeyboardInterrupt:
			print("Stop server")
			# LedR.deinit()
			# LedG.deinit()
			# LedB.deinit()
			# sta_if = network.WLAN(network.STA_IF)
			# sta_if.active(True)
			# sta_if.connect("YY WIFI", "mary1234")
			break


if __name__ == '__main__':
	runLedServer()
