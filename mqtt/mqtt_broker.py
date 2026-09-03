import asyncio
import logging
from amqtt.broker import Broker

# 1. 核心配置字典：监听局域网 1883 端口，允许匿名设备连接
config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '0.0.0.0:1883',
        }
    },
    'sys_interval': 10,
    'auth': {
        'allow-anonymous': True,
        'password-file': None
    },
    'topic-check': {
        'enabled': False
    }
}


async def start_broker():
    # 初始化 Broker 实例
    broker = Broker(config)
    await broker.start()
    print("🚀 Python 定制版 MQTT 服务器已启动！监听端口 1883...")

    # 挂起主协程，让服务器保持后台运行
    while True:
        await asyncio.sleep(99999)


if __name__ == '__main__':
    # 开启日志，这样 ESP32 连上来或者掉线，终端里一清二楚
    formatter = "[%(asctime)s] :: %(levelname)s :: %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)

    try:
        asyncio.run(start_broker())
    except KeyboardInterrupt:
        print("\nMQTT 服务器已手动关闭")