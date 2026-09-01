import dht
import network
import socket
import time
from machine import Pin

# --- 1. 连接你的 Wi-Fi ---
WIFI_SSID = "111"
WIFI_PASS = "111"


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("正在连接 Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        while not wlan.isconnected():
            time.sleep(1)
    print("Wi-Fi 连接成功！IP 地址:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]


# --- 2. 初始化传感器 ---
sensor = dht.DHT11(Pin(4))


# --- 3. 构建极简网页前端模板 ---
def web_page(temp, hum):
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="3"> <!-- 每3秒自动刷新一次页面 -->
    <title>农业微型测试箱看板</title>
    <style>
        body {{ font-family: Arial; text-align: center; margin-top: 50px; background: #f4f4f9; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); display: inline-block; }}
        h2 {{ color: #333; }}
        .data {{ font-size: 28px; font-weight: bold; color: #2e7d32; margin: 15px 0; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>🌱 农业微型环境测试箱</h2>
        <div class="data">温度: {temp} ℃</div>
        <div class="data">湿度: {hum} %</div>
        <p style="color: #888; font-size: 12px;">页面每 3 秒自动更新实时数据</p>
    </div>
</body>
</html>
"""
    return html


# --- 4. 启动 Web 服务主循环 ---
def start_server(ip):
    # 【已修复】这里将端口 80 明确转换为整型，避免元组报错
    addr = socket.getaddrinfo(ip, 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print(f"Web 服务器已启动，请在浏览器中访问: http://{ip}")

    while True:
        try:
            conn, client_addr = s.accept()
            # 读取浏览器发来的请求
            request = conn.recv(1024)

            # 读取当前传感器数据
            try:
                sensor.measure()
                t = sensor.temperature()
                h = sensor.humidity()
            except:
                t, h = "--", "--"

            # 组装并发送 HTML 响应
            response = web_page(t, h)
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()
        except Exception as e:
            print("连接异常:", e)
            try:
                conn.close()
            except:
                pass


if __name__ == '__main__':
    ip_addr = connect_wifi()
    start_server(ip_addr)