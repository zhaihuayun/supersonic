# AIsonic 探鱼器 V1 — KiCad 原理图 + PCB

根据 [`原理图/原理图.png`](../原理图/原理图.png) 设计的两块板，KiCad 9 工程：

| 工程 | 板尺寸 | 内容 |
|------|--------|------|
| [`AIsonic_TX_Driver_V1/`](./AIsonic_TX_Driver_V1/) | 100 × 70 mm，2 层 | TC4427 → IRL540N → EE19 1:8 变压器 → LC 匹配 → TX 换能器 |
| [`AIsonic_RX_Frontend_V1/`](./AIsonic_RX_Frontend_V1/) | 90 × 55 mm，2 层 | 限幅保护 → OPA320 LNA → 200 kHz MFB 带通 → AD8338 AGC → ADC 偏置输出 |

每个工程包含：

- `*.kicad_sch` 原理图（KiCad 当前的原理图格式；KiCad 9 已不再保存旧版 `.sch`）
- `*.kicad_pcb` 已布局、布线、双面 GND 铺铜和缝合过孔的 PCB
- `*.kicad_pro`（含网络类：电源 / 高压 / 栅极线宽与间距）
- `AIsonic.kicad_sym` / `AIsonic.pretty`：工程内自带的符号（OPA320、AD8338、EE19）和 EE19 封装
- `output/`：
  - 原理图 PDF/SVG、BOM（含立创编号 LCSC 列）
  - Gerber+钻孔压缩包、贴片坐标
  - PCB 正反面预览图、ERC/DRC 报告

## 验证结果

| 项 | TX | RX |
|----|----|----|
| ERC（原理图电气规则） | 0 错误 / 0 警告 | 0 错误 / 0 警告 |
| 网表与设计数据比对 | 一致 | 一致 |
| DRC 违规 | 0 | 0 |
| 未连接 | 0 | 0 |
| 原理图 ↔ PCB 一致性 | 0 差异 | 0 差异 |

## 相对原理图 PNG 的修正

1. **RX 带通滤波器**：PNG 的 3.3k / 2.2nF 中心频率约 22 kHz，不是 200 kHz。改为多反馈（MFB）带通：
   - 元件值：R5 = 2.4k，R6 = 143Ω，R7 = 4.7k，C3 = C4 = 1nF C0G
   - 结果：f0 ≈ 200 kHz，Q ≈ 3
2. **AD8338 引脚按 ADI 数据手册（LFCSP-16）**：
   - 单端输入：INPR 交流耦合，INMR 交流接地。
   - MODE 接 VBAT，DETO 接地。
   - VAGC 接内部 1.5V VREF；OFSN 经 100nF 接 VREF。
   - 增益由 J3（AGC_CTRL，接 MCU DAC）经 RC 滤波控制。
   - 裸焊盘 EP 接 GND，并打 4 个热过孔。
3. **TC4427 两路并联**：INA 和 INB 相连；OUTA、OUTB 各串 10Ω 后汇到 Q1 栅极，提高驱动电流。
4. **T1 次级引脚**：次级用 pin 10 → L1 → C3 → TX+，pin 6 → TX-（同名端仍为 1、6）。这样做是为了让高压走线不交叉。

## 下单前需人工确认

- **EE19 变压器封装** `AIsonic:EE19_5+5_Vertical`：按 5+5 针、针距 3.81 mm、排距 15.24 mm 估算，务必对照实际骨架尺寸修改。
- **AD8338 封装**：按 3×3 mm LFCSP-16、EP 1.6 mm 设计，核对立创 C578701 的实物封装。EP 上的热过孔建议选塞孔工艺。
- **L1（约 300 µH）/ C3（2.2nF 1kV）** 需按实际 PZT 电容调谐。
- BOM 中阻容的立创编号只是常用料，下单前核库存。

## 导入嘉立创EDA专业版

嘉立创EDA专业版 → 文件 → 导入 → KiCad，选择工程目录（或 `.kicad_sch` + `.kicad_pcb`）即可。也可以直接把 `output/*_gerber.zip` 上传到嘉立创下单。

## 重新生成

设计数据（元件、网络、原理图坐标、PCB 摆放）集中在 `_gen/design_tx.py`、`_gen/design_rx.py`。修改后重新生成：

```bash
# 依赖：KiCad 9（kicad-cli + pcbnew Python）、Java 17+、Freerouting 2.1
export FREEROUTING_JAR=/path/to/freerouting-2.1.0.jar
cd kicad/_gen
python3 build_pcb.py design_tx && python3 export.py design_tx
python3 build_pcb.py design_rx && python3 export.py design_rx
```

`build_pcb.py` 的执行步骤：

1. 生成原理图并跑 ERC，再比对网表。
2. 摆放元件，用 Freerouting 自动布线（结果不确定，最多重试 4 次）。
3. 铺铜、打缝合过孔，然后清理孤立过孔和悬空短线。
4. 最后运行 DRC（含原理图一致性检查）。

`--no-route` 只生成和摆放，不布线。
