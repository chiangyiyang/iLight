from time import sleep
import socket
import sys


class iLightServer:
	ssid = ''
	pw = ''
	ap_on = '1'
	sta_on = '1'
	
	def updateWifi(self):
		print('\nUpdate Wifi\n')
		if sys.platform == 'esp8266':
			import network
			ap_if = network.WLAN(network.AP_IF)
			if self.ap_on == '1':
				ap_if.active(True)
				ap_if.config(essid="iLight", authmode=network.AUTH_WPA_WPA2_PSK, password="12345678")
				print('\nEnable AP MODE\n')
			else:
				print('\nDisable AP MODE\n')
				ap_if.active(False)
			
			sta_if = network.WLAN(network.STA_IF)
			if self.sta_on == '1':
				print('\nEnable Station MODE\n')
				sta_if.active(True)
				sta_if.connect(self.ssid, self.pw)
				sleep(10)
				if not sta_if.isconnected():
					print('Link to AP(%s) failed!!' % self.ssid)
			else:
				print('\nDisable Station MODE\n')
				sta_if.active(False)
	
	def loadSetting(self):
		print('Load Settings')
		try:
			with open("settings.ini") as f:
				kv = dict(s.split('=') for s in f.read().split('&'))
				self.ssid = kv['ssid']
				self.pw = kv['pw']
				self.ap_on = kv['ap_on']
				self.sta_on = kv['sta_on']
				f.close()
				self.updateWifi()
		
		except  Exception as ex:
			print("Error occurred in loadSetting:\n%s\n\n" % ex)
	
	def saveSetting(self):
		print('Save Settings')
		with open("settings.ini", "w") as f:
			f.write("ssid=%s&pw=%s&ap_on=%s&sta_on=%s" % (self.ssid, self.pw, self.ap_on, self.sta_on))
			f.close()
	
	def getPage(self, pgType):
		if pgType == 'setup':
			return ("""
	<!DOCTYPE html>
	<html lang="en">
	<head>
	<meta charset="UTF-8">
	<title>iLight Setup</title>
	</head>
	<body>
	<form>
	<h1>iLight Setup</h1><hr>
	Link: <a href="/icontrol/">Control</a><hr>
	SSID:<input name="ssid" type="text" value="{0}"><br><br>
	PASSWORD:<input  name="pw" type="password" value=""><br><br>
	AP MODE:<input  name="ap_on" type="checkbox" value="1" {1}><br><br>
	Station MODE:<input  name="sta_on" type="checkbox" value="1" {2}><br><br>
	<button type="submit">OK</button>
	<button type="reset">Reset</button>
	</form>
	</body>
	</html>""".format(self.ssid,
			          ('checked' if self.ap_on == '1' else ''),
			          ('checked' if self.sta_on == '1' else '')))
		if pgType == 'control':
			return """<!DOCTYPE html>
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
	"""
	
	def setup(self):
		if self.isResetDown():
			self.ap_on = '1'
		if sys.platform == 'esp8266':
			from machine import Pin, PWM
			self.LedR = PWM(Pin(5), freq=500, duty=0)  # D1
			self.LedG = PWM(Pin(4), freq=500, duty=0)  # D2
			self.LedB = PWM(Pin(0), freq=500, duty=0)  # D3
		else:
			pass
	
	def isResetDown(self):
		if sys.platform == 'esp8266':
			from machine import Pin
			return Pin(14, Pin.IN, Pin.PULL_UP).value() == 0
		else:
			return False
	
	def isWifiSetup(self):
		return True
	
	def run(self):
		self.setup()  # set GPIO...
		self.loadSetting()
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
				# if pos == 2:
				# 	conn.close()
				# 	continue
				pSt = request.find('/isetup/?ssid=')
				if pSt == 6:
					# setup page back   ex. /isetup/?ssid=myAP&pw=12345678 HTTP
					print("Update settings")
					pEnd = request.find(' HTTP/1.1')
					try:
						kv = dict(s.split('=') for s in request[pSt + 9:pEnd].split('&'))
						self.ssid = kv['ssid']
						self.pw = kv['pw']
						self.sta_on = (kv['sta_on'] if 'sta_on' in kv.keys() else '')
						self.ap_on = (kv['ap_on'] if 'ap_on' in kv.keys() else '')
						self.ap_on = ('1' if self.sta_on == '' else self.ap_on)
						print("ssid: '%s'  pw: '%s'  ap_on: '%s'  sta_on: '%s'" % (
							self.ssid, self.pw, self.ap_on, self.sta_on))
						self.updateWifi()
						self.saveSetting()
					except:
						pass
				
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
				try:
					conn.send(self.getPage(pgType).encode())
					conn.close()
					print('Connection is closed!!\n\n\n\n')
				except OSError:
					print('Error occurred when sending response!!\n\n\n\n')
			
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
