"""Takes the newest Empire Maps Short (from the empire-maps-pipeline 'qa' branch, read only) and adds a small
YouTube banner for Facebook and Instagram Reels. The Empire Maps repo and YouTube channel are not touched."""
import json, os, re, subprocess, urllib.request
from PIL import Image, ImageDraw, ImageFont

SRC = "https://raw.githubusercontent.com/shehrozimtiaz0797-7/empire-maps-pipeline/qa/"
HANDLE = "@empiremaps1857"
os.makedirs("out", exist_ok=True)
os.makedirs("tmp", exist_ok=True)
for f in ("final.mp4", "script.json", "pipeline.log"):
    urllib.request.urlretrieve(SRC + f, "tmp/" + f)
script = json.load(open("tmp/script.json"))
log = open("tmp/pipeline.log", encoding="utf-8", errors="ignore").read()
m = re.findall(r"https://youtube\.com/shorts/[A-Za-z0-9_-]+", log)
yt = m[-1] if m else "https://youtube.com/" + HANDLE

probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", "tmp/final.mp4"], capture_output=True, text=True).stdout.strip().split(",")
W, H = int(probe[0]), int(probe[1])

# banner: red YouTube-style pill at the very top, outside the title and caption areas
bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
f1 = ImageFont.truetype(bold, int(W * 0.028))
text = f"More maps on YouTube  {HANDLE}"
tw = d.textlength(text, font=f1)
ph = int(W * 0.06)
pw = int(tw + ph * 1.6)
x0 = (W - pw) // 2
y0 = int(H * 0.012)
d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=ph // 2, fill=(230, 33, 23, 235))
# play triangle
cx, cy, r = x0 + ph * 0.62, y0 + ph / 2, ph * 0.22
d.polygon([(cx - r * 0.7, cy - r), (cx - r * 0.7, cy + r), (cx + r, cy)], fill=(255, 255, 255, 255))
d.text((x0 + ph * 1.05, y0 + ph / 2), text, font=f1, fill=(255, 255, 255, 255), anchor="lm")
img.save("tmp/banner.png")

# end card (2.5 s): last frame blurred + "watch more on YouTube"
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "tmp/final.mp4"], capture_output=True, text=True).stdout)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-sseof", "-0.2", "-i", "tmp/final.mp4", "-frames:v", "1", "tmp/last.png"], check=True)
from PIL import ImageFilter
card = Image.open("tmp/last.png").convert("RGB").filter(ImageFilter.GaussianBlur(18)).convert("RGBA")
card = Image.alpha_composite(card, Image.new("RGBA", (W, H), (0, 0, 0, 150)))
cd = ImageDraw.Draw(card)
big = ImageFont.truetype(bold, int(W * 0.075))
mid = ImageFont.truetype(bold, int(W * 0.05))
cd.text((W / 2, H * 0.36), "WANT MORE", font=big, fill=(255, 255, 255), anchor="mm")
cd.text((W / 2, H * 0.36 + W * 0.1), "EMPIRE MAPS?", font=big, fill=(255, 214, 90), anchor="mm")
bw, bh = int(W * 0.62), int(W * 0.14)
bx, by = (W - bw) // 2, int(H * 0.52)
cd.rounded_rectangle((bx, by, bx + bw, by + bh), radius=bh // 2, fill=(230, 33, 23))
tx, ty, tr = bx + bh * 0.6, by + bh / 2, bh * 0.2
cd.polygon([(tx - tr * 0.7, ty - tr), (tx - tr * 0.7, ty + tr), (tx + tr, ty)], fill=(255, 255, 255))
cd.text((bx + bh * 1.0, by + bh / 2), "YouTube", font=mid, fill=(255, 255, 255), anchor="lm")
cd.text((W / 2, by + bh + W * 0.09), HANDLE, font=mid, fill=(255, 255, 255), anchor="mm")
cd.text((W / 2, by + bh + W * 0.17), "New map every day", font=ImageFont.truetype(bold, int(W * 0.038)), fill=(220, 220, 220), anchor="mm")
card.convert("RGB").save("tmp/endcard.png")

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "tmp/final.mp4", "-i", "tmp/banner.png", "-loop", "1", "-t", "2.5", "-i", "tmp/endcard.png",
                "-f", "lavfi", "-t", "2.5", "-i", "anullsrc=r=48000:cl=stereo",
                "-filter_complex",
                "[0:v][1:v]overlay=0:0,fps=30,format=yuv420p,setsar=1[a];[2:v]scale=%d:%d,fps=30,format=yuv420p,setsar=1[b];"
                "[0:a]aresample=48000,aformat=channel_layouts=stereo[a1];[3:a]aformat=channel_layouts=stereo[a2];"
                "[a][a1][b][a2]concat=n=2:v=1:a=1[v][au]" % (W, H),
                "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "out/reel.mp4"], check=True)
tags = " ".join("#" + re.sub(r"[^A-Za-z0-9]", "", t) for t in (script.get("tags") or [])[:6] if re.sub(r"[^A-Za-z0-9]", "", t))
meta = {
    "title": script.get("title", ""),
    "youtube_url": yt,
    "caption": f"{script.get('title', '')}\n\n▶ Watch more empire maps on YouTube: {HANDLE}\n\n#history #maps #empire #historymaps {tags}\n\nMap borders: historical-basemaps (A. Ourednik). Narration: AI voice.",
    "fb_description": f"▶ Full video on YouTube: {yt}\n\n{script.get('title', '')}\n\n🔔 Subscribe for a new empire map every day: https://youtube.com/{HANDLE}?sub_confirmation=1\n\n#history #maps #empire\n\nMap borders: historical-basemaps (A. Ourednik). Narration: AI voice.",
}
json.dump(meta, open("out/meta.json", "w"), indent=1, ensure_ascii=False)
print(json.dumps(meta, indent=1, ensure_ascii=False))
