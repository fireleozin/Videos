# Cortes virais: "UM GOLPE DIFERENTE! - GTA 6 - Parte 10" (alanzoka)

Fonte: https://youtu.be/86msElVeQiA (2h19min59s). A transcrição completa, com marcação de tempo, está em `transcricao_completa.txt`.

Escolhi os 5 cortes depois de ler a live inteira. Os critérios foram humor espontâneo, reação genuína, situação absurda, gancho nos primeiros segundos e desfecho claro. Cada corte junta só os trechos com fala ou reação e tira as pausas e a navegação no jogo.

| # | Corte | Duração | Trechos do original | Por que viraliza |
|---|-------|---------|---------------------|------------------|
| 1 | **O Mário se empolgou no palco** | ~60s | 1:43:24 → 1:47:32 (6 trechos) | Cena da boate de strip. Um NPC da plateia ("Mário") sobe no palco, arranca a roupa e passa a mão na Lucia, e o alan grita "Ô MÁRIO!" sem parar. É o momento mais engraçado da live, com bordão repetível e fechamento ("o Mário se empolga, pô"). |
| 2 | **Ele não usa drogas… só come morango** | ~52s | 0:59:14 → 1:01:08 (6 trechos) | O fazendeiro que fabrica droga oferece "morangos com fertilizante". A frase "Só não uso drogas, mas fruta eu gosto" seguida de "aumentou alguma coisa minha" e "que morangaço" funciona como duplo sentido e vira comentário fácil. |
| 3 | **Gastou tudo tunando o carro… e bateu** | ~61s | 0:49:35 → 0:52:19 + 1:33:31 | Arco completo: gasta todo o dinheiro (do "bebê") no carro, bate em 2 minutos, o carro solta fumaça e depois vem o arrependimento: "devia ter investido no fundo do meu filho". Narrativa de causa e consequência que segura a retenção até o fim. |
| 4 | **O policial bateu nele… e ele que foi procurado** | ~57s | 1:15:56 → 1:17:17 | Indignação genuína com a injustiça do jogo: "O policial bate em mim e EU que sou perseguido". Gera identificação e debate nos comentários sobre a IA da polícia do GTA 6. |
| 5 | **"Não sou psicopata, sou profissional"** | ~53s | 0:16:25 + 1:11:04 + 2:08:05 | Compilação com setup e payoff: ele explica o "perfil criminal" (profissional, não psicopata) e depois a Lucia metralha gente duas vezes, e ele insiste: "ela não é psicopata, ela é profissional". Tem ironia e curiosidade sobre essa mecânica nova do GTA 6. |

Reservas: "Farol Matrix" (0:01:37–0:02:06), curiosidade técnica do GTA 6 que funciona bem com público gamer. "10 minutos no TikTok" (2:18:50–2:19:43) e "Esse cara não é o pai, é um jacaré" (2:17:07).

Tempos exatos de cada trecho: `cuts.json`.

## Formato de saída

- 1080x1920 (9:16), 60 fps, H.264 com CRF 19, áudio AAC 192k normalizado a -14 LUFS (padrão TikTok/Reels/Shorts).
- Layout: **facecam em cima** (1080x720, recortada do canto direito do vídeo original) e **gameplay embaixo** (1080x1200, recorte central). Assim a reação do streamer e o jogo aparecem ao mesmo tempo.
- **Gancho** em caixa preta nos primeiros ~3s.
- **Legendas dinâmicas** em maiúsculas, fonte Inter Black, blocos de até 3 palavras e a palavra falada destacada em amarelo com "pop". Palavrões aparecem censurados como `#@%!`.
- Falas dos NPCs em inglês ganham **tradução em PT** em itálico (corte 4).
- Micro-fades de 25ms em cada emenda para não haver estalos no áudio.

## Como renderizar

```bash
# 1. coloque o vídeo original (1080p) em cortes/source/video.mp4
yt-dlp -f "299+140" -o "cortes/source/video.%(ext)s" "https://youtu.be/86msElVeQiA"
# 2. renderize
cd cortes && python3 render.py          # todos -> output/
python3 render.py 02                    # só um corte
python3 render.py --test                # valida o pipeline com vídeo sintético
```

Antes de publicar, confira dois pontos no vídeo real:
1. A posição da facecam (`facecam` em `cuts.json`), que medi pelas miniaturas do YouTube: x=1506, y=452, 414x276.
2. A sincronia fina das legendas. Os tempos por palavra vêm das legendas automáticas do YouTube, e revisei o texto à mão.

## Textos para publicar

**1. Mário**
> O MÁRIO NÃO TEM LIMITES 😭🔥 #gta6 #alanzoka #gtavi #games #humor #fyp

**2. Morango**
> ele só come fruta, tá? 🍓👀 #gta6 #alanzoka #gtavi #gameplay #humor #fyp

**3. Carro**
> o fundo do filho virou rodão aro 19 💸🚗 #gta6 #alanzoka #gtavi #carros #humor #fyp

**4. Polícia**
> a polícia do GTA 6 é muito injusta 😤🚓 #gta6 #alanzoka #gtavi #gaming #fyp

**5. Psicopata**
> ela é PROFISSIONAL, tá? 🔫😇 #gta6 #alanzoka #gtavi #lucia #humor #fyp

Bilibili (título em chinês sugerido): `GTA6：她不是疯子，她是专业的 😂 | alanzoka`
