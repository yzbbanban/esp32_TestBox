import dht
from machine import Pin
import time

# --- 1. 初始化传感器 ---
# 将 GPIO 4 设置为连接 DHT11 的数据引脚
sensor_pin = Pin(4)
sensor = dht.DHT11(sensor_pin)

print("--- 开始读取 DHT11 温湿度数据 ---")

# --- 2. 循环读取并打印 ---
while True:
    try:
        # 触发传感器进行一次测量
        sensor.measure()

        # 获取温度和湿度数据
        temp = sensor.temperature()
        humidity = sensor.humidity()

        print(f"当前环境 -> 温度: {temp}°C, 湿度: {humidity}%")

    except OSError as e:
        # DHT11 对时序比较敏感，偶尔会读取失败，这里做个简单的容错
        print("读取失败，请检查接线...")

    # DHT11 的采样频率不能太高，官方建议每次读取至少间隔 2 秒
    time.sleep(2)