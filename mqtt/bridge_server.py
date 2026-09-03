import asyncio
import json
import websockets
from gmqtt import Client as MQTTClient  # 或者用你现有的 mqtt 客户端逻辑

# 保存所有连接到大屏的浏览器客户端
connected_clients = set()

# WebSocket 广播核心函数
async def broadcast_data(message):
    if connected_clients:
        # 将收到的 MQTT 消息瞬间广播给所有打开的网页大屏
        await asyncio.gather(*[client.send(message) for client in connected_clients])

async def ws_handler(websocket, path):
    connected_clients.add(websocket)
    print(f"[{websocket.remote_address}] 前端大屏已连接")
    try:
        async for message in websocket:
            pass
    except websockets.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)
        print("前端大屏已断开")

# 启动 WebSocket 服务监听 8765 端口
async def main():
    async with websockets.serve(ws_handler, "0.0.0.0", 8765):
        print("WebSocket 转发服务已启动: ws://localhost:8765")
        await asyncio.Future()  # 持续运行

if __name__ == "__main__":
    # 这里可以结合你现有的异步 MQTT 客户端一起放入事件循环
    asyncio.run(main())