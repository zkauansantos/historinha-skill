"""Monta a variante musical (D2): música no lugar da narração, legenda da letra e cortes em tempos fixos.
film.json: "lines" = [[início, fim, "letra"]] e "scenes" = [{"img": "01", "start": s, "badge"?: true}].
Uso: <venv com Pillow>/python music.py   ->  out/clipe.mp4
"""
import subprocess
from PIL import Image
from build import FILM, HERE, OUT, W, H, FPS, A, BADGE, chunks, clip_frames, draw_caption


def line_times(t0, t1, words):
    """shortcut: tempo de cada palavra proporcional ao tamanho dentro do verso; whisper por palavra erra em música."""
    total = sum(len(w) for w in words)
    out, t = [], t0
    for w in words:
        d = (t1 - t0) * len(w) / total
        out.append((t, t + d)); t += d
    return out


def main():
    OUT.mkdir(exist_ok=True)
    song = A['song']
    total = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', song],
                                 capture_output=True, text=True, check=True).stdout)
    words, times = [], []
    for t0, t1, text in FILM['lines']:
        ws = text.split()
        words += ws; times += line_times(t0, t1, ws)
    groups = chunks(words, times)
    scenes = FILM['scenes']
    for i, s in enumerate(scenes):
        s['end'] = scenes[i + 1]['start'] if i + 1 < len(scenes) else total
        img = Image.open(HERE / 'img' / f"{s['img']}.png").convert('RGB')
        scale = max(W / img.width, H / img.height) * (1 if s.get('badge') else 1.12)
        s['im'] = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
        clip = HERE / 'clips' / f"{s['img']}.mp4"
        s['frames'] = clip_frames(clip, round((s['end'] - s['start']) * FPS) + 2) if clip.exists() else None
    badge = Image.open(BADGE).convert('RGBA')
    badge = badge.resize((560, round(badge.height * 560 / badge.width)), Image.LANCZOS)

    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-i', song, '-map', '0:v', '-map', '1:a', '-t', f'{total:.3f}',
                            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-c:a', 'aac', '-b:a', '192k',
                            OUT / 'clipe.mp4'], stdin=subprocess.PIPE)
    for n in range(round(total * FPS)):
        tt = n / FPS
        s = next(x for x in reversed(scenes) if x['start'] <= tt)
        p = 0 if s.get('badge') else (tt - s['start']) / (s['end'] - s['start'])
        if s['frames']:
            frame = s['frames'][min(round((tt - s['start']) * FPS), len(s['frames']) - 1)].convert('RGBA')
        else:
            img = s['im']
            cw = min(img.width, img.height * W / H) / (1 + 0.10 * p)
            ch = cw * H / W
            x0, y0 = (img.width - cw) / 2, (img.height - ch) / 2
            frame = img.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((W, H), Image.BILINEAR).convert('RGBA')
        if s.get('badge'):
            frame.alpha_composite(badge, ((W - badge.width) // 2, 1185))
        for g, a, b in groups:
            if a <= tt < b + 0.15:
                active = next((i for i in g if times[i][0] <= tt < times[i][1]), g[-1])
                draw_caption(frame, words, g, active)
                break
        enc.stdin.write(frame.convert('RGB').tobytes())
    enc.stdin.close()
    enc.wait()
    print(f'{OUT / "clipe.mp4"}  {total:.1f}s')


if __name__ == '__main__':
    main()
