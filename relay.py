from machine import Pin
import time

print("--- 终极高阻抗切换测试 ---")

try:
    for i in range(5):
        print(f"[{i + 1}/5] 继电器：开启 (切换为 OUT 输出 0)")
        # 强行输出低电平，吸合
        relay_pin = Pin(4, Pin.OUT, value=0)
        time.sleep(1.5)

        print(f"[{i + 1}/5] 继电器：关闭 (切换为 IN 高阻抗)")
        # 不输出1了，直接把引脚变成输入模式，斩断输出电流
        relay_pin = Pin(4, Pin.IN)
        time.sleep(1.5)

    print("--- 测试结束 ---")

except KeyboardInterrupt:
    relay_pin = Pin(4, Pin.IN)
    print("安全退出")