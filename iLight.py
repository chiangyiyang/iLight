from time import sleep
import socket


class Setting:
	def load(self):
		print('Load Settings')

	def save(self):
		print('Save Settings')

setting = Setting()

def setup():
	# set hardware
	# import machine
	# from machine import Pin, PWM
	# setButton = Pin(14, Pin.IN, Pin.PULL_UP)
	# doSet = setButton.value()
	pass


def isResetDown():
	# return True
	return False


def getPage(type):
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
SSID:<input name="id" type="text" value=""><br>
PASSWORD:<input  name="pw" type="password" value=""><br>
<button type="submit">OK</button>
<button type="reset">Cancel</button>
</form>
</body>
</html>"""
		, 'control': """
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
</html>"""}
	return pages[type]


def isWifiSetup():
	return True


def run2():
	setup()  # set GPIO...
	setting.load()
	if (not isWifiSetup()) or (isResetDown()):
		print("Response Wifi setup page")
		response = getPage('setup')
	else:
		response = getPage('control')
	# Listen port 80 / 8080
	print('Listen Port 80 / 8080')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind(('', 8080))
	s.listen(5)
	while True:
		try:
			conn, addr = s.accept()
			print ("Accept Connection from '%s'" % str(addr))
			request = conn.recv(1024)
			print("Content:\n[%s]\n\n\n" % (request))
			pos = request.find('\r\n\r\nid=')
			if pos > -1:
				# setup page post back
				print ("Update settings")
				kv = dict(s.split('=') for s in request[pos + 4:].split('&'))
				setting.ssid = kv['id']
				setting.pw = kv['pw']
				print ("ESSID: '%s'  PW: '%s'" % (setting.ssid, setting.pw))
				# import network
				# ap_if = network.WLAN(network.AP_IF)
				# ap_if.config(essid="iLight", authmode=network.AUTH_WPA_WPA2_PSK, password="12345678")
				# sta_if = network.WLAN(network.STA_IF)
				# sta_if.active(True)
				# sta_if.connect("YY WIFI", "mary1234")
				setting.save()

			pSt = request.find('/?RGB=')
			if pSt > -1:
				# control page post back
				print ("Update control\n")
				pEnd = request.find(' HTTP/1.1')
				Vs = [int(s) for s in str(request)[pSt + 6:pEnd + 1].split(',')]
				print("R:%d G:%d B:%d\n\n" % Vs)
				pass  # LedR.duty(Vs[0])
				pass  # LedG.duty(Vs[1])
				pass  # LedB.duty(Vs[2])
				print ("Save control status")

			print('\n\nResponse:\n%s\n\n\n' % (response))
			conn.send(response)
			conn.close()
		except KeyboardInterrupt:
			# Save status
			print ("Save control status")
			# release resource
			# GPIO
			# socket
			# ...
			print ("Stop App")
			break


if __name__ == '__main__':
	run2()
