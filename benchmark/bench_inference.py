# Inference-time benchmark of prickly_pear_health3.pt on the Jetson Orin Nano.
# Replays 2 s of the field video (DJI_0009.MP4, 3840x2160) around each of the ten
# printed targets and calls the model exactly as scripts/yolo_fast.py does:
# model(frame, imgsz=640). Ultralytics' per-frame speed dict is logged unchanged.
import csv, json, platform, subprocess, sys, time
import cv2, torch, ultralytics
from ultralytics import YOLO

MODEL, CLIPS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
# 'paced': frames are fed at the video rate (29.97 fps), as a live stream delivers them;
# 'burst': back to back, which keeps the GPU at its highest clock
MODE = sys.argv[4] if len(sys.argv) > 4 else 'burst'
PERIOD = 1001 / 30000
TARGETS = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10']
WARMUP = 50

def sh(cmd):
    try: return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
    except Exception as e: return str(e)

model = YOLO(MODEL)
model.to('cuda')

def frames(name):
    cap = cv2.VideoCapture(f'{CLIPS}/{name}.mp4')
    while True:
        ok, f = cap.read()
        if not ok: break
        yield f
    cap.release()

# warm-up, not logged
n = 0
for f in frames('S1'):
    model(f, imgsz=640, verbose=False); n += 1
    if n >= WARMUP: break

rows = []
for name in TARGETS:
    frs = list(frames(name))
    for i, f in enumerate(frs):
        t0 = time.perf_counter()
        r = model(f, imgsz=640, verbose=False)[0]
        if MODE == 'paced':
            time.sleep(max(0.0, PERIOD - (time.perf_counter() - t0)))
        rows.append({'target': name, 'frame': i, 'boxes': len(r.boxes),
                     **{k: round(v, 3) for k, v in r.speed.items()}})

with open(f'{OUT}/inference_times_{MODE}.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

env = {'date': time.strftime('%Y-%m-%d %H:%M:%S %z'), 'model': MODEL,
       'board': sh('cat /proc/device-tree/model').rstrip('\x00'),
       'l4t': sh('head -1 /etc/nv_tegra_release'), 'power_mode': sh('nvpmodel -q 2>/dev/null | head -1'),
       'python': platform.python_version(), 'torch': torch.__version__, 'cuda': torch.version.cuda,
       'ultralytics': ultralytics.__version__, 'opencv': cv2.__version__, 'imgsz': 640,
       'input': '3840x2160 frames, 2 s window around each target', 'warmup_frames': WARMUP, 'mode': MODE,
       'loadavg_before': open('/proc/loadavg').read().strip()}
json.dump(env, open(f'{OUT}/environment_{MODE}.json', 'w'), indent=1)
print(json.dumps(env, indent=1))
