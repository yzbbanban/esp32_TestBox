# config.template.py - 配置文件模版（提交到 Git）
WIFI_SSID = "your_wifi_ssid_here"
WIFI_PASS = "your_wifi_password_here"
MQTT_BROKER = "192.168.X.X"
MQTT_CLIENT_ID = "esp32_smart_box"
DEFAULT_CONFIG = {
    "t_max": 32.0,
    "t_min": 18.0,
    "h_max": 80.0,
    "h_min": 30.0
}