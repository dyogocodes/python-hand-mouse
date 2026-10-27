# Python Hand Mouse 🖐️🐍

A DyogoCodes webcam project that implements hand tracking, cursor movement and pinch-to-click with Python, MediaPipe Tasks, OpenCV and PyAutoGUI.

**Status: implemented prototype, awaiting a real webcam and desktop validation.** Automated gesture-logic tests and Python syntax checks pass. End-to-end camera tracking, OS permissions, cursor accuracy and clicking have not been verified on physical hardware. This is source code you can run, not a packaged executable or a proven mouse replacement.

## What the code implements

- One-hand tracking through the MediaPipe Hand Landmarker Tasks API.
- Mirrored webcam preview with landmarks and an adjustable active region.
- Smoothed index-fingertip mapping to the primary display.
- Left click by pinching thumb and index finger, with dwell, hysteresis and cooldown.
- Cursor movement freezes during a pinch to reduce target drift.
- Starts paused; tracking loss pauses control and requires explicit resumption.
- Dry-run mode that never imports or calls desktop mouse control.
- Quit controls, camera cleanup and PyAutoGUI's enabled corner failsafe.

Right click, drag, scrolling, multiple monitors and a graphical installer are not implemented.

## Quick start

Use a local desktop with a webcam and **Python 3.11 or 3.12** as the initial setup target. Dependency installation and runtime compatibility still need local verification; this does not run in a browser or a headless notebook.

```bash
git clone https://github.com/dyogocodes/python-hand-mouse.git
cd python-hand-mouse
python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install and download the official Google model:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python download_model.py
python hand_mouse.py --dry-run
```

The model download requires internet access and is saved in `models/`. The model is not bundled or covered by a project-specific license; see Google's model documentation for its terms. The downloader uses the versioned float16/1 model URL, HTTPS, a timeout and an atomic rename. It does not verify a published checksum.

Start with the preview. Once tracking looks correct, quit and enable real desktop input:

```bash
python hand_mouse.py
```

## Controls

Keep the preview window focused for keyboard controls.

| Action | Control |
| --- | --- |
| Start or pause | Space |
| Move cursor | Move your index fingertip with thumb and index separated |
| Left click | Briefly pinch thumb and index, then separate before another click |
| Stop after tracking loss | Automatic pause; bring the hand back and press Space |
| Quit | Q, Escape, close preview window or Ctrl+C in terminal |
| Emergency stop | Move your physical mouse to a primary-screen corner |

Open thumb and index after enabling control to arm clicking. A held pinch triggers only one click. Cursor coordinates stay just inside the screen edges so the application does not intentionally enter failsafe corners. The physical mouse can still trigger the failsafe. No mouse button is held down by this application.

## Options

```bash
python hand_mouse.py --camera 1
python hand_mouse.py --smoothing 0.2 --margin 0.20
python hand_mouse.py --model /path/to/hand_landmarker.task --dry-run
python hand_mouse.py --help
```

Lower smoothing values reduce jitter but add lag. The margin defines the central camera region mapped to the screen. Pinch defaults live in `gestures.py`: close ratio 0.30, release ratio 0.50, dwell 80 ms, cooldown 350 ms. Distance is normalized by palm width using aspect-correct image coordinates. These are starting values, not calibrated accuracy guarantees.

## Platform notes and troubleshooting

- **macOS:** grant Camera permission to your terminal or IDE. Real mouse input may also require Accessibility permission. Restart the terminal/IDE after changing permissions. Retina coordinate behavior requires local testing.
- **Windows:** allow desktop-app camera access, close other webcam apps and try `--camera 1` if needed.
- **Linux:** use an X11 desktop for the initial test. Wayland input restrictions can prevent PyAutoGUI control. A missing tkinter dependency may require your distribution's `python3-tk` package.
- **Model missing:** run `python download_model.py` or pass `--model` for a manually downloaded Hand Landmarker `.task` file.
- **Dependency install fails:** use a fresh Python 3.11/3.12 environment and check whether MediaPipe provides a wheel for your OS and architecture. Avoid installing multiple OpenCV distributions in the same environment.
- **Jitter / missed pinches:** improve lighting, keep one hand in frame and adjust the gesture thresholds. Accuracy and latency vary with the camera and computer.
- **Stops at a corner:** this is the enabled PyAutoGUI failsafe. Relaunch after moving the physical cursor away from the corner.

Frames are processed locally. This application contains no frame recording or upload code. Installing dependencies and downloading the model require network access.

## Validation

Run from the repository root; these tests need no webcam or third-party packages:

```bash
python -m unittest discover -s tests -v
python -m py_compile hand_mouse.py gestures.py download_model.py
```

Automated coverage: screen mapping and bounds, aspect-correct pinch ratios, click arming, dwell interruption, cooldown and reset behavior. Passing these checks does not validate model loading or desktop integration.

Before describing this as a demonstrated working build:

- [ ] Install dependencies and load the model successfully on the target OS; record versions.
- [ ] Show live landmarks responding to a real hand in dry-run mode.
- [ ] Record continuous hand and desktop views proving cursor movement without physical mouse input.
- [ ] Demonstrate a pinch clicking a harmless desktop target, one click per pinch.
- [ ] Check pause, hand loss, quit and physical-mouse failsafe behavior.

Record OS, Python/dependency versions, webcam, lighting and any limitations with the result. No hardware validation has been recorded yet.

## Publication wording

Suggested hook: **Can your hand become your mouse? Here's a Python prototype to test.**

Suggested caption: **The source now implements hand tracking, cursor movement and pinch-to-click. Automated gesture tests pass; webcam and desktop behavior still need local validation. Try dry-run mode first.**

Existing silent TikTok/YouTube concept previews are not demonstrations of this implementation and are not narrated finished tutorials. Adding code does not change what those videos prove.

## References

- [MediaPipe Hand Landmarker Python guide](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python)
- [Hand Landmarker models](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models)
- [PyAutoGUI documentation and failsafe](https://pyautogui.readthedocs.io/en/latest/)

Created for [DyogoCodes](https://github.com/dyogocodes). Explore, test and share your results.
