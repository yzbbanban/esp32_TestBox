# main.py
import time
import network
import json
from machine import Pin, SPI
import dht
import ssd1306
import config
from umqtt.simple import MQTTClient

# ==========================================
# 1. 硬件初始化区域
# ==========================================
dht_sensor = dht.DHT11(Pin(4))
spi = SPI(1, baudrate=8000000, sck=Pin(12), mosi=Pin(11))
oled = ssd1306.SSD1306_SPI(128, 64, spi, Pin(9), Pin(10), Pin(8))


# ==========================================
# 2. 网络连接函数
# ==========================================
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        oled.fill(0)
        oled.text("Connecting WiFi...", 0, 25, 1)
        oled.show()
        print("正在连接 WiFi...")
        wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(0.5)
    ip = wlan.ifconfig()[0]
    print(f"WiFi 成功! IP: {ip}")
    return ip


# ==========================================
# 3. 核心业务主循环
# ==========================================
def main():
    ip = connect_wifi()
    sys_config = config.DEFAULT_CONFIG.copy()

    # 建立 MQTT 连接
    try:
        oled.fill(0)
        oled.text("Connecting MQTT...", 0, 25, 1)
        oled.show()

        mqtt = MQTTClient(config.MQTT_CLIENT_ID, config.MQTT_BROKER)
        mqtt.connect()
        print("MQTT 连接成功！")
    except Exception as e:
        print("MQTT 连接失败:", e)
        oled.fill(0)
        oled.text("MQTT Error!", 0, 25, 1)
        oled.show()
        time.sleep(2)
        return  # 连接失败则重启或退出

    while True:
        try:
            # 1. 采集物理数据
            dht_sensor.measure()
            t = dht_sensor.temperature()
            h = dht_sensor.humidity()

            # 2. 刷新屏幕
            oled.fill(0)
            oled.text("--- Smart Box ---", 0, 0, 1)
            oled.text(f"Temp: {t} C", 0, 18, 1)
            oled.text(f"Hum:  {h} %", 0, 34, 1)

            if t > sys_config.get("t_max", 30):
                oled.text("WARN: TOO HOT!", 0, 52, 1)
            elif h < sys_config.get("h_min", 40):
                oled.text("WARN: TOO DRY!", 0, 52, 1)
            else:
                oled.text(ip, 4, 52, 1)
            oled.show()

            # 3. 通过 MQTT 上报 JSON 数据
            payload = json.dumps({"temperature": t, "humidity": h})
            mqtt.publish(b"testbox/data", payload.encode())
            print(f"[MQTT 上报] {payload}")

        except Exception as e:
            print("循环发生错误:", e)

        time.sleep(2)


if __name__ == '__main__':
    main()