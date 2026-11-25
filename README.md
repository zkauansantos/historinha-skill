# historinha-skill

Skill do Claude Code para fazer anúncio em formato "historinha meme": cartoon 2D gerado por IA, narrado em 1ª pessoa, com legenda palavra por palavra e o app entrando como a virada da história.

O formato é do [Thallis Ribeiro](https://x.com/thallisribeiro/status/2125207626229088654). Aqui está o processo que usei para adaptar para o Eatiary, transformado em skill.

## O que faz

- `gen.py`: folha de personagem, 10 cenas (9:16) e as falas, no Gemini.
- `screen.py`: cola o print real do seu app no celular desenhado (a IA gera a tela verde, o script encaixa na perspectiva).
- `build.py`: monta o MP4 1080x1920 com voz, legenda no tempo do whisper, caixa do gancho, mascote, selo da loja e trilha. Se tiver os clipes animados no Google Flow em `clips/`, usa no lugar das imagens.

## Instalar

```
git clone https://github.com/zkauansantos/historinha-skill
cp -r historinha-skill/historinha ~/.claude/skills/
```

Depois é só pedir no Claude Code: "faz uma historinha pro meu app". Detalhes em `historinha/SKILL.md`.

## Licença

MIT
