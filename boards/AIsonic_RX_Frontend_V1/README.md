# AIsonic RX 超声波接收前端 V1.0

嘉立创EDA专业版工程（`.eprj3`）。对应方案文档里的 **RX 接收板**。

路径：`D:\vibecodeing\AIsonic\boards\AIsonic_RX_Frontend_V1\`

用客户端打开：双击 `AIsonic_RX_Frontend_V1.eprj3`，或：

```powershell
node "$env:USERPROFILE\.cursor\skills\easyeda-eprj3\scripts\open.js" open --dir "D:\vibecodeing\AIsonic\boards\AIsonic_RX_Frontend_V1"
```

重新生成（会覆盖本目录）：

```powershell
node "D:\vibecodeing\AIsonic\boards\_build_rx.js"
```

## 电路

```
200kHz RX PZT
    → J1 → Cin 100nF → Rser 100Ω → BAT54S 钳位
    → U2 OPA320 非反相 LNA（Rf=100k / Rg=10k ≈ 20 dB，偏置 VREF=1.65V）
    → Rbpf/Cbpf 二阶 RC（3.9k + 2.2nF，台上按 170~230 kHz 微调）
    → U3 AD8338 VGA（GAIN 由 MCU DAC 0.1~1.1V 控制）
    → Cadc 100nF + Radc 偏置到 1.65V → J2.ADC_OUT → STM32 PA0
```

- 供电：J2 **+3V3 / GND**（与 TX +12V 共地单点）
- VREF：Rbias1/Rbias2 10k 分压 1.65V，同时给 LNA 和 ADC 偏置
- AD8338：MODE=+3V3（增益随 GAIN 上升）；DETO/OFSN/INMR/EPAD=GND；VAGC 接芯片内部 1.5V；FBKP/FBKM/INPD/INMD/OUTM 悬空用内部默认

## 板框

双层 **90.0 × 55.0 mm**（3600 × 2200 mil）。原理图图框 **A2**（2340 × 1654）。顶/底层 GND 铺铜。输入在左、VGA 在中、MCU 接口在右；远离 TX 板 / DC-DC。

## 接口

| 连接器 | 封装 | 定义 |
|--------|------|------|
| J1 | KF2EDG-3.81-2P | 1 RX+、2 RX−/GND |
| J2 | KF2EDG-3.81-4P | 1 ADC_OUT、2 VREF 1.65V、3 +3V3、4 GND |
| J3 | KF2EDG-3.81-2P | 1 AGC_CTRL（PA4 DAC）、2 GND |

## 关键料（立创）

| 位号 | 型号 | LCSC |
|------|------|------|
| U2 | OPA320AIDBVT | C206063 |
| U3 | AD8338ACPZ-R7 | C578701 |
| D2 | BAT54S | C727126 |

完整配单见仓库 [`立创BOM_探鱼器V1.csv`](../../立创BOM_探鱼器V1.csv) 中 RX 相关行。

## 打开后建议人工检查

1. OPA320 SOT-23-5、AD8338 LFCSP-16 焊盘与 datasheet 核对（含 EPAD 接地）
2. BAT54S：COM 接信号，A1 接 GND，C2 接 3V3
3. BPF 元件值按实测 PZT 阻抗重算
4. DRC / 模拟地分割是否需要（V1 先整板 GND 铺铜）

本工程是可打开的 V1 骨架，不是最终生产 Gerber。出板前务必在嘉立创EDA里核对封装与间隙。
