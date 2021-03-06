# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
import webrepl
webrepl.start()
gc.collect()

# import ledServer
# ledServer.runLedServer()
# import iLight
# iLight.run()

from iLight import iLightServer
iLightServer().run()
