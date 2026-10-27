# Inference-time benchmark on the Jetson Orin Nano

Per-frame inference time of `models/prickly_pear_health3.pt`, reported in Table 4 of the
manuscript.

## Set-up

- **Board:** NVIDIA Jetson Orin Nano Developer Kit (8 GB), JetPack 6.2 (L4T R36.4.4),
  15 W power mode
- **Software:** Python 3.10.12, PyTorch 2.3.0 (CUDA 12.4), Ultralytics 8.4.51, OpenCV 4.11.0
- **Call:** `model(frame, imgsz=640)`, the same as in `scripts/yolo_fast.py`
- **Input:** 2 s of the recorded flight video (3840 × 2160, 29.97 fps) centred on each of
  the ten printed targets, 59 to 60 frames per target, 594 frames in total. The windows
  were cut from the original file and re-encoded with
  `ffmpeg -ss <t-1> -i DJI_0009.MP4 -t 2 -an -c:v libx264 -preset veryfast -crf 12 -pix_fmt yuv420p`.
  The flight video itself is not redistributed here because of its size.
- **Warm-up:** 50 frames, discarded

Target times (elapsed time in the video, s): S1 319.0, S2 351.5, S3 335.0, S4 282.5,
S5 291.0, S6 410.0, S7 391.0, S8 361.0, S9 300.0, S10 378.0.

## Runs

| Run | How frames are fed | Mean inference (ms) | s.d. |
|---|---|---|---|
| `burst` | back to back | 23.61 | 0.12 |
| `paced` | at the video rate, 29.97 fps | 23.09 | 1.41 |

In the `burst` run, pre-processing and post-processing add 7.17 ms and 3.91 ms on
average, for 34.69 ms per frame in total.

## Files

- `bench_inference.py`: the benchmark (`python bench_inference.py <model> <clips dir> <out dir> [burst|paced]`)
- `inference_times_burst.csv`, `inference_times_paced.csv`: one row per frame, with the
  Ultralytics `speed` dictionary (ms) and the number of boxes
- `environment_burst.json`, `environment_paced.json`: software and hardware state at run time

The latencies of the original 2025 field-trial run were not logged. These measurements
replace them, as stated in the manuscript.
