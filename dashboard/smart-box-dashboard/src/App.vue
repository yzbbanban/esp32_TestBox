<script setup>
import { ref, onMounted } from 'vue'

// 定义响应式数据
const temperature = ref('--')
const humidity = ref('--')
const connectionStatus = ref('正在连接 WebSocket...')
const isConnected = ref(false)

onMounted(() => {
  // 连接 Python 提供的 WebSocket 桥接服务
  const ws = new WebSocket('ws://localhost:8765')

  ws.onopen = () => {
    connectionStatus.value = '已连接到物联网数据中心'
    isConnected.value = true
    console.log('WebSocket 连接成功')
  }

  ws.onmessage = (event) => {
    try {
      // 解析来自 ESP32 通过 MQTT 转发过来的 JSON 数据
      const data = JSON.parse(event.data)
      temperature.value = data.temperature
      humidity.value = data.humidity
    } catch (e) {
      console.error('解析 JSON 失败:', e)
    }
  }

  ws.onclose = () => {
    connectionStatus.value = '连接已断开，请检查 Python 后端'
    isConnected.value = false
    console.log('WebSocket 连接关闭')
  }

  ws.onerror = (error) => {
    connectionStatus.value = '连接发生错误'
    isConnected.value = false
    console.error('WebSocket 错误:', error)
  }
})
</script>

template
<template>
  <div class="dashboard-container">
    <div class="card">
      <h2>🌱 智能微型测试箱监控大屏</h2>

      <!-- 连接状态提示 -->
      <div class="status-bar" :class="{ 'connected': isConnected, 'disconnected': !isConnected }">
        {{ connectionStatus }}
      </div>

      <!-- 数据展示区域 -->
      <div class="data-grid">
        <div class="data-box">
          <span class="label">实时温度</span>
          <span class="value">{{ temperature }} <small>℃</small></span>
        </div>

        <div class="data-box">
          <span class="label">实时湿度</span>
          <span class="value">{{ humidity }} <small>%</small></span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  font-family: Arial, sans-serif;
  background-color: #f4f4f9;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0;
}

.card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  width: 400px;
  text-align: center;
}

h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 20px;
}

.status-bar {
  font-size: 14px;
  padding: 8px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-weight: bold;
}

.status-bar.connected {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-bar.disconnected {
  background-color: #ffebee;
  color: #c62828;
}

.data-grid {
  display: flex;
  justify-content: space-around;
  gap: 15px;
}

.data-box {
  background: #f9f9fb;
  flex: 1;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.label {
  display: block;
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.value {
  font-size: 26px;
  font-weight: bold;
  color: #2c3e50;
}

.value small {
  font-size: 14px;
  font-weight: normal;
  color: #888;
}
</style>