import asyncio
import json
import websockets
from gmqtt import Client as MQTTClient
import time

# 存储所有连接到 Vue3 大屏的浏览器客户端
connected_clients = set()


# 1. 处理来自前端 WebSocket 的连接
async def ws_handler(websocket):
    connected_clients.add(websocket)
    print(f"[WebSocket] 新的前端大屏已连接: {websocket.remote_address}")
    try:
        async for message in websocket:
            # 如果前端有发消息过来可以按需处理，这里主要用于保持连接
            pass
    except websockets.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)
        print("[WebSocket] 前端大屏已断开连接")


# 2. 广播数据给所有网页大屏
async def broadcast_to_frontend(payload_str):
    if connected_clients:
        # 并发向所有连接的浏览器发送 JSON 数据
        await asyncio.gather(*[client.send(payload_str) for client in connected_clients])


# 3. 接收到 ESP32 的 MQTT 消息时的回调
def on_message(client, topic, payload, qos, properties):
    try:
        message_str = payload.decode('utf-8')
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')}[MQTT 收到] 话题: {topic} | 内容: {message_str}")

        # 将 MQTT 收到的数据放入 asyncio 事件循环，异步广播给网页
        asyncio.run_coroutine_threadsafe(
            broadcast_to_frontend(message_str),
            loop
        )
    except Exception as e:
        print("解析 MQTT 消息异常:", e)


def on_connect(client, flags, rc, properties):
    print("[MQTT] 成功连接到 Broker，开始订阅话题...")
    client.subscribe('testbox/data', qos=0)


# 4. 主异步入口
async def main():
    global loop
    loop = asyncio.get_running_loop()

    # 初始化 MQTT 客户端
    mqtt_client = MQTTClient("mac_bridge_server")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # 连接到本地运行的 MQTT Broker (或本机的 Mosquitto 服务)
    # 如果你用的是 Python 自建的 Broker，请确保其地址正确
    await mqtt_client.connect('127.0.0.1', port=1883)

    # 启动 WebSocket 服务，监听 8765 端口
    async with websockets.serve(ws_handler, "0.0.0.0", 8765):
        print("[服务就绪] WebSocket 桥接服务已启动: ws://localhost:8765")
        # 保持主程序持续运行
        await asyncio.Future()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("服务已手动停止。")