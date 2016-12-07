from time import sleep
import socket
import sys


class iLightServer:
	pages = {'setup': """
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
		, 'control': """<!DOCTYPE html>
<html>
<head> <title>iLight</title> </head>
<form>
<h1>iLight Control</h1><hr>
Link: <a href="/isetup/">Setup</a><hr>
RGB:
<button name="RGB" value="0x0x0" type="submit">0%</button>
<button name="RGB" value="512x512x512" type="submit">50%</button>
<button name="RGB" value="1023x1023x1023" type="submit">100%</button>
</form>
</html>
"""}
	
	def setup(self):
		if sys.platform == 'esp8266':
			from machine import Pin, PWM
			setButton = Pin(14, Pin.IN, Pin.PULL_UP)
			doSet = setButton.value()
			self.LedR = PWM(Pin(5), freq=500, duty=0)  # D1
			self.LedG = PWM(Pin(4), freq=500, duty=0)  # D2
			self.LedB = PWM(Pin(0), freq=500, duty=0)  # D3
		else:
			pass
	
	def isResetDown(self):
		# return True
		return False

	
	def isWifiSetup(self):
		return True
	
	def run(self):
		self.setup()  # set GPIO...
		self.setting.load()
		if (not self.isWifiSetup()) or (self.isResetDown()):
			pgType = 'setup'
		else:
			pgType = 'control'
		# Listen port 80 / 8080
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if sys.platform == 'esp8266':
			s.bind(('', 80))
			print('Listen Port 80')
		else:
			s.bind(('', 8080))
			print('Listen Port 8080')
		s.listen(5)
		while True:
			try:
				conn, addr = s.accept()
				print("Accept Connection from '%s'" % str(addr))
				request = str(conn.recv(1024))
				print("Content:\n[%s]\n\n\n" % (request))
				# pos = request.find('GET /favicon.ico HTTP/1.1')
				# if pos > -1:
				# 	conn.send(self.pages[pgType])
				# 	conn.close()
				# 	print('Connection is closed!!\n\n\n\n')
				# 	continue
				pos = request.find('\r\n\r\nid=')
				if pos > -1:
					# setup page post back
					print("Update settings")
					kv = dict(s.split('=') for s in request[pos + 4:].split('&'))
					self.ssid = kv['id']
					self.pw = kv['pw']
					print("ESSID: '%s'  PW: '%s'" % (setting.ssid, setting.pw))
					# import network
					# ap_if = network.WLAN(network.AP_IF)
					# ap_if.config(essid="iLight", authmode=network.AUTH_WPA_WPA2_PSK, password="12345678")
					# sta_if = network.WLAN(network.STA_IF)
					# sta_if.active(True)
					# sta_if.connect("YY WIFI", "mary1234")
					self.setting.save()
				
				pSt = request.find('/?RGB=')
				if pSt > -1:
					# control page post back
					print("Update control\n")
					pEnd = request.find(' HTTP/1.1')
					try:
						Vs = tuple(int(s) for s in str(request)[pSt + 6:pEnd + 1].split('x'))
						print("R:%d G:%d B:%d\n\n" % Vs)
						if sys.platform == 'esp8266':
							self.LedR.duty(Vs[0])
							self.LedG.duty(Vs[1])
							self.LedB.duty(Vs[2])
						print("Save control status")
					except ValueError as e:
						pass
				if request.find('GET /isetup/') > -1:
					pgType = 'setup'
				if request.find('GET /icontrol/') > -1:
					pgType = 'control'
				# print('\n\nResponse:\n%s\n\n\n' % (self.pages(pgType)))
				conn.send(self.pages[pgType])
				conn.close()
				print('Connection is closed!!\n\n\n\n')
			except KeyboardInterrupt:
				# Save status
				print("Save control status")
				# release resource
				if self.platform == '8266':
					# GPIO
					self.LedR.deinit()
					self.LedG.deinit()
					self.LedB.deinit()
				# socket
				conn.close()
				print("Stop App")
				break


if __name__ == '__main__':
	iLightServer().run()
