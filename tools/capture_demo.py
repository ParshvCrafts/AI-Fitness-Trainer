"""Record the README demo from the real app.

Starts app.py (eventlet, the production server path), opens it in headless
Chromium with the webcam replaced by a stock clip, clicks through calibration
and training like a user, and writes docs/assets/{demo.gif,calibration.png,training.png}.

The clip is Mixkit #21272 (free Mixkit licence, no attribution required); it is
downloaded into tools/.cache and not committed. The fake camera plays:
  0-9 s   still of the arm hanging down   (held pose for calibration step 1)
  9-18 s  still of the top of a curl      (held pose for calibration step 2)
  18 s+   the real clip, looped           (training)

Needs: ffmpeg on PATH, `pip install playwright` and `playwright install chromium`.
Run:   python tools/capture_demo.py
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'tools' / '.cache'
ASSETS = ROOT / 'docs' / 'assets'
CLIP_URL = 'https://assets.mixkit.co/videos/21272/21272-720.mp4'
PORT = 5055
W, H, FPS = 854, 480, 15
HOLD_S = 9
GIF_SECONDS = 10


def ffmpeg(*args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def build_fake_camera():
    CACHE.mkdir(parents=True, exist_ok=True)
    clip = CACHE / 'clip_21272.mp4'
    if not clip.exists():
        req = urllib.request.Request(CLIP_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as r, open(clip, 'wb') as f:
            shutil.copyfileobj(r, f)
    cam = CACHE / 'camera.y4m'
    scale = f'scale={W}:{H},fps={FPS},format=yuv420p'
    # Stills at 1.6 s (arm down, ~9 deg) and 2.4 s (top of curl, ~134 deg), then the clip twice.
    ffmpeg('-ss', '1.6', '-i', str(clip), '-ss', '2.4', '-i', str(clip), '-i', str(clip), '-i', str(clip),
           '-filter_complex',
           f'[0:v]trim=end_frame=1,loop={HOLD_S * 30}:1:0,setpts=N/30/TB,{scale}[a];'
           f'[1:v]trim=end_frame=1,loop={HOLD_S * 30}:1:0,setpts=N/30/TB,{scale}[b];'
           f'[2:v]{scale}[c];[3:v]{scale}[d];[a][b][c][d]concat=n=4:v=1[out]',
           '-map', '[out]', '-an', str(cam))
    return cam


def wait_for_port(port, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        with socket.socket() as s:
            if s.connect_ex(('127.0.0.1', port)) == 0:
                return
        time.sleep(0.3)
    raise RuntimeError(f'server did not open port {port}')


def main():
    cam = build_fake_camera()
    ASSETS.mkdir(parents=True, exist_ok=True)
    frames = CACHE / 'frames'
    shutil.rmtree(frames, ignore_errors=True)
    frames.mkdir()

    server = subprocess.Popen([sys.executable, 'app.py'], cwd=ROOT, env={**os.environ, 'PORT': str(PORT)})
    try:
        wait_for_port(PORT)
        with sync_playwright() as p:
            browser = p.chromium.launch(args=[
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
                f'--use-file-for-fake-video-capture={cam}',
            ])
            size = {'width': 1280, 'height': 860}
            context = browser.new_context(viewport=size, record_video_dir=str(frames), record_video_size=size)
            page = context.new_page()
            video_t0 = time.time()
            page.goto(f'http://127.0.0.1:{PORT}/')
            page.evaluate("""() => {
                window.__log = {done: null, errors: [], ms: [], counts: []};
                socket.on('calibration_done', d => window.__log.done = d);
                socket.on('calibration_error', d => window.__log.errors.push(d));
                socket.on('frame_processed', d => { window.__log.ms.push(d.server_ms); window.__log.counts.push(d.count); });
            }""")
            page.click('#get-started-btn')
            page.click('.arm-btn[data-arm="left"]')
            t0 = time.time()
            page.click('#start-camera-btn')
            page.wait_for_selector('#calibration-screen.active')

            page.wait_for_timeout(500)
            page.click('#calibrate-min-btn')  # arm-down still is on camera until t0 + 9 s
            page.wait_for_function("!document.querySelector('#calibrate-max-btn').disabled", timeout=15000)
            page.wait_for_timeout(max(0, int((t0 + HOLD_S + 0.6 - time.time()) * 1000)))
            page.click('#calibrate-max-btn')  # curl still is on camera until t0 + 18 s
            page.wait_for_timeout(3500)
            page.locator('.calibration-container').screenshot(path=str(ASSETS / 'calibration.png'))
            page.wait_for_function('window.__log.done || window.__log.errors.length', timeout=15000)
            log = page.evaluate('window.__log')
            if not log['done']:
                raise RuntimeError(f'calibration failed: {log["errors"]}')
            print('calibrated', log['done'])

            # Start training just before the clip begins at t0 + 18 s.
            page.wait_for_timeout(max(0, int((t0 + 2 * HOLD_S - 0.3 - time.time()) * 1000)))
            page.click('#complete-calibration-btn')
            page.evaluate('window.__log.ms = []; window.__log.counts = []')
            target = page.locator('.training-container')
            box = target.bounding_box()
            start = time.time() - video_t0 + 0.7  # skip the screen transition
            page.wait_for_timeout(GIF_SECONDS * 1000)
            target.screenshot(path=str(ASSETS / 'training.png'))
            log = page.evaluate('window.__log')
            video = page.video.path()
            context.close()
            browser.close()
    finally:
        server.terminate()
        server.wait(timeout=10)

    ms = sorted(log['ms'])
    stats = {
        'reps_counted': max(log['counts'] or [0]),
        'frames_processed': len(ms),
        'server_ms_median': ms[len(ms) // 2] if ms else None,
        'server_ms_p90': ms[int(len(ms) * 0.9)] if ms else None,
        'seconds': GIF_SECONDS,
    }
    print(json.dumps(stats, indent=2))
    (CACHE / 'capture_stats.json').write_text(json.dumps(stats, indent=2))

    crop = f"crop={int(box['width'])}:{int(box['height'])}:{int(box['x'])}:{int(box['y'])}"
    ffmpeg('-ss', f'{start:.2f}', '-t', str(GIF_SECONDS), '-i', str(video), '-vf',
           f'{crop},fps=10,scale=560:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=80:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle',
           '-loop', '0', str(ASSETS / 'demo.gif'))
    print('wrote', ASSETS / 'demo.gif', round((ASSETS / 'demo.gif').stat().st_size / 1e6, 2), 'MB')


if __name__ == '__main__':
    main()
