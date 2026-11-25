# Animar as cenas no Google Flow

Passo a passo para transformar `img/01.png` a `img/10.png` em clipes. Depois, coloque os clipes em `clips/01.mp4` a `clips/10.mp4` e peça ao agente para remontar.

## Passo a passo

1. Os prompts das cenas ficam no `flow.md` da pasta do projeto (o agente escreve um por cena; o do primeiro vídeo está mais abaixo como exemplo). Abra https://labs.google/flow e entre com a conta Google que tem o plano (o Flow gasta créditos por vídeo).
2. Clique em **Novo projeto**.
3. Na caixa de prompt, troque o modo para **Frames para vídeo** (Frames to Video). É o modo que usa a sua imagem como primeiro quadro.
4. Em configurações (ícone de ajuste ao lado do prompt):
   - **Proporção:** 9:16 (vertical).
   - **Modelo:** Veo 3.1 Lite (10 créditos por clipe; o Quality gasta 200). O Lite bastou no primeiro vídeo.
   - **Resultados por prompt:** 1 (cada resultado gasta créditos).
5. Clique no **+** do primeiro quadro e envie a imagem da cena (`img/01.png`). Deixe o último quadro vazio.
6. Cole o prompt da cena (lista abaixo) e gere.
7. Assista os resultados. Bom = o personagem continua igual à imagem, faz só a ação pedida e a câmera não pula. Se deformar o rosto ou inventar texto, gere de novo.
8. Baixe o melhor (ícone de download, **1080p** se aparecer a opção) e renomeie para `01.mp4`.
9. Repita para as 10 cenas e jogue os arquivos em `clips/` da pasta do projeto, com dois dígitos (`01.mp4`, não `1.mp4`).

O Flow gera clipes de 8 s com som. Não tem problema: o agente corta cada clipe no tamanho da fala e tira o som do Flow.

## Prompts (cole um por cena)

Todos terminam com a mesma frase para segurar o estilo. Copie o bloco inteiro.

**01**
```
The woman yanks the phone out of the man's hand; he tips back on the kitchen stool, flailing his arms, holding the food container. Slight camera shake. Keep the exact 2D cartoon art style, characters and colors of the image. No dialogue, no lip movement, no new text.
```
**02**
```
Slow push-in from the woman's face down to the phone screen. She raises one eyebrow and sighs. Keep the exact 2D cartoon art style, characters and colors of the image. No dialogue, no lip movement, no new text.
```
**03**
```
The man points proudly at the diet sheet on the fridge and nods with a big grin; sparkles twinkle. The woman in the back rolls her eyes. Keep the exact 2D cartoon art style, characters and colors of the image. No dialogue, no lip movement, no new text.
```
**04**
```
Very slow push-in on the man's face lit by the fridge light; a tear rolls down his cheek; the fridge light flickers. Keep the exact 2D cartoon art style, characters and colors of the image. No dialogue, no lip movement, no new text.
```
**05**
```
Slow push-in on the face; his eyes widen and his jaw clenches; the speed lines behind him rush outward. Keep the exact 2D cartoon art style, characters and colors of the image. No dialogue, no lip movement, no new text.
```
**06**
```
The man shrugs twice with open palms; the question marks float and bob around his head. The woman keeps her arms crossed. Keep the exact 2D cartoon art style, characters and colors of the image. No dialogue, no lip movement, no new text.
```
**07**
```
Dust falls from the calendar; the man shakes his head while crying, holding it with both hands. Slow push-in. Keep the exact 2D cartoon art style, characters and colors of the image. No dialogue, no lip movement, no new text.
```
**08**
```
The light bulb flashes on and the orange energy aura bursts outward; the man raises his fist higher. The woman steps back, surprised. Keep the exact 2D cartoon art style, characters and colors of the image. No dialogue, no lip movement, no new text.
```
**09**
```
The man takes a photo of his plate with the phone, a soft flash, then looks at the phone amazed; the woman leans in closer. Keep the exact 2D cartoon art style, characters and colors of the image. No dialogue, no lip movement, no new text.
```
**10**
```
The couple laughs and hugs tighter; Bia keeps the phone with the app screen steady and readable, only a slight tilt. Sparkles twinkle. Do not change or distort what is on the phone screen. Keep the exact 2D cartoon art style, characters and colors of the image. No dialogue, no lip movement, no new text.
```

## Dicas

- Uma ação por cena. Se o Flow inventar movimento demais, apague a parte do prompt que pede câmera e gere de novo.
- Cena que der errado 3 vezes: mande o print, ajusto o prompt.
- O espaço vazio da cena 9 existe para a edição pôr o Gommo. A cena 10 já tem a Home real na tela; não peça ao Flow para desenhar o app nem o mascote.
