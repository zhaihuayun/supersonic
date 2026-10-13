"""AIsonic RX front-end: protection -> OPA320 LNA -> 200 kHz MFB band-pass -> AD8338 VGA -> ADC bias."""
from schgen import Comp, Schematic

PROJECT = 'AIsonic_RX_Frontend_V1'
BOARD = (90.0, 55.0)

R0805 = 'Resistor_SMD:R_0805_2012Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
TB2 = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1-2-3.81_1x02_P3.81mm_Horizontal'
TB4 = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1-4-3.81_1x04_P3.81mm_Horizontal'
HOLE = 'MountingHole:MountingHole_3.2mm_M3'
OPA_FIELDS = {'LCSC': 'C206063', 'MPN': 'OPA320AIDBVT'}

NETCLASSES = {
    'Power': dict(width=0.3, clearance=0.2, nets=['+3V3', 'GND']),
}

PLACE = {
    'J1': (4.5, 26.0, 270),
    'D1': (10.5, 22.0, 180), 'C1': (12.5, 26.0, 0), 'R1': (17.0, 26.0, 0),
    'D2': (21.0, 31.0, 0), 'R2': (22.0, 21.5, 90),
    'U1': (27.0, 26.0, 0), 'C2': (27.0, 21.0, 0), 'R3': (27.0, 31.0, 0), 'R4': (31.0, 31.0, 90),
    'R5': (34.0, 25.0, 0), 'R6': (37.0, 30.5, 90), 'C4': (39.5, 25.0, 0), 'C3': (41.5, 20.0, 0),
    'U2': (45.5, 26.0, 0), 'C5': (45.5, 21.0, 0), 'R7': (45.5, 31.0, 0),
    'C6': (52.0, 26.0, 0), 'C7': (53.0, 31.5, 90),
    'U3': (60.0, 28.0, 0), 'C10': (58.5, 23.0, 0), 'C11': (61.5, 19.5, 0),
    'C12': (55.5, 24.0, 90), 'C9': (64.0, 23.5, 90),
    'R8': (59.0, 36.5, 90), 'C13': (62.5, 35.5, 90), 'J3': (57.0, 50.0, 0),
    'C14': (67.0, 28.0, 0), 'R9': (70.5, 31.5, 90),
    'J2': (85.5, 30.0, 90), 'J4': (85.5, 43.0, 90), 'C17': (79.0, 41.0, 90),
    'R10': (12.0, 41.0, 90), 'R11': (15.0, 41.0, 90), 'C15': (19.0, 41.0, 90), 'C16': (22.0, 41.0, 90),
    'H1': (4.0, 4.0, 0), 'H2': (86.0, 4.0, 0), 'H3': (4.0, 51.0, 0), 'H4': (86.0, 51.0, 0),
}

# AD8338 exposed pad: 2x2 thermal vias to the bottom GND plane (plug/tent at fab)
EXTRA_VIAS = [(60.0 + dx, 28.0 + dy, 0.6, 0.3) for dx in (-0.45, 0.45) for dy in (-0.45, 0.45)]
# COMM (pad 5) and DETO (pad 8) tied straight into the EP; x offsets keep 0.2mm to pads 4/6 and 7/9.
EXTRA_TRACKS = [('GND', 0.2, [(59.31, 29.4375), (59.31, 28.6)]),
                ('GND', 0.2, [(60.69, 29.4375), (60.69, 28.6)])]

REF_AT = {'R11': (15.0, 44.6, 0), 'R10': (12.0, 44.6, 0), 'C16': (22.0, 44.6, 0), 'C15': (19.0, 44.6, 0),
          'J3': (52.0, 47.0, 0)}
STITCH_PITCH = 2.5

SILK = [
    (45.0, 3.5, 'AIsonic RX Frontend V1.0  200kHz', 1.4),
    (6.0, 17.0, '1:RX+ 2:GND', 0.9),
    (74.0, 13.5, '1:ADC 2:VREF 3:3V3 4:GND', 0.9),
    (76.0, 47.5, '1:3V3 2:GND', 0.9),
    (60.5, 45.0, '1:AGC 2:GND', 0.9),
    (17.0, 46.0, 'VREF 1.65V', 0.9),
]


def build():
    s = Schematic(PROJECT, 'AIsonic RX 接收前端板（200kHz）', paper='A3', comments=(
        '按 原理图/原理图.png RX接收板 设计；BPF 按 200kHz 重新计算（原图 3.3k/2.2nF ≈ 22kHz）',
        'AD8338 引脚按 ADI 数据手册 CP-16-22；单端输入：INPR 交流耦合，INMR 交流接地',
        '+3V3 由 MCU 板提供，与 TX +12V 单点共地'))
    A = s.add
    # ---- input protection ----
    A(Comp('J1', 'Connector_Generic:Conn_01x02', 'RX_PZT', TB2, (8, 30), mirror=True,
           nets={'1': 'RX_IN', '2': 'GND'}, fields={'Function': '1 RX+ / 2 RX-(GND)'}, ref_pos=(6.5, 28.6, 5.5, 33.4)))
    A(Comp('D1', 'Diode:BAT54S', 'BAT54S', 'Package_TO_SOT_SMD:SOT-23', (16, 36), rot=180,
           nets={'1': 'GND', '2': 'GND', '3': 'RX_IN'}, fields={'LCSC': 'C727126', 'Note': '反并联 ±0.3V 钳位'},
           ref_pos=(17, 33.5, 17, 38.6)))
    A(Comp('C1', 'Device:C', '100nF', C0805, (22, 30), rot=90, nets={'1': 'RX_IN', '2': 'RX_AC'},
           fields={'LCSC': 'C14663'}))
    A(Comp('R1', 'Device:R', '100Ω', R0805, (28, 30), rot=90, nets={'1': 'RX_AC', '2': 'LNA_IN'}))
    A(Comp('D2', 'Diode:BAT54S', 'BAT54S', 'Package_TO_SOT_SMD:SOT-23', (32, 36), rot=180,
           nets={'1': 'GND', '2': '+3V3', '3': 'LNA_IN'}, fields={'LCSC': 'C727126', 'Note': 'COM=信号 A=GND K=3V3'},
           ref_pos=(33, 33.5, 33, 38.6)))
    # ---- LNA ----
    A(Comp('R2', 'Device:R', '100k', R0805, (38, 34), nets={'1': 'LNA_IN', '2': 'VREF'},
           fields={'Note': '同相输入偏置到 1.65V'}))
    A(Comp('U1', 'AIsonic:OPA320xDBV', 'OPA320AIDBVT', 'Package_TO_SOT_SMD:SOT-23-5', (46, 31),
           nets={'3': 'LNA_IN', '4': 'LNA_FB', '1': 'LNA_OUT', '5': '+3V3', '2': 'GND'}, fields=OPA_FIELDS,
           ref_pos=(47, 27.5, 47, 34.6)))
    A(Comp('R3', 'Device:R', '100k', R0805, (46, 38), rot=90, nets={'1': 'LNA_FB', '2': 'LNA_OUT'},
           fields={'Note': 'Rf'}))
    A(Comp('R4', 'Device:R', '10k', R0805, (42, 40), nets={'1': 'LNA_FB', '2': 'VREF'}, fields={'Note': 'Rg'},
           ref_pos=(39.3, 39.6, 39.3, 41.0)))
    A(Comp('C2', 'Device:C', '100nF', C0805, (50, 24), nets={'1': '+3V3', '2': 'GND'}, fields={'LCSC': 'C14663'}))
    # ---- MFB band-pass 200 kHz ----
    A(Comp('R5', 'Device:R', '2.4k 1%', R0805, (56, 31), rot=90, nets={'1': 'LNA_OUT', '2': 'BPF_N'}))
    A(Comp('R6', 'Device:R', '143Ω 1%', R0805, (60, 37), nets={'1': 'BPF_N', '2': 'VREF'}))
    A(Comp('C3', 'Device:C', '1nF C0G', C0805, (66, 25), rot=90, nets={'1': 'BPF_N', '2': 'BPF_OUT'}))
    A(Comp('C4', 'Device:C', '1nF C0G', C0805, (64, 31), rot=90, nets={'1': 'BPF_N', '2': 'BPF_INV'}))
    A(Comp('U2', 'AIsonic:OPA320xDBV_N', 'OPA320AIDBVT', 'Package_TO_SOT_SMD:SOT-23-5', (72, 32),
           nets={'4': 'BPF_INV', '3': 'VREF', '1': 'BPF_OUT', '5': '+3V3', '2': 'GND'}, fields=OPA_FIELDS,
           ref_pos=(73, 28.5, 73, 35.6)))
    A(Comp('R7', 'Device:R', '4.7k 1%', R0805, (73, 41), rot=90, nets={'1': 'BPF_INV', '2': 'BPF_OUT'}))
    A(Comp('C5', 'Device:C', '100nF', C0805, (76, 24), nets={'1': '+3V3', '2': 'GND'}, fields={'LCSC': 'C14663'}))
    # ---- AD8338 VGA ----
    A(Comp('C6', 'Device:C', '100nF', C0805, (88, 32), rot=90, nets={'1': 'BPF_OUT', '2': 'VGA_INP'},
           fields={'LCSC': 'C14663'}))
    A(Comp('C7', 'Device:C', '100nF', C0805, (90, 35), rot=90, nets={'1': 'GND', '2': 'VGA_INM'}, fields={'LCSC': 'C14663'},
           ref_pos=(89, 36.6, 89, 38.0)))
    A(Comp('U3', 'AIsonic:AD8338', 'AD8338ACPZ-R7', 'Package_CSP:LFCSP-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm', (100, 34),
           nets={'1': 'VGA_INP', '2': None, '3': None, '4': 'VGA_INM', '7': 'AGC_F',
                 '11': 'VGA_OUT', '10': None, '12': None, '9': None, '13': 'VREF15', '16': 'VREF15',
                 '14': 'OFSN_C', '15': '+3V3', '6': '+3V3', '5': 'GND', '17': 'GND', '8': 'GND'},
           fields={'LCSC': 'C578701', 'MPN': 'AD8338ACPZ-R7'}, ref_pos=(106.5, 30.3, 94, 43.6)))
    A(Comp('C10', 'Device:C', '100nF', C0805, (106, 23), nets={'1': '+3V3', '2': 'GND'}, fields={'LCSC': 'C14663'}))
    A(Comp('C11', 'Device:C', '1uF', C0805, (110, 23), nets={'1': '+3V3', '2': 'GND'}))
    A(Comp('C9', 'Device:C', '100nF', C0805, (106, 47), nets={'1': 'OFSN_C', '2': 'VREF15'},
           fields={'LCSC': 'C14663', 'Note': '失调消除，高通 ≈4kHz'}))
    A(Comp('C12', 'Device:C', '100nF', C0805, (111, 47), nets={'1': 'VREF15', '2': 'GND'},
           fields={'LCSC': 'C14663'}))
    # ---- AGC control ----
    A(Comp('J3', 'Connector_Generic:Conn_01x02', 'AGC_CTRL', TB2, (80, 50), mirror=True,
           nets={'1': 'AGC_CTRL', '2': 'GND'}, fields={'Function': '1 AGC_CTRL(PA4 DAC) / 2 GND'},
           ref_pos=(78.5, 48.6, 77.5, 53.4)))
    A(Comp('R8', 'Device:R', '1k', R0805, (89, 50), rot=90, nets={'1': 'AGC_CTRL', '2': 'AGC_F'}))
    A(Comp('C13', 'Device:C', '10nF', C0805, (91, 53), nets={'1': 'AGC_F', '2': 'GND'}))
    # ---- ADC driver ----
    A(Comp('C14', 'Device:C', '1uF', C0805, (114, 32), rot=90, nets={'1': 'VGA_OUT', '2': 'ADC_OUT'}))
    A(Comp('R9', 'Device:R', '10k', R0805, (119, 36), nets={'1': 'ADC_OUT', '2': 'VREF'},
           fields={'Note': 'ADC 偏置到 1.65V'}))
    A(Comp('J2', 'Connector_Generic:Conn_01x04', 'TO_MCU', TB4, (131, 33),
           nets={'1': 'ADC_OUT', '2': 'VREF', '3': '+3V3', '4': 'GND'},
           fields={'Function': '1 ADC_OUT(PA0) / 2 VREF / 3 +3V3 / 4 GND'}, ref_pos=(130, 30.6, 130, 37.6)))
    A(Comp('J4', 'Connector_Generic:Conn_01x02', '3V3_IN', TB2, (131, 44),
           nets={'1': '+3V3', '2': 'GND'}, fields={'Function': '1 +3V3 / 2 GND'}, ref_pos=(130, 42.6, 130, 47.6)))
    A(Comp('C17', 'Device:C', '10uF', C0805, (122, 46), nets={'1': '+3V3', '2': 'GND'}))
    s.flag('+3V3', 118, 52)
    s.flag('GND', 122, 52)
    # ---- virtual ground 1.65 V ----
    A(Comp('R10', 'Device:R', '10k 1%', R0805, (20, 52), nets={'1': '+3V3', '2': 'VREF'}))
    A(Comp('R11', 'Device:R', '10k 1%', R0805, (20, 57), nets={'1': 'VREF', '2': 'GND'}))
    A(Comp('C15', 'Device:C', '10uF', C0805, (26, 57), nets={'1': 'VREF', '2': 'GND'}))
    A(Comp('C16', 'Device:C', '100nF', C0805, (31, 57), nets={'1': 'VREF', '2': 'GND'}, fields={'LCSC': 'C14663'}))
    for i, h in enumerate(['H1', 'H2', 'H3', 'H4']):
        A(Comp(h, 'Mechanical:MountingHole', 'M3', HOLE, (140 + i * 6, 20), in_bom=False))

    # wiring
    s.path(('J1', '1'), ('C1', '1'))
    s.path(('D1', '3'), (16, 30))
    s.junction(16, 30)
    s.path(('C1', '2'), ('R1', '1'))
    s.path(('R1', '2'), ('U1', '3'))
    s.path(('D2', '3'), (32, 30))
    s.path(('R2', '1'), (38, 30))
    s.junction(32, 30)
    s.junction(38, 30)
    s.path(('R4', '1'), (42, 32), ('U1', '4'))
    s.path(('R3', '1'), (42, 38))
    s.junction(42, 38)
    s.path(('U1', '1'), ('R5', '1'))
    s.path(('R3', '2'), (51, 38), (51, 31))
    s.junction(51, 31)
    s.path(('R5', '2'), ('C4', '1'))
    s.path(('R6', '1'), (60, 31))
    s.path(('C3', '1'), (60, 25), (60, 31))
    s.junction(60, 31)
    s.path(('C4', '2'), ('U2', '4'))
    s.path(('R7', '1'), (67, 41), (67, 31))
    s.junction(67, 31)
    s.path(('U2', '3'), (69, 36))
    s.label('VREF', 69, 36, 270)
    s.path(('U2', '1'), ('C6', '1'))
    s.path(('C3', '2'), (78, 25), (78, 32))
    s.path(('R7', '2'), (78, 41), (78, 32))
    s.junction(78, 32)
    s.path(('C6', '2'), ('U3', '1'))
    s.path(('C7', '2'), ('U3', '4'))
    s.path(('J3', '1'), ('R8', '1'))
    s.path(('R8', '2'), (92, 50), (92, 37), ('U3', '7'))
    s.path(('C13', '1'), (91, 50))
    s.junction(91, 50)
    s.path(('U3', '11'), ('C14', '1'))
    s.path(('C14', '2'), ('J2', '1'))
    s.path(('J2', '2'), (124, 33))
    s.label('VREF', 124, 33, 180)
    s.path(('J2', '3'), (127, 34))
    s.pwr('+3V3', 127, 34)
    s.path(('J2', '4'), (126, 35))
    s.pwr('GND', 126, 35)
    s.path(('J4', '1'), (127, 44))
    s.pwr('+3V3', 127, 44)
    s.path(('J4', '2'), (126, 45))
    s.pwr('GND', 126, 45)
    s.path(('R9', '1'), (119, 32))
    s.junction(119, 32)
    s.path(('R10', '2'), ('R11', '1'))
    s.path(('C15', '1'), (26, 54.5), (20, 54.5))
    s.path(('C16', '1'), (31, 54.5), (26, 54.5))
    s.path((31, 54.5), (35, 54.5))
    s.junction(20, 54.5)
    s.junction(26, 54.5)
    s.label('VREF', 35, 54.5, 0)

    s.box(3, 14, 136, 64, 'RX接收板（200kHz 接收前端电路）', (0, 90, 180))
    s.box(11, 24, 36, 42, '输入保护', (0, 130, 0))
    s.box(36.5, 18, 53, 44, 'LNA（OPA320，+20.8dB）', (0, 100, 0))
    s.box(53.5, 18, 80.5, 44, '200kHz 带通（MFB，Q≈3）', (0, 100, 0))
    s.box(81, 18, 113, 44.5, 'AGC 可变增益 AD8338', (0, 100, 0))
    s.box(113.5, 26, 124, 44.5, 'ADC 驱动/偏置', (0, 100, 0))
    s.box(14, 47, 40, 62, '虚拟地 VREF=1.65V', (0, 100, 0))
    s.box(76, 46, 100, 59, 'AGC 控制（STM32 DAC PA4）', (0, 100, 0))
    s.text(102, 56, 'VREF15 = AD8338 内部 1.5V 基准', 1.3)
    s.text(3, 68, 'RX 关键参数：', 1.8, bold=True)
    for i, t in enumerate([
            '1. 输入信号：mV 级回波；D1 反并联钳位 ±0.3V，D2 将 LNA 输入钳在 GND~3V3',
            '2. LNA：同相放大 G = 1 + R3/R4 = 11（+20.8dB），以 VREF=1.65V 为虚拟地',
            '3. BPF：多路反馈带通，R5=2.4k / R6=143Ω / R7=4.7k / C3=C4=1nF C0G → f0≈200kHz，Q≈3（BW≈±34kHz），中心增益≈-1',
            '4. AD8338：GAIN 0.1~1.1V 对应 0~80dB（12.5mV/dB），MODE=3V3 正斜率；DETO=GND、VAGC=VREF15 关闭内部 AGC',
            '5. ADC 驱动：OUTP 经 C14 1uF 交流耦合，R9 10k 偏置到 1.65V → J2.1 → STM32H750 PA0（ADC1）',
            '6. 时序：TX 发送 20 周期后等待 300us 再启动 ADC DMA（2048 点），然后 FFT / 峰值检测 / 距离计算']):
        s.text(3, 70.5 + i * 2.0, t, 1.3)
    return s
