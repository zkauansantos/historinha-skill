---
name: historinha
description: Produz um anúncio "historinha meme" para app (cartoon 2D por IA, ~50 s, 10 cenas, narração em 1ª pessoa, legenda palavra por palavra, gancho em caixa branca, CTA de loja). Gera folha de personagem, cenas e voz no Gemini, cola a tela real do app no celular desenhado, escreve os prompts do Google Flow e monta o MP4. Use quando pedirem historinha, cartoon meme, vídeo narrado com personagem.
---

# Historinha meme

Formato do Thallis Ribeiro (x.com/thallisribeiro/status/2125207626229088654): cartoon 2D de meme, 10 cenas de ~5 s com corte seco, narração em 1ª pessoa, gancho numa caixa branca no topo, legenda grande palavra por palavra e o produto entrando como a virada da história.

## Requisitos

- `GEMINI_API_KEY` no ambiente ou num `.env` (imagem: `gemini-3.1-flash-image`; voz: `gemini-3.8-flash-tts`).
- `ffmpeg`, `whisper-cli` (whisper.cpp) com um modelo `ggml-small.bin`, Python 3 com Pillow.
- Conta no Google Flow (labs.google/flow) para animar.

## Roteiro (10 falas, ~2,7 palavras por segundo)

1. Gancho: "sou só eu, ou você também...?" com a dor real do público (o resultado que não vem, não a tarefa chata).
2. Conflito que bate com a caixa do gancho.
3. O começo empolgado.
4. A queda.
5. A verdade ("eu sei o que fazer, mas não consigo").
6. A culpa não é sua: falta tal coisa.
7. O custo de continuar assim.
8. A virada: o que resolve.
9. O produto fazendo exatamente isso.
10. CTA curto ("toca no botão e baixa o X").

Dor contada pelo personagem, em 1ª pessoa. Nada que afirme o corpo ou a vida de quem assiste (política de anúncios da Meta).

## Passos

1. Copie `film.example.json` para `<projeto>/film.json` e ajuste: `assets` (fonte, trilha, selo da loja, modelo do whisper; caminhos relativos à pasta do projeto), `hook`, `hookUntilScene`, `style`, `sheet` (folha de personagem) e `scenes` com `vo`, `img` e, se quiser, `gommo` (PNG do mascote que entra uma vez), `badge`, `hold` e `screen`.
2. Na pasta do projeto: `python3 <skill>/scripts/gen.py all`. Refazer cenas: `--redo 3,7` (0 = folha). Confira cada imagem: texto em inglês, mão solta, celular gigante, personagem trocado.
3. Tela do app: nunca peça para a IA desenhar a tela, ela aumenta o celular e solta a mão. Peça "normal-sized smartphone ... screen is a plain flat solid pure green (#00FF00) rectangle" e "each character has exactly two arms and two hands", ponha `"screen": "app/home.png"` na cena e rode `python <skill>/scripts/screen.py`. Ele acha as bordas do verde, cola o print na perspectiva com a cena ampliada 3x e recorta pela curva do aparelho.
4. Esboço: `python <skill>/scripts/build.py` gera `out/esboco.mp4` (1080x1920) com zoom lento, voz, legenda no tempo do whisper, caixa do gancho, mascote, selo e trilha.
5. Animar no Flow: um clipe de 8 s por cena, imagem da cena como primeiro quadro, último quadro vazio, Veo 3.1 Lite. Passo a passo e prompts de exemplo em `references/flow.md`. Salve como `clips/01.mp4` ... `clips/10.mp4` (dois dígitos).
6. Rode `build.py` de novo: ele usa o clipe quando existe, corta no tamanho da fala e descarta o som do Flow.

## Pegadinhas

- O Gemini TTS lê em voz alta qualquer instrução de estilo enviada junto: mande só a fala.
- Ele devolve 44 bytes de cabeçalho WAV dentro do PCM e ~160 ms de ruído no fim; `gen.py` corta os dois (senão estala na troca de fala).
- Limite de 10 pedidos por minuto no TTS: deu 429, espere 1 minuto e rode de novo (só gera o que falta).
- Nome do produto em inglês: troque a grafia só para a voz em `SPOKEN` no `gen.py`.
- Peça no `style` que todo texto dentro da cena saia no idioma do público, senão vem em inglês.
- Mascote e selo longe dos rostos; a faixa de baixo do Reels é coberta pela interface.
