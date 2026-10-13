"""Render a board to PNG (cropped to the outline) for visual review."""
import subprocess
import sys

from PIL import Image


def render(pcb, out, w, h, layers='F.Cu,B.Cu,F.SilkS,F.Fab,Edge.Cuts', dpi=300, origin=(100, 100)):
    pdf = out + '.pdf'
    subprocess.run(['kicad-cli', 'pcb', 'export', 'pdf', '--layers', layers, '--mode-single', '-o', pdf, pcb],
                   check=True, capture_output=True)
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-singlefile', pdf, out], check=True)
    im = Image.open(out + '.png')
    k = dpi / 25.4
    m = 3
    im.crop((int((origin[0] - m) * k), int((origin[1] - m) * k), int((origin[0] + w + m) * k),
             int((origin[1] + h + m) * k))).save(out + '.png')


if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]),
           *(sys.argv[5:6] or []))
