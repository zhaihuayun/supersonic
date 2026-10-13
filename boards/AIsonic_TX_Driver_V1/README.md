# AIsonic TX 超声波驱动板 V1.0

嘉立创EDA专业版工程（`.eprj3`）。对应方案文档里的 **TX 发射驱动板**。

路径：`D:\vibecodeing\AIsonic\boards\AIsonic_TX_Driver_V1\`

用客户端打开：双击 `AIsonic_TX_Driver_V1.eprj3`，或：

```powershell
node "$env:USERPROFILE\.cursor\skills\easyeda-eprj3\scripts\open.js" open --dir "D:\vibecodeing\AIsonic\boards\AIsonic_TX_Driver_V1"
```

重新生成（会覆盖本目录）：

```powershell
node "D:\vibecodeing\AIsonic\boards\_build_tx.js"
```

## 电路

```
STM32 PA8 PWM 200kHz
    → J1 → U1 TC4427 (INA)
    → Rg 10Ω → Q1 IRL540 Gate
    → Drain → T1 EE19 初级(1:8) → 次级
    → L1 330µH → Cmatch 2nF HV → J3 TX+/TX- → 200kHz PZT
```

- 供电：J2 **+12V / GND**（仅 TX 功率，与 MCU 3.3V 共地单点）
- 保护：Drain→GND **SMBJ100A**（阴极接 Drain，阳极接 GND）
- 未用 INB 已接地；Rgs=10k 下拉 Gate
- Burst：20 周期 / 100µs，禁止连续发射；发射后等 300µs 再开 RX ADC

## 板框

双层 **100.0 × 70.0 mm**（4000 × 2800 mil）。原理图图框 **A2**（2340 × 1654），避免链路画出图框。顶/底层 GND 铺铜。功率回路：Q1–变压器–12V 去耦尽量短；右侧为高压 LC / 换能器区。

## 接口

| 连接器 | 封装 | 定义 |
|--------|------|------|
| J1 | KF2EDG-3.81-2P | 1 PWM（PA8）、2 GND |
| J2 | KF2EDG-5.08-2P | 1 +12V、2 GND |
| J3 | KF2EDG-5.08-2P | 1 TX+、2 TX- |

## 关键料（立创）

| 位号 | 型号 | LCSC |
|------|------|------|
| U1 | TC4427AEOA713 | C20551 |
| Q1 | IRL540NPBF-VB | C5240567 |
| D1 | SMBJ100A | C151249 |
| T1 | EE19 1:8（10T/80T） | 外购绕制 |
| L1 | ~330µH | 按 PZT 电容微调 220~330µH |
| Cmatch | 2nF ≥1kV | 高压瓷片/MLCC |

完整配单见仓库 [`立创BOM_探鱼器V1.csv`](../../立创BOM_探鱼器V1.csv) 中 TX 相关行。

## 打开后建议人工检查

1. 封装库 discretes（TO-220 孔距、EE19 骨架、接线端子）按实物微调  
2. DRC / 电气规则，高压间隙  
3. Q1 散热：可贴片或加小散热器  
4. 变压器同名端、初级/次级不要接反  
5. 图框：打开后确认图页尺寸为 A2；若仍显示 A4，在图框属性里把 Size 改成 A2（Width 2340 / Height 1654）

本工程是可打开的 V1 骨架，不是最终生产 Gerber。出板前务必在嘉立创EDA里核对封装与间隙。
