from machine import Pin, SPI
import ssd1306
import time

# 1. 初始化高速 SPI 接口 (使用硬件 SPI 通道 1)
# SCL(D0) 接 GPIO 12, SDA(D1) 接 GPIO 11
spi = SPI(1, baudrate=8000000, sck=Pin(12), mosi=Pin(11))

# 2. 初始化额外的控制引脚
dc = Pin(9)
rst = Pin(10)
cs = Pin(8)

# 3. 创建 OLED 显示屏对象 (标准分辨率为 128x64)
oled = ssd1306.SSD1306_SPI(128, 64, spi, dc, rst, cs)

# 4. 清空屏幕缓存 (0 为全黑，1 为全亮)
oled.fill(0)
oled.show()

# 5. 写入测试文本 (格式: 字符串, X坐标, Y坐标, 颜色)
oled.text("--- SYSTEM ---", 10, 0, 1)
oled.text("Status: ONLINE", 0, 16, 1)
oled.text("Temp: 26.5 C", 0, 32, 1)
oled.text("Hum:  65.0 %", 0, 48, 1)

# 6. 将缓存中的画面一次性刷新到屏幕上
oled.show()