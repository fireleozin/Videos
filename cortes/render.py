#!/usr/bin/env python3
"""Renderiza os cortes verticais (9:16) definidos em cuts.json.

Uso:
  python3 render.py                 # renderiza todos a partir de source/video.mp4
  python3 render.py 02_morango      # só os cortes cujo id começa com esse prefixo
  python3 render.py --test          # usa uma fonte sintética (valida o pipeline sem o vídeo)

Layout (1080x1920):
  - topo: facecam (crop do canto direito do vídeo original) 1080x720
  - base: gameplay (crop central) 1080x1200
  - gancho (título) nos primeiros segundos, legendas palavra a palavra na emenda
"""
import json, os, re, subprocess, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_W, OUT_H = 1080, 1920
CAM_H = 720                     # altura da facecam no vertical
GAME_H = OUT_H - CAM_H          # 1200
FPS = 60
CAPTION_Y = CAM_H + 215        # legendas logo abaixo do título/emenda, sobre o gameplay
TITLE_SECS = 3.2
FONT = "Inter Black"
JOIN_FADE = 0.025               # micro fade nas emendas (evita estalos)

def ts(t):
    t = max(t, 0)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def clean(word):
    w = word.upper()
    w = re.sub(r"[.,;:]+$", "", w)          # tira pontuação final (mantém ? ! ...)
    return w

def chunk_words(words, max_words=3, max_chars=16, gap=0.45):
    """Agrupa palavras em blocos curtos (estilo shorts)."""
    chunks, cur = [], []
    for i, wd in enumerate(words):
        if cur:
            prev = cur[-1]
            text_len = sum(len(x["w"]) + 1 for x in cur) + len(wd["w"])
            mw, mc = (12, 48) if wd["style"] == "npc" else (max_words, max_chars)
            if (len(cur) >= mw or text_len > mc or wd["t"] - prev["end"] > gap
                    or re.search(r"[.?!]$", prev["raw"])
                    or (prev["raw"].endswith(",") and len(cur) >= 2) or wd["style"] != prev["style"]):
                chunks.append(cur); cur = []
        cur.append(wd)
    if cur: chunks.append(cur)
    return chunks

def build_ass(cut, words_src, segs, path):
    # mapeia tempo da fonte -> tempo do corte
    offs, acc = [], 0.0
    for a, b in segs:
        offs.append((a, b, acc)); acc += b - a
    total = acc
    def m(t):
        for a, b, o in offs:
            if a - 0.3 <= t < b:
                return o + max(t - a, 0)
        return None
    def seg_end(t):
        for a, b, o in offs:
            if a - 0.3 <= t < b:
                return o + (b - a)
        return total
    words = []
    for item in words_src:            # [inicio, fim, palavra] em tempo da fonte
        t0, t1, raw = item[0], item[1], item[2]
        mt = m(t0)
        if mt is None or not raw: continue
        end = min(mt + max(t1 - t0, 0.1), seg_end(t0))
        words.append({"t": mt, "end": end, "raw": raw, "w": clean(raw), "style": "main"})
    words.sort(key=lambda x: x["t"])
    for i, wd in enumerate(words):      # nunca sobrepor a próxima palavra
        if i + 1 < len(words):
            wd["end"] = max(min(wd["end"], words[i + 1]["t"]), wd["t"] + 0.06)

    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {OUT_W}
PlayResY: {OUT_H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT},86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,1,0,1,7,4,5,40,40,0,1
Style: Npc,{FONT},64,&H00E0E0E0,&H00E0E0E0,&H00000000,&H96000000,-1,-1,0,0,100,100,0,0,1,5,3,5,60,60,0,1
Style: WM,Inter Black,58,&H9CFFFFFF,&H9CFFFFFF,&HC8000000,&HFF000000,-1,-1,0,0,100,100,4,0,1,2,0,8,0,0,0,1
Style: Title,{FONT},74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,3,18,0,8,50,50,70,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f"Dialogue: 0,{ts(0)},{ts(total + 1)},WM,,0,0,0,,{{\\an8\\pos({OUT_W//2},34)}}LM DOS CORTES"]
    # gancho / título (caixa preta, pop-in)
    title = cut["title"].replace("\n", "\\N")
    ev.append(f"Dialogue: 5,{ts(0)},{ts(TITLE_SECS)},Title,,0,0,0,,"
              f"{{\\an5\\pos({OUT_W//2},{CAM_H})\\3c&H000000&\\fscx80\\fscy80\\t(0,120,\\fscx104\\fscy104)\\t(120,220,\\fscx100\\fscy100)\\fad(0,250)}}{title}")
    HL = "&H00F7FF&"   # amarelo (BGR)
    chunks = chunk_words(words)
    for ci, ch in enumerate(chunks):
        start = ch[0]["t"]
        nxt = chunks[ci + 1][0]["t"] if ci + 1 < len(chunks) else total
        end = nxt if nxt - ch[-1]["end"] < 0.6 else min(ch[-1]["end"] + 0.35, nxt)
        if start < TITLE_SECS - 0.05 and ch[0]["style"] == "main":
            pass  # legenda e título convivem (título fica acima)
        style = "Npc" if ch[0]["style"] == "npc" else "Cap"
        for k, wd in enumerate(ch):
            w_end = ch[k + 1]["t"] if k + 1 < len(ch) else end
            if w_end <= wd["t"]: continue
            parts = []
            for j, x in enumerate(ch):
                if style == "Cap" and j == k:
                    parts.append(f"{{\\c{HL}\\fscx112\\fscy112}}{x['w']}{{\\c&HFFFFFF&\\fscx100\\fscy100}}")
                else:
                    parts.append(x["w"])
            text = " ".join(parts)
            pop = "\\fscx90\\fscy90\\t(0,80,\\fscx100\\fscy100)" if k == 0 else ""
            y = CAPTION_Y if style == "Cap" else CAPTION_Y + 10
            ev.append(f"Dialogue: 1,{ts(wd['t'])},{ts(w_end)},{style},,0,0,0,,{{\\an5\\pos({OUT_W//2},{y}){pop}}}{text}")
            if style == "Npc":
                break  # fala de NPC (tradução) aparece inteira, sem destaque palavra a palavra
        if style == "Npc":
            ev[-1] = re.sub(r"^(Dialogue: 1,[^,]+,)[^,]+", lambda mm: mm.group(1) + ts(end), ev[-1])
    with open(path, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(ev) + "\n")
    return total

def render(cfg, cut, src, outdir, test=False):
    # cada trecho: [inicio, fim] ou [inicio, fim, x_do_recorte_de_gameplay]
    gx = [s[2] if len(s) > 2 else cfg["gameplay"]["x"] for s in cut["segments"]]
    segs = [s[:2] for s in cut["segments"]]
    words = json.load(open(os.path.join(HERE, "captions", cut["id"] + ".json"), encoding="utf-8"))
    if test:  # remapeia tudo para uma fonte sintética curta e contínua
        acc, nsegs, shift = 0.0, [], []
        for a, b in segs:
            nsegs.append([acc, acc + b - a]); shift.append((a, b, acc - a)); acc += b - a
        nw = []
        for it in words:
            for a, b, d in shift:
                if a - 0.3 <= it[0] < b:
                    nw.append([it[0] + d, it[1] + d] + it[2:]); break
        segs, words = nsegs, nw
    ass = os.path.join(outdir, cut["id"] + ".ass")
    tmp_cap = {"title": cut["title"]}
    total = build_ass(tmp_cap, words, segs, ass)

    fc = cfg["facecam"]; gp = cfg["gameplay"]
    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for a, b in segs:
        args += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", src]
    n = len(segs)
    f = []
    for i, (a, b) in enumerate(segs):
        d = b - a
        f.append(f"[{i}:v]fps={FPS},setpts=PTS-STARTPTS,format=yuv420p,split=2[c1_{i}][c2_{i}]")
        f.append(f"[c1_{i}]crop={fc['w']}:{fc['h']}:{fc['x']}:{fc['y']},scale={OUT_W}:{CAM_H}:flags=lanczos,"
                 f"eq=contrast=1.03:saturation=1.08[cam{i}]")
        f.append(f"[c2_{i}]crop={gp['w']}:{gp['h']}:{gx[i]}:{gp['y']},scale={OUT_W}:{GAME_H}:flags=lanczos,"
                 f"eq=saturation=1.1[game{i}]")
        f.append(f"[cam{i}][game{i}]vstack=inputs=2[v{i}]")
        f.append(f"[{i}:a]aresample=48000,asetpts=PTS-STARTPTS,"
                 f"afade=t=in:st=0:d={JOIN_FADE},afade=t=out:st={max(d - JOIN_FADE, 0):.3f}:d={JOIN_FADE}[a{i}]")
    f.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")
    f.append(f"[cv]drawbox=x=0:y={CAM_H-3}:w={OUT_W}:h=6:color=black@0.9:t=fill,"
             f"ass='{ass}':fontsdir=/usr/share/fonts[vout]")
    f.append("[ca]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
    out = os.path.join(outdir, cut["id"] + ".mp4")
    args += ["-filter_complex", ";".join(f), "-map", "[vout]", "-map", "[aout]",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]
    subprocess.run(args, check=True)
    if cfg.get("endcard"):
        total = add_endcard(out, os.path.join(HERE, cfg["endcard"]), total)
    print(f"OK {out}  ({total:.1f}s)")
    return out

def add_endcard(video, card, dur, hold=3.5, fade=0.35):
    """Emenda a tela final (seguir/curtir) com dissolve + leve zoom de entrada."""
    tmp = video.replace(".mp4", ".tmp.mp4")
    off = dur - fade
    fc = (f"[0:v]fps={FPS},format=yuv420p,setpts=PTS-STARTPTS[a];"
          f"[1:v]format=yuv420p,scale=1188:2112,zoompan=z='max(1.1-0.1*on/18,1)':x='iw/2-iw/zoom/2':"
          f"y='ih/2-ih/zoom/2':d=1:s={OUT_W}x{OUT_H}:fps={FPS}[b];"
          f"[a][b]xfade=transition=fade:duration={fade}:offset={off:.3f}[v];"
          f"[0:a]asetpts=PTS-STARTPTS,afade=t=out:st={max(dur - 0.6, 0):.3f}:d=0.6[a0];"
          f"[a0][2:a]acrossfade=d={fade}[au]")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", video,
                    "-loop", "1", "-t", str(hold), "-framerate", str(FPS), "-i", card,
                    "-f", "lavfi", "-t", str(hold), "-i", "anullsrc=r=48000:cl=stereo",
                    "-filter_complex", fc, "-map", "[v]", "-map", "[au]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, video)
    return dur + hold - fade

def make_test_source(path, dur):
    # 1920x1080 com "facecam" (quadro azul) no lugar real e tom de áudio
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", f"testsrc2=s=1920x1080:r=60:d={dur}",
        "-f", "lavfi", "-i", f"sine=f=440:d={dur}",
        "-vf", "drawbox=x=1506:y=452:w=414:h=276:color=blue@0.8:t=fill,"
               "drawtext=font='Inter':text='FACECAM':x=1600:y=560:fontsize=48:fontcolor=white",
        "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-shortest", path], check=True)

def main():
    test = "--test" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    cfg = json.load(open(os.path.join(HERE, "cuts.json"), encoding="utf-8"))
    outdir = os.path.join(HERE, "test_output" if test else "output")
    os.makedirs(outdir, exist_ok=True)
    src = os.path.join(HERE, cfg["source"])
    if test:
        longest = max(sum(b - a for a, b in c["segments"]) for c in cfg["cuts"])
        src = os.path.join(outdir, "fake_source.mp4")
        make_test_source(src, int(longest) + 2)
    elif not os.path.exists(src):
        sys.exit(f"Vídeo fonte não encontrado: {src}")
    for cut in cfg["cuts"]:
        if only and not any(cut["id"].startswith(o) for o in only): continue
        render(cfg, cut, src, outdir, test)

if __name__ == "__main__":
    main()
