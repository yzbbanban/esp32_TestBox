import dht
import network
import socket
import time
from machine import Pin
import neopixel
from config import WIFI_SSID, WIFI_PASS, DEFAULT_CONFIG
# 将配置导入到全局变量中供网页动态修改
config = DEFAULT_CONFIG.copy()


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)

    # 1. 先强行关闭 Wi-Fi，清理底层残留状态机
    wlan.active(False)
    time.sleep(1)

    # 2. 重新激活
    wlan.active(True)
    time.sleep(1)

    if not wlan.isconnected():
        print("正在连接 Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)

        # 增加一个超时计数器（防止卡死在无限循环里）
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            print(".", end="")

        if not wlan.isconnected():
            print("\nWi-Fi 连接超时，请检查密码或路由器状态！")
            return None

    print("\nWi-Fi 连接成功！IP 地址:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]


# 初始化传感器与板载 RGB 灯 (GPIO 48)
sensor = dht.DHT11(Pin(4))
np = neopixel.NeoPixel(Pin(48), 1)


def web_page(temp, hum, status):
    alert_color = "#d32f2f" if status else "#2e7d32"
    status_text = "⚠️ 报警：环境指标超限！" if status else "🟢 系统运行正常"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="3">
    <title>农业微型测试箱看板</title>
    <style>
        body {{ font-family: Arial; text-align: center; margin-top: 20px; background: #f4f4f9; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); display: inline-block; width: 320px; }}
        .data {{ font-size: 24px; font-weight: bold; color: {alert_color}; margin: 8px 0; }}
        .status {{ font-size: 15px; font-weight: bold; color: {alert_color}; margin-bottom: 12px; }}
        input {{ width: 60px; padding: 4px; text-align: center; }}
        .form-group {{ margin: 6px 0; font-size: 13px; text-align: left; display: flex; justify-content: space-between; align-items: center; }}
        button {{ background: #2e7d32; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; margin-top: 10px; width: 100%; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>🌱 智能微型测试箱</h2>
        <div class="status">{status_text}</div>
        <div class="data">温度: {temp} ℃</div>
        <div class="data">湿度: {hum} %</div>
        <hr>
        <form action="/" method="GET">
            <div class="form-group"><span>温度上限 (°C):</span><input type="text" name="t_max" value="{config['t_max']}"></div>
            <div class="form-group"><span>温度下限 (°C):</span><input type="text" name="t_min" value="{config['t_min']}"></div>
            <div class="form-group"><span>湿度上限 (%):</span><input type="text" name="h_max" value="{config['h_max']}"></div>
            <div class="form-group"><span>湿度下限 (%):</span><input type="text" name="h_min" value="{config['h_min']}"></div>
            <button type="submit">保存报警阈值</button>
        </form>
    </div>
</body>
</html>
"""
    return html


def parse_query(request_str):
    try:
        if "GET /?" in request_str:
            query_start = request_str.find("/?") + 2
            query_end = request_str.find(" HTTP/")
            query_str = request_str[query_start:query_end]
            pairs = query_str.split("&")
            for pair in pairs:
                key, val = pair.split("=")
                if key in config:
                    config[key] = float(val)
            print("已更新报警阈值:", config)
    except Exception as e:
        print("解析参数错误:", e)


def start_server(ip):
    addr = socket.getaddrinfo(ip, 80)[0][-1]
    s = socket.socket()

    # 【新增这行】允许端口立即重用，避免重启报错 EADDRINUSE
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(addr)
    s.listen(5)
    print(f"Web 服务器已启动，访问地址: http://{ip}")

    while True:
        try:
            conn, client_addr = s.accept()
            request = conn.recv(1024).decode('utf-8')
            parse_query(request)

            try:
                sensor.measure()
                t = sensor.temperature()
                h = sensor.humidity()
            except:
                t, h = 25.0, 50.0

            is_alarm = (t > config['t_max'] or t < config['t_min'] or
                        h > config['h_max'] or h < config['h_min'])

            if is_alarm:
                # 报警：让板载灯闪烁 3 次红光
                for _ in range(3):
                    np[0] = (40, 0, 0)  # 亮红光
                    np.write()
                    time.sleep(0.2)
                    np[0] = (0, 0, 0)  # 灭
                    np.write()
                    time.sleep(0.2)
                # 保持最后留红
                np[0] = (40, 0, 0)
            else:
                # 正常：常亮绿光
                np[0] = (0, 40, 0)
            np.write()

            response = web_page(t, h, is_alarm)
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