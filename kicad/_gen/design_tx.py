"""AIsonic TX driver board: TC4427 -> IRL540N -> EE19 1:8 -> LC match -> 200 kHz PZT."""
from schgen import Comp, Schematic

PROJECT = 'AIsonic_TX_Driver_V1'
BOARD = (100.0, 70.0)

R0805 = 'Resistor_SMD:R_0805_2012Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
C1206 = 'Capacitor_SMD:C_1206_3216Metric'
TB381 = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1-2-3.81_1x02_P3.81mm_Horizontal'
TB508 = 'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal'
HOLE = 'MountingHole:MountingHole_3.2mm_M3'

NETCLASSES = {
    'Power': dict(width=1.0, clearance=0.3, nets=['+12V', 'GND', 'DRAIN']),
    'HV': dict(width=0.8, clearance=1.0, nets=['SEC_HI', 'LC_MID', 'TX+', 'TX-']),
    'Gate': dict(width=0.5, clearance=0.25, nets=['GATE', 'GATE_A', 'GATE_B']),
}

# PCB placement: ref -> (x_mm, y_mm, rotation_deg), board-relative, top side.
PLACE = {
    'J1': (4.5, 22.0, 270), 'J2': (5.5, 52.0, 270),
    'R1': (12.0, 22.0, 0), 'R5': (17.0, 26.5, 90),
    'U1': (24.0, 26.0, 0),
    'C1': (24.0, 21.5, 0), 'C2': (24.0, 31.5, 0),
    'R2': (31.0, 25.4, 0), 'R4': (31.0, 28.0, 0), 'R3': (35.0, 32.0, 90),
    'Q1': (38.0, 28.0, 0), 'D1': (44.0, 35.5, 0),
    'C5': (47.0, 47.0, 180),
    'T1': (60.0, 32.0, 90),
    'L1': (75.0, 50.0, 0),
    'C3': (82.0, 58.0, 0),
    'J3': (94.5, 42.0, 90),
    'H1': (4.0, 4.0, 0), 'H2': (96.0, 4.0, 0), 'H3': (4.0, 66.0, 0), 'H4': (96.0, 66.0, 0),
}

REF_AT = {'U1': (24.0, 26.0, 90), 'R4': (31.0, 29.6, 0), 'R2': (31.0, 23.8, 0), 'C1': (21.0, 21.5, 0),
          'C2': (21.0, 31.5, 0)}

SILK = [
    (50.0, 3.5, 'AIsonic TX Driver V1.0  200kHz', 1.5),
    (76.0, 66.0, '! HIGH VOLTAGE 150Vpp', 1.2),
    (6.0, 16.0, '1:PWM 2:GND', 0.9),
    (6.0, 45.5, '1:+12V 2:GND', 0.9),
    (91.0, 31.0, '1:TX+ 2:TX-', 0.9),
]


def build():
    s = Schematic(PROJECT, 'AIsonic TX 发射驱动板（200kHz）', paper='A4', comments=(
        '按 原理图/原理图.png TX发射板 设计',
        'Burst 20 周期/100us，禁止连续发射；发射后等 300us 再开 RX ADC',
        '+12V 仅供 TX 功率级，与 MCU 3V3 单点共地'))
    A = s.add
    A(Comp('J1', 'Connector_Generic:Conn_01x02', 'PWM_IN', TB381, (8, 24), mirror=True,
           nets={'1': 'PWM_IN', '2': 'GND'}, fields={'Function': '1 PWM(PA8) / 2 GND'},
           ref_pos=(6.5, 22.6, 5.5, 27.4)))
    A(Comp('R1', 'Device:R', '10Ω', R0805, (15, 24), rot=90, nets={'1': 'PWM_IN', '2': 'DRV_IN'}))
    A(Comp('R5', 'Device:R', '10k', R0805, (21, 29), nets={'1': 'DRV_IN', '2': 'GND'},
           fields={'Note': '输入下拉，MCU 未启动时 MOS 关断'}))
    A(Comp('U1', 'Driver_FET:TC4427xOA', 'TC4427AEOA', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm', (30, 25),
           nets={'2': 'DRV_IN', '4': 'DRV_IN', '3': 'GND', '6': '+12V', '7': 'GATE_A', '5': 'GATE_B'},
           fields={'LCSC': 'C20551', 'MPN': 'TC4427AEOA713'}, ref_pos=(31, 20.5, 31.3, 28.6)))
    A(Comp('C1', 'Device:C', '100nF 50V', C0805, (37, 19), nets={'1': '+12V', '2': 'GND'},
           fields={'LCSC': 'C14663'}))
    A(Comp('C2', 'Device:C', '10uF 25V', C1206, (43, 19), nets={'1': '+12V', '2': 'GND'}))
    A(Comp('R2', 'Device:R', '10Ω', R0805, (39, 24), rot=90, nets={'1': 'GATE_A', '2': 'GATE'},
           ref_pos=(37.4, 22.6, 39.4, 22.6)))
    A(Comp('R4', 'Device:R', '10Ω', R0805, (39, 26), rot=90, nets={'1': 'GATE_B', '2': 'GATE'},
           ref_pos=(37.4, 28.0, 39.4, 28.0)))
    A(Comp('R3', 'Device:R', '10k', R0805, (45, 29), nets={'1': 'GATE', '2': 'GND'},
           fields={'Note': 'Rgs 栅极下拉'}))
    A(Comp('Q1', 'Transistor_FET:Q_NMOS_GDS', 'IRL540N', 'Package_TO_SOT_THT:TO-220-3_Vertical', (49, 24),
           nets={'1': 'GATE', '2': 'DRAIN', '3': 'GND'}, fields={'LCSC': 'C5240567', 'MPN': 'IRL540NPBF'},
           ref_pos=(51.2, 23.0, 51.2, 24.4)))
    A(Comp('D1', 'Device:D', 'SMBJ100A', 'Diode_SMD:D_SMB', (58.5, 24), rot=270,
           nets={'1': 'DRAIN', '2': 'GND'}, fields={'LCSC': 'C151249', 'Note': 'Drain TVS，阴极接 Drain'},
           ref_pos=(59.5, 23.6, 59.5, 25.0)))
    A(Comp('C5', 'Device:C_Polarized', '100uF 25V', 'Capacitor_THT:CP_Radial_D8.0mm_P3.50mm', (53, 15),
           nets={'1': '+12V', '2': 'GND'}, fields={'Note': '脉冲储能，紧靠 T1 初级'}))
    A(Comp('T1', 'AIsonic:EE19_1to8', 'EE19 1:8 (10T:80T)', 'AIsonic:EE19_5+5_Vertical', (67.5, 19),
           nets={'1': '+12V', '3': 'DRAIN', '6': 'TX-', '10': 'SEC_HI'},
           fields={'Note': '外购/自绕，同名端 1 与 6；次级 10 脚接 LC 匹配'}, ref_pos=(64.5, 14.3, 63.5, 24.6)))
    A(Comp('L1', 'Device:L', '300uH', 'Inductor_THT:L_Radial_D10.0mm_P5.00mm_Fastron_07M', (77, 21), rot=90,
           nets={'1': 'SEC_HI', '2': 'LC_MID'}, fields={'Note': '按 PZT 电容微调 220~330uH'}))
    A(Comp('C3', 'Device:C', '2.2nF 1kV', 'Capacitor_THT:C_Disc_D7.5mm_W5.0mm_P7.50mm', (83.5, 21), rot=90,
           nets={'1': 'LC_MID', '2': 'TX+'}, fields={'Note': '高压瓷片 ≥1kV'}))
    A(Comp('J3', 'Connector_Generic:Conn_01x02', 'TX_PZT', TB508, (91, 21),
           nets={'1': 'TX+', '2': 'TX-'}, fields={'Function': '1 TX+ / 2 TX-'}, ref_pos=(90, 19.5, 89, 24.3)))
    A(Comp('J2', 'Connector_Generic:Conn_01x02', '+12V_IN', TB508, (8, 36), mirror=True,
           nets={'1': '+12V', '2': 'GND'}, fields={'Function': '1 +12V / 2 GND'}, ref_pos=(6.5, 34.6, 5.5, 39.4)))
    for i, h in enumerate(['H1', 'H2', 'H3', 'H4']):
        A(Comp(h, 'Mechanical:MountingHole', 'M3', HOLE, (60 + i * 6, 36), in_bom=False))
    s.flag('+12V', 20, 36)
    s.flag('GND', 25, 36)

    s.path(('J1', '1'), ('R1', '1'))
    s.path(('R1', '2'), ('U1', '2'))
    s.path(('U1', '4'), (24, 26), (24, 24))
    s.path(('R5', '1'), (21, 24))
    s.junction(24, 24)
    s.junction(21, 24)
    s.path(('U1', '7'), ('R2', '1'))
    s.path(('U1', '5'), ('R4', '1'))
    s.path(('R2', '2'), ('Q1', '1'))
    s.path(('R4', '2'), (42, 26), (42, 24))
    s.path(('R3', '1'), (45, 24))
    s.junction(42, 24)
    s.junction(45, 24)
    s.path(('Q1', '2'), (50, 21), ('T1', '3'))
    s.path(('D1', '1'), (58.5, 21))
    s.junction(58.5, 21)
    s.path(('T1', '10'), ('L1', '1'))
    s.path(('L1', '2'), ('C3', '1'))
    s.path(('C3', '2'), ('J3', '1'))

    s.box(3, 8, 97, 33, 'TX发射板（200kHz 发射驱动电路）', (194, 0, 0))
    s.box(12, 16, 46.5, 32, '栅极驱动 TC4427', (0, 100, 0))
    s.box(47, 9.5, 63, 32, '功率 MOS / TVS', (0, 100, 0))
    s.box(63.2, 9.5, 74.5, 26.5, '变压器 EE19 1:8', (0, 100, 0))
    s.box(74.8, 14, 87.5, 25, 'LC 匹配（200kHz）', (0, 100, 0))
    s.text(12, 35.5, '供电接口 +12V', 1.5, bold=True)
    s.text(3, 44, 'TX 关键参数：', 1.8, bold=True)
    for i, t in enumerate(['1. 发射频率 200kHz（PWM 50%，STM32H750 PA8）',
                           '2. 发射脉冲 20 周期（100us），禁止连续发射',
                           '3. 次级驱动电压 80~150Vpp',
                           '4. 变压器 1:8（10T:80T），同名端 T1.1 / T1.6',
                           '5. 匹配 L1=300uH、C3=2.2nF/1kV（按 PZT 实测微调）',
                           '6. TC4427 双通道并联：INA=INB，OUTA/OUTB 各串 10Ω 到栅极',
                           '7. PCB：C5-T1-Q1-GND 功率回路最短；次级/LC/J3 高压区间距 ≥1mm']):
        s.text(3, 46.5 + i * 2.0, t, 1.3)
    return s
