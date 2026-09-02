# esp32_TestBox


# ESP32-S3 (N16R8) MicroPython 开发环境搭建指南 (macOS + PyCharm)

本文档记录了在 macOS 环境下，为带有 8MB PSRAM 的高配版 ESP32-S3 (S3-N16R8) 刷入 MicroPython 固件，并使用 PyCharm 进行开发的完整流程。

## 一、 固件下载 (Octal-SPIRAM 支持)

由于使用的开发板型号为 **S3-N16R8**（16MB Flash, 8MB PSRAM），底层使用了八线 SPI 通信，必须下载专属的 Octal-SPIRAM 固件，否则无法调用额外的运行内存。

1. 访问 MicroPython 官方下载页，搜索 `ESP32-S3`。
2. 选择 **GENERIC ESP32-S3 (WROOM)**。
3. **关键：** 向下滚动页面，找到 **`Firmware (Support for Octal-SPIRAM)`** 栏目。
4. 在 Releases 列表中，点击带有 `(latest)` 标识的第一行中的 **`[.bin]`** 链接进行下载。

## 二、 macOS 终端烧录流程

不需要安装臃肿的 IDE，直接使用轻量级的命令行工具完成底层系统的刷写。

### 1. 准备烧录工具与识别端口
打开 Mac 终端 (Terminal)，安装官方烧录工具 `esptool`：
`pip3 install esptool`

使用 Type-C 数据线连接开发板与 Mac，查找设备端口：
`ls /dev/cu.*`
> *注：在 Apple Silicon 芯片的 Mac 上，端口通常显示为 `/dev/cu.usbmodemXXXX`（例如：`/dev/cu.usbmodem2101`）。*

### 2. 擦除出厂固件
防止分区表冲突，首次刷入前必须清空 Flash（注意替换为实际端口）：
`esptool --chip esp32s3 --port /dev/cu.usbmodem2101 erase_flash`
*等待终端提示 `Chip erase completed successfully`。*

### 3. 刷入 MicroPython 固件
在终端输入以下命令的**前半部分**（注意最后 `0` 后面保留一个空格），**先不要按回车**：
`esptool --chip esp32s3 --port /dev/cu.usbmodem2101 --baud 460800 write-flash -z 0 `

然后，将下载好的 `.bin` 文件直接**拖拽到终端窗口中**，系统会自动补全绝对路径。确认无误后按下回车执行烧录。
*等待进度条至 100% 且提示 `Hash of data verified`，系统刷写完成。*

---

## 三、 PyCharm 开发环境配置

通过官方插件，可以在 PyCharm 中实现代码自动补全、一键运行以及 REPL 硬件交互。

### 1. 安装 MicroPython 插件
1. 打开 PyCharm，按下 `Cmd + ,` 进入设置 (Settings)。
2. 在左侧菜单点击 **Plugins**。
3. 在顶部切换到 **Marketplace** 标签，搜索 `MicroPython` 并点击 **Install**。
4. **必须操作：** 安装完成后，点击 **Restart IDE** 重启 PyCharm，否则配置菜单不会生效。

### 2. 配置项目支持
1. 在 PyCharm 中新建一个纯 Python 项目。
2. 再次按下 `Cmd + ,` 打开设置。
3. 依次展开 **Languages & Frameworks** -> **MicroPython**。
4. 勾选 **Enable MicroPython support**。
5. **Device type** 选择 `ESP8266/ESP32`。
6. **Device path** 填入之前的设备端口（如 `/dev/cu.usbmodem2101`），点击 Apply。

### 3. 补全 API 依赖
返回代码编辑区，PyCharm 顶部会弹出黄色提示横幅（Packages required for MicroPython support are missing）。点击 **Install requirements** 自动下载硬件 API 存根，解决代码标红问题。

---

## 四、 硬件测试规范 (以 SHT30 I2C 传感器为例)

在项目根目录新建 `main.py`。针对农业环境测试箱中的温湿度采集，建议使用以下代码直接进行 I2C 协议通信，无需额外寻找第三方库。

```python
import machine
import time

# 初始化 I2C 总线 (S3 推荐 SDA=8, SCL=9)
i2c = machine.I2C(0, scl=machine.Pin(9), sda=machine.Pin(8), freq=400000)
SHT30_ADDR = 0x44

def scan_i2c():
    """扫描 I2C 硬件挂载状态"""
    devices = i2c.scan()
    if devices:
        for d in devices:
            print(f"找到 I2C 设备，地址: {hex(d)}")
    else:
        print("未找到任何 I2C 设备，请检查 3V3, GND, SDA, SCL 接线！")

def read_sht30():
    """读取并计算 SHT30 温湿度"""
    try:
        i2c.writeto(SHT30_ADDR, b'\x2C\x06')
        time.sleep_ms(50)
        data = i2c.readfrom(SHT30_ADDR, 6)
        
        t_raw = (data[0] << 8) | data[1]
        temp = -45 + (175 * t_raw / 65535.0)
        
        h_raw = (data[3] << 8) | data[4]
        humi = 100 * (h_raw / 65535.0)
        
        return temp, humi
    except OSError as e:
        print("SHT30 通信失败:", e)
        return None, None

if __name__ == '__main__':
    scan_i2c()
    while True:
        temperature, humidity = read_sht30()
        if temperature is not None:
            print(f"[环境监控] 温度: {temperature:.2f} °C  |  湿度: {humidity:.2f} %")
        time.sleep(2)