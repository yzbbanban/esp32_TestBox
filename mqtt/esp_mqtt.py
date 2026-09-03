# 1. 激活并连接 Wi-Fi（请替换为你的实际 SSID 和密码）
import network
import time
wlan = network.WLAN(network.STA_IF)
wlan.active(False)
time.sleep(1)

# 2. 重新激活
wlan.active(True)
time.sleep(1)
wlan.connect("111", "111")

# 2. 检查连接状态，如果是 True，说明连上了
wlan.isconnected()

# 3. 重新执行安装命令（可以顺便把屏幕驱动一起装了）
import mip
mip.install("umqtt.simple")
mip.install("ssd1306")