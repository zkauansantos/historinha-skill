"""Cola a tela real do app (film.json "screen") sobre a tela verde da cena, na perspectiva dela.
Uso: <venv com Pillow>/python screen.py   ->  img/NN.png (o original verde fica em img/NN_green.png)
"""
import json, shutil
from pathlib import Path
from PIL import Image, ImageFilter

HERE = Path.cwd()


def is_green(p):
    r, g, b = p[:3]
    return g > 150 and g - r > 70 and g - b > 70


def fit(pts):
    """Reta u = a*v + b por mínimos quadrados."""
    n = len(pts)
    sv, su = sum(v for v, _ in pts), sum(u for _, u in pts)
    svv, svu = sum(v * v for v, _ in pts), sum(v * u for v, u in pts)
    a = (n * svu - sv * su) / (n * svv - sv * sv)
    return a, (su - a * sv) / n


def corners(img):
    """Cantos da tela verde: retas ajustadas no miolo de cada lado (fora das curvas) e cruzadas."""
    w, h = img.size
    px = img.load()
    rows, cols = {}, {}
    for y in range(h):
        for x in range(w):
            if is_green(px[x, y]):
                rows.setdefault(y, []).append(x)
                cols.setdefault(x, []).append(y)
    ys, xs = sorted(rows), sorted(cols)
    mid = lambda k: k[len(k) // 5: -len(k) // 5]
    left = fit([(y, min(rows[y])) for y in mid(ys)])
    right = fit([(y, max(rows[y])) for y in mid(ys)])
    def edge(pick):
        pts = []
        for x in xs:
            y = pick(cols[x])
            lx, rx = left[0] * y + left[1], right[0] * y + right[1]
            f = (x - lx) / (rx - lx)
            if 0.15 < f < 0.3 or 0.7 < f < 0.85:
                pts.append((x, y))
        return fit(pts)

    top, bottom = edge(min), edge(max)
    def cross(vert, horiz):
        a, b = vert
        c, d = horiz
        y = (c * b + d) / (1 - c * a)
        return a * y + b, y

    return [cross(left, top), cross(right, top), cross(right, bottom), cross(left, bottom)]


def solve(a, b):
    n = len(b)
    m = [row + [v] for row, v in zip(a, b)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[piv] = m[piv], m[c]
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    return [m[i][n] / m[i][i] for i in range(n)]


def coeffs(dst, src):
    """Coeficientes de Image.PERSPECTIVE: mapeia cada ponto de dst (saída) para src (tela do app)."""
    a, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        a.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return solve(a, b)


def main():
    film = json.loads((HERE / 'film.json').read_text())
    for i, s in enumerate(film['scenes'], 1):
        if not s.get('screen'):
            continue
        out, green = HERE / 'img' / f'{i:02d}.png', HERE / 'img' / f'{i:02d}_green.png'
        if sum(is_green(p) for p in Image.open(out).convert('RGB').get_flattened_data()) > 2000:
            shutil.copy(out, green)
        scene = Image.open(green).convert('RGB')
        scene = scene.resize((scene.width * 3, scene.height * 3), Image.LANCZOS)
        app = Image.open(HERE / s['screen']).convert('RGB')
        q = corners(scene)
        cx, cy = sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4
        q = [(cx + (x - cx) * 1.02, cy + (y - cy) * 1.02) for x, y in q]
        tw = round(max(abs(q[1][0] - q[0][0]), abs(q[2][0] - q[3][0])) * 1.3)
        app = app.resize((tw, round(app.height * tw / app.width)), Image.LANCZOS)
        aw, ah = app.size
        warped = app.transform(scene.size, Image.PERSPECTIVE, coeffs(q, [(0, 0), (aw, 0), (aw, ah), (0, ah)]),
                               Image.BICUBIC)
        mask = Image.new('L', scene.size, 0)
        mp, sp = mask.load(), scene.load()
        for y in range(scene.height):
            for x in range(scene.width):
                if is_green(sp[x, y]):
                    mp[x, y] = 255
        scene.paste(warped, (0, 0), mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.5)))
        scene.save(out)
        print(out.name, 'tela colada', q)


if __name__ == '__main__':
    main()
