"""Monta o esboço: imagem com zoom lento, voz, legenda palavra por palavra, caixa do gancho, Gommo, selo e trilha.
Uso: <venv com Pillow>/python build.py   ->  out/esboco.mp4
"""
import json, subprocess, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path.cwd()
W, H, FPS = 1080, 1920, 30
GAP = 0.15
FILM = json.loads((HERE / 'film.json').read_text())
A = {k: HERE / Path(v).expanduser() for k, v in FILM['assets'].items()}
FONT, FONT_HOOK, WHISPER, SONG, BADGE = A['font'], A['fontHook'], A['whisper'], A['song'], A['badge']
ACTIVE = (255, 138, 76)
CAPTION_Y = 1150
OUT = HERE / 'out'


def wav_len(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def word_times(wav, words, offset):
    """Tempo de cada palavra do roteiro, pelo whisper; cai para proporcional se a contagem não bater."""
    tmp = OUT / 'w16.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-ar', '16000', tmp], check=True)
    subprocess.run(['whisper-cli', '-m', WHISPER, '-l', 'pt', '-ml', '1', '-sow', '-oj', '-of', OUT / 'w', '-f', tmp],
                   check=True, capture_output=True)
    segs = [s for s in json.loads((OUT / 'w.json').read_text())['transcription'] if s['text'].strip()]
    if len(segs) == len(words):
        return [(offset + s['offsets']['from'] / 1000, offset + s['offsets']['to'] / 1000) for s in segs]
    start = offset + segs[0]['offsets']['from'] / 1000
    end = offset + segs[-1]['offsets']['to'] / 1000
    total = sum(len(w) for w in words)
    out, t = [], start
    for w in words:
        d = (end - start) * len(w) / total
        out.append((t, t + d)); t += d
    return out


def chunks(words, times):
    """Grupos de até 3 palavras; quebra depois de pontuação."""
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        if len(cur) == 3 or w[-1] in ',.:?!' or (len(cur) == 2 and len(w) > 9):
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    return [(g, times[g[0]][0], times[g[-1]][1]) for g in groups]


def clip_frames(path, n):
    """Primeiros n quadros do clipe do Flow, cobrindo 1080x1920; repete o último se o clipe for curto."""
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-an', '-vf',
                          f'fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}',
                          '-frames:v', str(n), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                         check=True, capture_output=True).stdout
    size = W * H * 3
    frames = [Image.frombytes('RGB', (W, H), raw[i:i + size]) for i in range(0, len(raw) - size + 1, size)]
    return frames + [frames[-1]] * (n - len(frames))


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def draw_caption(img, words, group, active):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(str(FONT), 68)
    parts = [words[i].upper() for i in group]
    space = d.textlength(' ', font=f)
    widths = [d.textlength(p, font=f) for p in parts]
    x = (W - sum(widths) - space * (len(parts) - 1)) / 2
    for i, p, wd in zip(group, parts, widths):
        d.text((x, CAPTION_Y), p, font=f, fill=ACTIVE if i == active else (255, 255, 255),
               stroke_width=7, stroke_fill=(0, 0, 0), anchor='ls')
        x += wd + space


def hook_layer(text):
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = ImageFont.truetype(str(FONT_HOOK), 78)
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=f) > 780:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    lh, top = 96, 290
    box_h = lh * len(lines) + 70
    d.rounded_rectangle((84, top, 996, top + box_h), radius=26, fill=(255, 255, 255, 255))
    for i, ln in enumerate(lines):
        d.text((W / 2, top + 35 + lh * i + lh / 2), ln, font=f, fill=(0, 0, 0), anchor='mm')
    return layer


def main():
    film = FILM
    OUT.mkdir(exist_ok=True)
    scenes, t = [], 0.0
    for i, s in enumerate(film['scenes'], 1):
        vo = HERE / 'vo' / f'{i:02d}.wav'
        dur = wav_len(vo) + GAP + s.get('hold', 0)
        words = s['vo'].split()
        times = word_times(vo, words, t)
        img = Image.open(HERE / 'img' / f'{i:02d}.png').convert('RGB')
        scale = max(W / img.width, H / img.height) * 1.12
        img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
        clip = HERE / 'clips' / f'{i:02d}.mp4'
        frames = clip_frames(clip, round(dur * FPS) + 2) if clip.exists() else None
        scenes.append(dict(start=t, dur=dur, img=img, frames=frames, words=words, times=times, groups=chunks(words, times),
                           gommo=s.get('gommo'), badge=s.get('badge')))
        t += dur
    total = t
    hook = hook_layer(film['hook'])
    hook_until = scenes[film['hookUntilScene'] - 1]['start']
    gommo_imgs = {}
    for s in scenes:
        if s['gommo']:
            g = Image.open(HERE / s['gommo']).convert('RGBA')
            gommo_imgs[s['gommo']] = g.resize((340, round(g.height * 340 / g.width)), Image.LANCZOS)
    badge = Image.open(BADGE).convert('RGBA')
    badge = badge.resize((560, round(badge.height * 560 / badge.width)), Image.LANCZOS)

    narr = OUT / 'narracao.wav'
    inputs, filt = [], []
    for i, s in enumerate(scenes):
        inputs += ['-i', HERE / 'vo' / f'{i + 1:02d}.wav']
        filt.append(f'[{i}:a]adelay={round(s["start"] * 1000)}:all=1[a{i}]')
    filt.append(''.join(f'[a{i}]' for i in range(len(scenes))) + f'amix=inputs={len(scenes)}:normalize=0[out]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(filt), '-map', '[out]',
                    '-t', f'{total:.3f}', narr], check=True)

    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-i', narr, '-stream_loop', '-1', '-i', SONG,
                            '-filter_complex', f'[2:a]volume=-17dB,afade=t=out:st={total - 1.5:.2f}:d=1.5[m];'
                                               '[1:a][m]amix=inputs=2:normalize=0[a]',
                            '-map', '0:v', '-map', '[a]', '-t', f'{total:.3f}', '-c:v', 'libx264', '-pix_fmt',
                            'yuv420p', '-crf', '20', '-c:a', 'aac', '-b:a', '192k', OUT / 'esboco.mp4'],
                           stdin=subprocess.PIPE)
    for n in range(round(total * FPS)):
        tt = n / FPS
        s = next(x for x in reversed(scenes) if x['start'] <= tt)
        p = (tt - s['start']) / s['dur']
        if s['frames']:
            frame = s['frames'][min(round((tt - s['start']) * FPS), len(s['frames']) - 1)].convert('RGBA')
        else:
            frame = None
        img = s['img']
        cw = min(img.width, img.height * W / H) / (1 + 0.10 * p)
        ch = cw * H / W
        x0, y0 = (img.width - cw) / 2, (img.height - ch) / 2
        frame = frame or img.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((W, H), Image.BILINEAR).convert('RGBA')
        if tt < hook_until:
            frame.alpha_composite(hook)
        if s['gommo']:
            g = gommo_imgs[s['gommo']]
            e = ease((tt - s['start'] - 1.0) / 0.35)
            if e > 0:
                gx = round(W - g.width - 40 + (1 - e) * (g.width + 60))
                frame.alpha_composite(g, (gx, 120))
        if s['badge']:
            frame.alpha_composite(badge, ((W - badge.width) // 2, 1185))
        for group, a, b in s['groups']:
            nxt = [g for g in s['groups'] if g[1] > a]
            end = nxt[0][1] if nxt else s['start'] + s['dur']
            if a <= tt < end:
                active = next((i for i in group if s['times'][i][0] <= tt < s['times'][i][1] + 0.05), group[-1] if tt >= b else group[0])
                draw_caption(frame, s['words'], group, active)
        enc.stdin.write(frame.convert('RGB').tobytes())
    enc.stdin.close()
    enc.wait()
    print(f'{OUT / "esboco.mp4"}  {total:.1f}s')


if __name__ == '__main__':
    main()
