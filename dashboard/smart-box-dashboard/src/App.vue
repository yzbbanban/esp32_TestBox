<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const temperature = ref('--')
const humidity = ref('--')
const connectionStatus = ref('正在连接 WebSocket...')
const isConnected = ref(false)

let myChart = null
// 保存折线图的历史数据
const timeList = []
const tempDataList = []
const humDataList = []

onMounted(() => {
  // 1. 初始化 ECharts 折线图
  const chartDom = document.getElementById('main-chart')
  myChart = echarts.init(chartDom)

  const option = {
    title: {
      text: '环境温湿度实时曲线',
      left: 'center',
      textStyle: { fontSize: 14 },
      top: 10  // 1. 让标题靠顶部更近一点
    },
    tooltip: { trigger: 'axis' },
    legend: {
      data: ['温度 (℃)', '湿度 (%)'],
      top: 35  // 2. 将图例往下移一点，避开标题
    },
    xAxis: { type: 'category', boundaryGap: false, data: timeList },
    yAxis: { type: 'value' },
    series: [
      { name: '温度 (℃)', type: 'line', data: tempDataList, smooth: true, itemStyle: { color: '#ff7675' } },
      { name: '湿度 (%)', type: 'line', data: humDataList, smooth: true, itemStyle: { color: '#74b9ff' } }
    ],
    grid: { left: '10%', right: '10%', bottom: '15%', top: '25%' } // 3. 适当增大顶部留白 (top)
  }
  myChart.setOption(option)

  // 2. 建立 WebSocket 连接
  const ws = new WebSocket('ws://localhost:8765')

  ws.onopen = () => {
    connectionStatus.value = '已连接到物联网数据中心'
    isConnected.value = true
  }

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      temperature.value = data.temperature
      humidity.value = data.humidity

      // 获取当前格式化时间 (HH:mm:ss)
      const now = new Date().toLocaleTimeString()

      // 限制最多显示最近 20 个数据点，避免折线无限拉长
      if (timeList.length >= 20) {
        timeList.shift()
        tempDataList.shift()
        humDataList.shift()
      }

      timeList.push(now)
      tempDataList.push(data.temperature)
      humDataList.push(data.humidity)

      // 刷新 ECharts 图表
      myChart.setOption({
        xAxis: { data: timeList },
        series: [
          { data: tempDataList },
          { data: humDataList }
        ]
      })
    } catch (e) {
      console.error('解析 JSON 失败:', e)
    }
  }

  ws.onclose = () => {
    connectionStatus.value = '连接已断开'
    isConnected.value = false
  }
})
</script>

<template>
  <div class="dashboard-container">
    <div class="card">
      <h2>🌱 智能微型测试箱监控大屏</h2>

      <div class="status-bar" :class="{ 'connected': isConnected, 'disconnected': !isConnected }">
        {{ connectionStatus }}
      </div>

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

      <!-- ECharts 图表挂载容器 -->
      <div id="main-chart" style="width: 100%; height: 280px; margin-top: 20px;"></div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  font-family: Arial, sans-serif;
  background-color: #f4f4f9;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0;
  padding: 20px;
}

.card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  width: 550px;
  text-align: center;
}

h2 {
  color: #333;
  margin-bottom: 15px;
  font-size: 20px;
}

.status-bar {
  font-size: 13px;
  padding: 6px;
  border-radius: 6px;
  margin-bottom: 15px;
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
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.value small {
  font-size: 14px;
  font-weight: normal;
  color: #888;
}
</style>