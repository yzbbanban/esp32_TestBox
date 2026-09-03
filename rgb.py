import machine
import neopixel
import time

# --- 1. 硬件初始化 ---
# 这块 ESP32-S3 开发板的板载 RGB 灯通常连接在 GPIO 48
LED_PIN = 48
pin = machine.Pin(LED_PIN, machine.Pin.OUT)

# 初始化 NeoPixel 对象，1 代表只有 1 颗灯珠
np = neopixel.NeoPixel(pin, 1)

print("--- 开始板载 RGB 灯测试 ---")

# --- 2. 控制逻辑 ---
try:
    while True:
        # 设置为红色 (R, G, B)，数值范围 0-255
        # 注意：不要设置太高（比如255），会非常刺眼！20就足够亮了。
        np[0] = (20, 0, 0)
        np.write()  # 必须调用 write() 才会生效
        print("状态: 红色亮起")
        time.sleep(1)

        # 设置为绿色
        np[0] = (0, 20, 0)
        np.write()
        print("状态: 绿色亮起")
        time.sleep(1)

        # 设置为蓝色
        np[0] = (0, 0, 20)
        np.write()
        print("状态: 蓝色亮起")
        time.sleep(1)

        # 熄灭
        np[0] = (0, 0, 0)
        np.write()
        print("状态: 熄灭")
        time.sleep(1)

except KeyboardInterrupt:
    # 捕获停止命令，确保程序退出时灯是灭的
    np[0] = (0, 0, 0)
    np.write()
    print("测试结束，灯已熄灭")