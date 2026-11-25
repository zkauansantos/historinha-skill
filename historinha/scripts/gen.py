"""Gera as imagens (Gemini image) e as falas (Gemini TTS) do esboço. Pula o que já existe.
Uso: python3 gen.py [images|voice|all] [--redo N,N]
"""
import base64, json, os, sys, urllib.request, wave
from pathlib import Path

HERE = Path.cwd()
IMG_MODEL = 'gemini-3.1-flash-image'
TTS_MODEL = 'gemini-3.8-flash-tts'
VOICE = 'Puck'
SPOKEN = {'Eatiary': 'Itiéri'}


def key():
    if os.environ.get('GEMINI_API_KEY'):
        return os.environ['GEMINI_API_KEY']
    env = next((d / '.env' for d in [HERE, *HERE.parents] if (d / '.env').exists()), None)
    for line in (env.read_text().splitlines() if env else []):
        if line.startswith('GEMINI_API_KEY='):
            return line.split('=', 1)[1].strip().strip('"')
    sys.exit('Falta GEMINI_API_KEY (ambiente ou .env)')


def call(model, body):
    req = urllib.request.Request(
        f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
        data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': key()})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def inline(path):
    return {'inline_data': {'mime_type': 'image/png', 'data': base64.b64encode(Path(path).read_bytes()).decode()}}


def image(prompt, refs, out):
    body = {'contents': [{'parts': [*map(inline, refs), {'text': prompt}]}],
            'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '9:16'}}}
    for part in call(IMG_MODEL, body)['candidates'][0]['content']['parts']:
        if 'inlineData' in part:
            out.write_bytes(base64.b64decode(part['inlineData']['data']))
            return
    raise RuntimeError(f'sem imagem para {out.name}')


def speak(text):
    for k, v in SPOKEN.items():
        text = text.replace(k, v)
    return text


def voice(text, out):
    body = {'contents': [{'parts': [{'text': speak(text)}]}],
            'generationConfig': {'responseModalities': ['AUDIO'],
                                 'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': VOICE}}}}}
    data = call(TTS_MODEL, body)['candidates'][0]['content']['parts'][0]['inlineData']['data']
    with wave.open(str(out), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        pcm = base64.b64decode(data)
        w.writeframes(trim_tail(pcm[44:] if pcm[:4] == b'RIFF' else pcm))


def trim_tail(pcm, win=480, quiet=60):
    """O TTS devolve ~160 ms de ruído alto colado depois do silêncio final: corta no último trecho silencioso."""
    import array
    a = array.array('h', pcm)
    rms = lambda j: (sum(x * x for x in a[j:j + win]) / win) ** .5
    j = len(a) - win
    while j > 3 * win and not all(rms(j - k * win) < quiet for k in range(3)):
        j -= win
    return a[:j + win].tobytes() if j > len(a) - 24000 else pcm


def main():
    film = json.loads((HERE / 'film.json').read_text())
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    redo = set()
    if '--redo' in sys.argv:
        redo = {int(n) for n in sys.argv[sys.argv.index('--redo') + 1].split(',')}
    (HERE / 'img').mkdir(exist_ok=True); (HERE / 'vo').mkdir(exist_ok=True)
    sheet = HERE / 'img' / 'sheet.png'
    if what in ('images', 'all'):
        if not sheet.exists() or 0 in redo:
            image(film['sheet'], [], sheet); print('sheet ok')
        for i, s in enumerate(film['scenes'], 1):
            out = HERE / 'img' / f'{i:02d}.png'
            if out.exists() and i not in redo:
                continue
            refs = [sheet] + ([HERE / 'img' / '01.png'] if i > 1 else []) + [HERE / r for r in s.get('refs', [])]
            image(f"{film['style']}\n\nScene: {s['img']}", refs, out); print(out.name, 'ok')
    if what in ('voice', 'all'):
        for i, s in enumerate(film['scenes'], 1):
            out = HERE / 'vo' / f'{i:02d}.wav'
            if out.exists() and i not in redo:
                continue
            voice(s['vo'], out); print(out.name, 'ok')


if __name__ == '__main__':
    main()
