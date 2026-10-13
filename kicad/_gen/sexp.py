"""Minimal S-expression reader/writer for KiCad files."""
import re

_tok = re.compile(r'\s*(\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+)', re.S)


class Sym(str):
    """Bare (unquoted) atom."""


def parse(text):
    stack, cur = [], []
    pos = 0
    n = len(text)
    while pos < n:
        m = _tok.match(text, pos)
        if not m:
            break
        pos = m.end()
        t = m.group(1)
        if t == '(':
            stack.append(cur)
            cur = []
        elif t == ')':
            done = cur
            cur = stack.pop()
            cur.append(done)
        elif t.startswith('"'):
            cur.append(t[1:-1].replace('\\"', '"').replace('\\\\', '\\'))
        else:
            cur.append(Sym(t))
    return cur[0] if len(cur) == 1 else cur


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


def dump(node, indent=0):
    if not isinstance(node, list):
        if isinstance(node, Sym):
            return str(node)
        if isinstance(node, str):
            return q(node)
        if isinstance(node, float):
            return ('%.4f' % node).rstrip('0').rstrip('.')
        return str(node)
    simple = all(not isinstance(x, list) for x in node)
    if simple:
        return '(' + ' '.join(dump(x) for x in node) + ')'
    pad = '\t' * (indent + 1)
    head = []
    rest = list(node)
    while rest and not isinstance(rest[0], list):
        head.append(dump(rest.pop(0)))
    out = '(' + ' '.join(head)
    for x in rest:
        out += '\n' + pad + dump(x, indent + 1)
    return out + '\n' + '\t' * indent + ')'


def find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def find1(node, key):
    r = find(node, key)
    return r[0] if r else None
