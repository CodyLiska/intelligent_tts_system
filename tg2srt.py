from textgrid import TextGrid

def fmt(t):
    ms = int(round(float(t)*1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

tg = TextGrid.fromFile(r"aligned\utt_0001.TextGrid")
tier = tg[0]  # first tier (usually words)
start = float(tier.minTime)
end   = float(tier.maxTime)

with open("input.txt","r",encoding="utf-8") as f:
    text = " ".join([ln.strip() for ln in f if ln.strip()])

with open("out.srt","w",encoding="utf-8") as srt:
    srt.write(f"1\n{fmt(start)} --> {fmt(end)}\n{text}\n\n")

print("Wrote out.srt")
