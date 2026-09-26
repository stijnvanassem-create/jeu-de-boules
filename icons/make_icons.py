# Generates the app icons (pure Python, no dependencies): python3 icons/make_icons.py
import zlib, struct, math, os

def png(path, w, h, px):
    raw = b''.join(b'\x00' + bytes(px[y*w*3:(y+1)*w*3]) for y in range(h))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))

BG = (184, 71, 31)
L = (-0.45, -0.6, 0.66); n = math.sqrt(sum(c*c for c in L)); L = tuple(c/n for c in L)
H = (L[0], L[1], L[2] + 1); n = math.sqrt(sum(c*c for c in H)); H = tuple(c/n for c in H)

def ball(u, v, cx, cy, r, base, grooves):
    nx, ny = (u-cx)/r, (v-cy)/r
    d = nx*nx + ny*ny
    if d >= 1:
        return None
    nz = math.sqrt(1-d)
    dif = max(0, nx*L[0] + ny*L[1] + nz*L[2])
    spec = max(0, nx*H[0] + ny*H[1] + nz*H[2]) ** 40
    col = [min(255, c*(0.32 + 0.8*dif) + 255*spec*0.85) for c in base]
    for ax in grooves:
        if abs(nx*ax[0] + ny*ax[1] + nz*ax[2]) < 0.035:
            col = [c*0.55 for c in col]
    return col

def sample(u, v):
    col = list(BG)
    sd = ((u-0.49)/0.33)**2 + ((v-0.84)/0.07)**2
    if sd < 1:
        col = [c*(0.72 + 0.28*sd) for c in col]
    return (ball(u, v, 0.46, 0.48, 0.30, (172, 180, 188), [(0.0, 0.94, 0.34), (0.8, -0.2, 0.56)])
            or ball(u, v, 0.80, 0.78, 0.075, (236, 178, 74), [])
            or col)

def make(size, path, ss=2):
    px = []
    for y in range(size):
        for x in range(size):
            acc = [0, 0, 0]
            for sy in range(ss):
                for sx in range(ss):
                    c = sample((x + (sx+.5)/ss)/size, (y + (sy+.5)/ss)/size)
                    for i in range(3):
                        acc[i] += c[i]
            px += [int(a/(ss*ss)) for a in acc]
    png(path, size, size, px)

here = os.path.dirname(os.path.abspath(__file__))
for s, name in [(512, 'icon-512.png'), (192, 'icon-192.png'), (180, 'apple-touch-icon.png')]:
    make(s, os.path.join(here, name))
