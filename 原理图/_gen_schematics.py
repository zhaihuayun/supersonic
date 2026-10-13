# -*- coding: utf-8 -*-
from pathlib import Path

OUT = Path(__file__).resolve().parent


def svg_wrap(w, h, body):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <style>
      .bg {{ fill: #f7f8fa; }}
      .title {{ font: 700 22px 'Segoe UI', 'Microsoft YaHei', sans-serif; fill: #1a1a1a; }}
      .sub {{ font: 400 13px 'Segoe UI', 'Microsoft YaHei', sans-serif; fill: #555; }}
      .lbl {{ font: 600 12px 'Segoe UI', 'Microsoft YaHei', sans-serif; fill: #222; }}
      .sm {{ font: 400 11px Consolas, 'Microsoft YaHei', monospace; fill: #333; }}
      .note {{ font: 400 11px 'Segoe UI', 'Microsoft YaHei', sans-serif; fill: #666; }}
      .box {{ fill: #fff; stroke: #2c3e50; stroke-width: 1.5; }}
      .box-tx {{ fill: #fff5eb; stroke: #c05621; stroke-width: 1.8; }}
      .box-rx {{ fill: #ebf8ff; stroke: #2b6cb0; stroke-width: 1.8; }}
      .box-mcu {{ fill: #f0fff4; stroke: #276749; stroke-width: 1.8; }}
      .wire {{ stroke: #2d3748; stroke-width: 1.6; fill: none; }}
      .wire-pwr {{ stroke: #c53030; stroke-width: 1.8; fill: none; }}
      .wire-sig {{ stroke: #2b6cb0; stroke-width: 1.6; fill: none; }}
      .comp {{ fill: #fff; stroke: #1a202c; stroke-width: 1.5; }}
      .pin {{ fill: #edf2f7; stroke: #4a5568; stroke-width: 1; }}
    </style>
  </defs>
  <rect class="bg" width="{w}" height="{h}"/>
  {body}
</svg>
"""


def main():
    # 1. System
    body = """
  <text class="title" x="40" y="40">AI 超声波探鱼器 V1.0 — 系统原理框图</text>
  <text class="sub" x="40" y="62">STM32H750 + TX/RX 分离 + 双 200kHz PZT</text>

  <rect class="box" x="420" y="90" width="160" height="50" rx="6"/>
  <text class="lbl" x="448" y="120">手机 APP / PC</text>

  <line class="wire-sig" x1="500" y1="140" x2="500" y2="175"/>
  <text class="sm" x="510" y="165">BLE / WiFi</text>

  <rect class="box-mcu" x="360" y="175" width="280" height="90" rx="8"/>
  <text class="lbl" x="430" y="210">STM32H750</text>
  <text class="sm" x="390" y="232">TIM1 CH1 (PA8) PWM 200kHz</text>
  <text class="sm" x="390" y="250">ADC1 (PA0) · DAC/PWM AGC</text>

  <line class="wire" x1="420" y1="265" x2="220" y2="300"/>
  <rect class="box-tx" x="80" y="300" width="220" height="130" rx="8"/>
  <text class="lbl" x="130" y="328">TX 发射驱动板</text>
  <text class="sm" x="100" y="350">TC4427 → MOSFET</text>
  <text class="sm" x="100" y="368">升压变压器 1:8</text>
  <text class="sm" x="100" y="386">LC 匹配 ~300uH</text>
  <text class="sm" x="100" y="404">输出 80~150 Vpp Burst</text>
  <text class="sm" x="100" y="420">J2: +12V / GND</text>

  <line class="wire" x1="580" y1="265" x2="780" y2="300"/>
  <rect class="box-rx" x="700" y="300" width="240" height="130" rx="8"/>
  <text class="lbl" x="755" y="328">RX 接收前端板</text>
  <text class="sm" x="720" y="350">保护 BAT54S</text>
  <text class="sm" x="720" y="368">LNA OPA320 20dB</text>
  <text class="sm" x="720" y="386">BPF 170~230kHz</text>
  <text class="sm" x="720" y="404">AGC AD8338 20~70dB</text>
  <text class="sm" x="720" y="420">→ ADC 0~3.3V @1.65V偏置</text>

  <line class="wire" x1="190" y1="430" x2="190" y2="470"/>
  <line class="wire" x1="820" y1="430" x2="820" y2="470"/>
  <rect class="box" x="100" y="470" width="180" height="55" rx="6"/>
  <text class="lbl" x="125" y="502">TX 200kHz PZT</text>
  <rect class="box" x="730" y="470" width="180" height="55" rx="6"/>
  <text class="lbl" x="755" y="502">RX 200kHz PZT</text>

  <line class="wire" x1="190" y1="525" x2="190" y2="560"/>
  <line class="wire" x1="820" y1="525" x2="820" y2="560"/>
  <line class="wire" x1="190" y1="560" x2="820" y2="560"/>
  <rect class="box" x="320" y="545" width="360" height="70" rx="8" fill="#e6fffa" stroke="#319795"/>
  <text class="lbl" x="430" y="575">水体传播 / 鱼·水底反射</text>
  <text class="sm" x="400" y="595">声速 ≈ 1500 m/s · 测距 d=c·t/2</text>

  <text class="note" x="40" y="660">文件：01_系统框图.svg · V1 实验机基线 · TX/RX 分板布线，高压远离 ADC</text>
"""
    (OUT / "01_系统框图.svg").write_text(svg_wrap(1020, 690, body), encoding="utf-8")

    # 2. TX
    body = """
  <text class="title" x="30" y="36">TX 发射驱动板原理图 · V1.0</text>
  <text class="sub" x="30" y="56">STM32H750 PA8 → TC4427 → MOSFET → EE19 变压器 → LC → 200kHz PZT</text>

  <rect class="pin" x="30" y="110" width="70" height="70" rx="4"/>
  <text class="lbl" x="48" y="135">J1</text>
  <text class="sm" x="40" y="155">1 PWM</text>
  <text class="sm" x="40" y="170">2 GND</text>

  <line class="wire-sig" x1="100" y1="140" x2="160" y2="140"/>
  <text class="sm" x="110" y="130">PA8</text>

  <rect class="comp" x="160" y="90" width="140" height="110" rx="4"/>
  <text class="lbl" x="195" y="115">U1 TC4427</text>
  <text class="sm" x="175" y="140">IN ← PWM</text>
  <text class="sm" x="175" y="158">VDD = +12V</text>
  <text class="sm" x="175" y="176">OUT → Gate</text>
  <text class="sm" x="175" y="192">GND</text>
  <text class="sm" x="160" y="220">C1 100nF · C2 10uF @ VDD</text>

  <line class="wire" x1="300" y1="150" x2="360" y2="150"/>
  <text class="sm" x="310" y="140">Rg 10Ω</text>

  <rect class="comp" x="360" y="90" width="130" height="120" rx="4"/>
  <text class="lbl" x="385" y="115">Q1 IRL540</text>
  <text class="sm" x="375" y="140">G ← Rg</text>
  <text class="sm" x="375" y="158">S → GND</text>
  <text class="sm" x="375" y="176">D → XFMR</text>
  <text class="sm" x="375" y="194">Rgs 10k G-S</text>

  <line class="wire" x1="425" y1="210" x2="425" y2="250"/>
  <rect class="comp" x="385" y="250" width="80" height="40" rx="3"/>
  <text class="sm" x="395" y="275">D1 SMBJ100A</text>
  <line class="wire" x1="425" y1="290" x2="425" y2="320"/>
  <text class="sm" x="435" y="315">GND</text>

  <line class="wire-pwr" x1="490" y1="130" x2="540" y2="130"/>
  <rect class="comp" x="540" y="80" width="150" height="140" rx="4"/>
  <text class="lbl" x="565" y="105">T1 EE19</text>
  <text class="sm" x="555" y="128">初级 ~10T</text>
  <text class="sm" x="555" y="146">次级 ~80T</text>
  <text class="sm" x="555" y="164">匝比 ≈ 1:8</text>
  <text class="sm" x="555" y="182">Pri+ ← +12V</text>
  <text class="sm" x="555" y="200">Pri- ← Drain</text>

  <rect class="pin" x="540" y="20" width="90" height="45" rx="4"/>
  <text class="lbl" x="558" y="40">J2 +12V</text>
  <text class="sm" x="558" y="55">1:+12 2:GND</text>
  <line class="wire-pwr" x1="585" y1="65" x2="585" y2="80"/>

  <line class="wire" x1="690" y1="130" x2="740" y2="130"/>
  <rect class="comp" x="740" y="90" width="120" height="100" rx="4"/>
  <text class="lbl" x="770" y="115">LC 匹配</text>
  <text class="sm" x="755" y="140">L1 ≈ 300uH</text>
  <text class="sm" x="755" y="158">Cmatch 2nF HV</text>
  <text class="sm" x="755" y="176">fres≈200kHz</text>

  <line class="wire" x1="860" y1="130" x2="910" y2="130"/>
  <rect class="comp" x="910" y="95" width="120" height="90" rx="4"/>
  <text class="lbl" x="925" y="125">TX PZT</text>
  <text class="sm" x="925" y="145">200kHz</text>
  <text class="sm" x="925" y="163">J3 TX+/TX-</text>

  <rect class="box-tx" x="30" y="360" width="480" height="150" rx="6"/>
  <text class="lbl" x="50" y="388">Burst 时序（禁止连续发射）</text>
  <text class="sm" x="50" y="415">1) TIM1 PWM 200kHz 50% · 20周期 ≈ 100us</text>
  <text class="sm" x="50" y="435">2) 停止 PWM · 等待振铃 300us（盲区）</text>
  <text class="sm" x="50" y="455">3) 启动 RX ADC DMA 采样</text>
  <text class="sm" x="50" y="475">V1 目标输出：约 80 Vpp · 水桶/鱼缸验证</text>
  <text class="sm" x="50" y="495">功率回路：MOS-变压器-去耦电容 最短；高压远离 MCU/ADC</text>

  <rect class="box" x="540" y="360" width="490" height="150" rx="6"/>
  <text class="lbl" x="560" y="388">网表摘要</text>
  <text class="sm" x="560" y="412">NET_PWM: J1.1 — U1.IN</text>
  <text class="sm" x="560" y="430">NET_GATE: U1.OUT — Rg — Q1.G ; Rgs→GND</text>
  <text class="sm" x="560" y="448">NET_DRAIN: Q1.D — T1.Pri- — D1.A ; D1.K→GND</text>
  <text class="sm" x="560" y="466">NET_12V: J2.1 — U1.VDD — T1.Pri+</text>
  <text class="sm" x="560" y="484">NET_TX: T1.Sec — L1 — Cmatch — J3.TX+/TX-</text>
  <text class="sm" x="560" y="502">GND: J1.2 J2.2 Q1.S U1.GND 单点回流</text>
"""
    (OUT / "02_TX发射板原理图.svg").write_text(svg_wrap(1080, 540, body), encoding="utf-8")

    # 3. RX
    body = """
  <text class="title" x="30" y="36">RX 接收前端板原理图 · V1.0</text>
  <text class="sub" x="30" y="56">保护 → LNA(OPA320) → BPF 200kHz → AGC(AD8338) → ADC偏置 → STM32H750 PA0</text>

  <rect class="pin" x="20" y="120" width="80" height="70" rx="4"/>
  <text class="lbl" x="42" y="145">J1</text>
  <text class="sm" x="30" y="165">1 RX+</text>
  <text class="sm" x="30" y="180">2 RX-</text>

  <line class="wire-sig" x1="100" y1="145" x2="150" y2="145"/>

  <rect class="comp" x="150" y="95" width="140" height="120" rx="4"/>
  <text class="lbl" x="175" y="120">输入保护</text>
  <text class="sm" x="165" y="142">Cin 100nF 隔直</text>
  <text class="sm" x="165" y="160">Rser 100Ω</text>
  <text class="sm" x="165" y="178">D2 BAT54S</text>
  <text class="sm" x="165" y="196">双向限幅→GND</text>

  <line class="wire-sig" x1="290" y1="145" x2="340" y2="145"/>

  <rect class="comp" x="340" y="85" width="160" height="140" rx="4"/>
  <text class="lbl" x="380" y="110">U1 OPA320</text>
  <text class="sm" x="355" y="132">非反相放大</text>
  <text class="sm" x="355" y="150">Rf=100k Rg=10k</text>
  <text class="sm" x="355" y="168">G≈11 (~20dB)</text>
  <text class="sm" x="355" y="186">V+=3.3V</text>
  <text class="sm" x="355" y="204">偏置 VREF 1.65V</text>

  <line class="wire-sig" x1="500" y1="145" x2="550" y2="145"/>

  <rect class="comp" x="550" y="95" width="150" height="120" rx="4"/>
  <text class="lbl" x="580" y="120">200kHz BPF</text>
  <text class="sm" x="565" y="145">二阶有源带通</text>
  <text class="sm" x="565" y="163">170~230 kHz</text>
  <text class="sm" x="565" y="181">R 3.3k~5.1k</text>
  <text class="sm" x="565" y="199">C ≈ 2.2nF</text>

  <line class="wire-sig" x1="700" y1="145" x2="750" y2="145"/>

  <rect class="comp" x="750" y="85" width="150" height="140" rx="4"/>
  <text class="lbl" x="780" y="110">U2 AD8338</text>
  <text class="sm" x="765" y="132">VGA 0~80dB</text>
  <text class="sm" x="765" y="150">工作 20~70dB</text>
  <text class="sm" x="765" y="168">初值 ~40dB</text>
  <text class="sm" x="765" y="186">GAIN←DAC/PWM</text>
  <text class="sm" x="765" y="204">J3 AGC_CTRL</text>

  <line class="wire-sig" x1="900" y1="145" x2="940" y2="145"/>

  <rect class="comp" x="940" y="95" width="150" height="120" rx="4"/>
  <text class="lbl" x="960" y="120">ADC 驱动</text>
  <text class="sm" x="955" y="145">隔直 + 偏置</text>
  <text class="sm" x="955" y="163">中点 1.65V</text>
  <text class="sm" x="955" y="181">输出 0~3.3V</text>
  <text class="sm" x="955" y="199">→ PA0 ADC1</text>

  <rect class="box-rx" x="340" y="250" width="280" height="90" rx="6"/>
  <text class="lbl" x="360" y="275">VREF = 1.65V</text>
  <text class="sm" x="360" y="295">3.3V — 10k — VREF — 10k — GND</text>
  <text class="sm" x="360" y="313">或 TLV431 精密基准 · 供 LNA/ADC 偏置</text>
  <text class="sm" x="360" y="331">交流信号绕 1.65V 摆动</text>

  <rect class="pin" x="650" y="250" width="200" height="90" rx="4"/>
  <text class="lbl" x="670" y="275">J2 → STM32</text>
  <text class="sm" x="670" y="295">1 ADC_OUT (PA0)</text>
  <text class="sm" x="670" y="312">2 VREF · 3 3V3 · 4 GND</text>
  <text class="sm" x="670" y="329">J3: AGC_CTRL / GND</text>

  <rect class="box" x="20" y="370" width="1070" height="120" rx="6"/>
  <text class="lbl" x="40" y="398">设计要点</text>
  <text class="sm" x="40" y="422">· TX 发射时 RX 输入可能泄漏数十 V → 保护二极管必须；发射后等 300us 再采样</text>
  <text class="sm" x="40" y="442">· 增益勿一级拉满；LNA≈20dB + BPF + AGC 可调，总增益约 60dB 量级</text>
  <text class="sm" x="40" y="462">· ADC：2MSPS / DMA 2048 点；采样前去直流 → FFT → 峰值测深</text>
  <text class="sm" x="40" y="482">· PCB：RX 输入远离 TX板 / DC-DC / 蓝牙；磁珠隔离数字与模拟地</text>
"""
    (OUT / "03_RX接收板原理图.svg").write_text(svg_wrap(1120, 520, body), encoding="utf-8")

    # 4. MCU
    body = """
  <text class="title" x="30" y="36">主控互联原理图 · STM32H750</text>
  <text class="sub" x="30" y="56">与 TX / RX 板接口、电源与调试口</text>

  <rect class="box-mcu" x="360" y="100" width="280" height="280" rx="10"/>
  <text class="lbl" x="430" y="140">STM32H750</text>
  <text class="sm" x="390" y="170">PA8  TIM1_CH1 → TX PWM</text>
  <text class="sm" x="390" y="192">PA0  ADC1_IN  ← RX ADC_OUT</text>
  <text class="sm" x="390" y="214">PA4  DAC1 / PWM → AGC_CTRL</text>
  <text class="sm" x="390" y="236">USART / USB → PC 调试</text>
  <text class="sm" x="390" y="258">SPI/SDIO 可选存储</text>
  <text class="sm" x="390" y="280">3V3 / GND</text>
  <text class="sm" x="390" y="302">SWD：SWDIO / SWCLK</text>
  <text class="sm" x="390" y="330">时钟：HSE 可选外晶振</text>
  <text class="sm" x="390" y="352">供电：3V3 LDO ← 5V/12V</text>

  <rect class="box-tx" x="40" y="140" width="220" height="160" rx="8"/>
  <text class="lbl" x="90" y="170">TX 板</text>
  <text class="sm" x="60" y="200">J1.PWM ← PA8</text>
  <text class="sm" x="60" y="220">J1.GND</text>
  <text class="sm" x="60" y="240">J2 +12V 独立功率地</text>
  <text class="sm" x="60" y="260">J3 → TX PZT</text>
  <text class="sm" x="60" y="280">Burst 由固件控制</text>

  <rect class="box-rx" x="740" y="140" width="220" height="160" rx="8"/>
  <text class="lbl" x="800" y="170">RX 板</text>
  <text class="sm" x="760" y="200">ADC_OUT → PA0</text>
  <text class="sm" x="760" y="220">AGC_CTRL ← PA4</text>
  <text class="sm" x="760" y="240">3V3 / VREF / GND</text>
  <text class="sm" x="760" y="260">J1 ← RX PZT</text>
  <text class="sm" x="760" y="280">模拟地就近单点</text>

  <line class="wire" x1="260" y1="200" x2="360" y2="200"/>
  <line class="wire" x1="640" y1="200" x2="740" y2="200"/>

  <rect class="box" x="40" y="360" width="920" height="100" rx="6"/>
  <text class="lbl" x="60" y="390">电源建议</text>
  <text class="sm" x="60" y="415">12V（TX 功率）与 3.3V（MCU/RX）分开供电路径；共地单点连接，避免大电流经模拟地回流</text>
  <text class="sm" x="60" y="435">TX 发射瞬间电流大：12V 侧就近大电解 + 陶瓷；MCU 侧磁珠隔离</text>
  <text class="sm" x="60" y="455">第一版成功标准：水桶测深 ~0.8m → 水池 ~3m → 再湖泊/鱼目标</text>
"""
    (OUT / "04_主控互联原理图.svg").write_text(svg_wrap(1000, 490, body), encoding="utf-8")

    print("OK", [p.name for p in sorted(OUT.glob("*.svg"))])


if __name__ == "__main__":
    main()
