"""Build docs/assets/social-preview.png (1280x640) from the captured training screenshot.

Run tools/capture_demo.py first. Upload the result in GitHub: Settings -> General -> Social preview.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ASSETS = Path(__file__).resolve().parents[1] / 'docs' / 'assets'
W, H = 1280, 640
BG = (10, 14, 39)
CYAN = (0, 212, 255)


def font(name, size):
    for path in (f'C:/Windows/Fonts/{name}', f'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


img = Image.new('RGB', (W, H), BG)
shot = Image.open(ASSETS / 'training.png').convert('RGB')
# The person and the tracked arm from the video panel, scaled to the card height.
video = shot.crop((int(shot.width * 0.30), 0, int(shot.width * 0.69), int(shot.height * 0.70)))
video = video.resize((int(video.width * H / video.height), H), Image.LANCZOS)
x0 = W - video.width
img.paste(video, (x0, 0))

# Fade the left edge of the photo into the background (no hard seam).
fade = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(fade)
for i in range(160):
    d.line([(x0 + i, 0), (x0 + i, H)], fill=int(255 * (1 - i / 160) ** 1.6))
d.rectangle([0, 0, x0, H], fill=255)
img = Image.composite(Image.new('RGB', (W, H), BG), img, fade.filter(ImageFilter.GaussianBlur(4)))

d = ImageDraw.Draw(img)
d.text((64, 150), 'AI Fitness Trainer', font=font('segoeuib.ttf', 64), fill=(255, 255, 255))
d.text((64, 240), 'Bicep-curl rep counter in the browser', font=font('segoeui.ttf', 34), fill=CYAN)
lines = ['MediaPipe Pose + Flask-SocketIO', 'Two-pose calibration, hysteresis counting', 'Tested end to end on real frames']
for i, line in enumerate(lines):
    y = 330 + i * 52
    d.ellipse([66, y + 12, 80, y + 26], fill=CYAN)
    d.text((96, y), line, font=font('segoeui.ttf', 28), fill=(214, 222, 240))
d.text((64, 560), 'github.com/ParshvCrafts/AI-Fitness-Trainer', font=font('segoeui.ttf', 22), fill=(130, 140, 170))

out = ASSETS / 'social-preview.png'
img.save(out, optimize=True)
print(out, round(out.stat().st_size / 1e6, 2), 'MB')
