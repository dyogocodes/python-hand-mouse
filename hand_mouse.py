"""Webcam hand mouse using MediaPipe Tasks. Starts paused."""
import argparse
from pathlib import Path
import sys
import time

from gestures import PinchClick, map_point, pinch_ratio


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--model', type=Path, default=Path(__file__).parent / 'models/hand_landmarker.task')
    parser.add_argument('--dry-run', action='store_true', help='Track gestures without desktop input')
    parser.add_argument('--smoothing', type=float, default=0.30, help='0 < value <= 1; larger is faster')
    parser.add_argument('--margin', type=float, default=0.15, help='Active camera border, 0 <= value < 0.45')
    args = parser.parse_args()
    if not 0 < args.smoothing <= 1 or not 0 <= args.margin < 0.45:
        parser.error('Invalid smoothing or margin')
    if not args.model.is_file():
        parser.error(f'Model missing: {args.model}. Run python download_model.py first.')
    return args


def main():
    args = arguments()
    import cv2
    import mediapipe as mp
    import numpy as np
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision

    mouse = None
    if not args.dry_run:
        import pyautogui as mouse
        mouse.FAILSAFE = True
        screen_w, screen_h = mouse.size()
    else:
        screen_w, screen_h = 1920, 1080  # Virtual display for preview only.

    options = vision.HandLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(args.model)),
        running_mode=vision.RunningMode.VIDEO, num_hands=1,
        min_hand_detection_confidence=0.6, min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6)
    camera = cv2.VideoCapture(args.camera)
    active, smooth, previous_stamp = False, None, -1
    click = PinchClick()
    window = 'DyogoCodes Hand Mouse'
    try:
        if not camera.isOpened():
            raise RuntimeError('Cannot open webcam. Check permissions or try --camera 1.')
        cv2.namedWindow(window)
        with vision.HandLandmarker.create_from_options(options) as tracker:
            while True:
                ok, frame = camera.read()
                if not ok:
                    raise RuntimeError('Webcam stopped delivering frames.')
                frame = cv2.flip(frame, 1)
                h, w = frame.shape[:2]
                rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                stamp = max(previous_stamp + 1, time.monotonic_ns() // 1_000_000)
                previous_stamp = stamp
                result = tracker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), stamp)
                now = time.monotonic()
                status = 'PAUSED'
                if result.hand_landmarks:
                    points = result.hand_landmarks[0]
                    for point in points:
                        cv2.circle(frame, (int(point.x * w), int(point.y * h)), 3, (0, 220, 120), -1)
                    ratio = pinch_ratio(points, w, h)
                    if active:
                        target = map_point(points[8].x, points[8].y, screen_w, screen_h, args.margin)
                        smooth = target if smooth is None else tuple(
                            old + args.smoothing * (new - old) for old, new in zip(smooth, target))
                        fired = click.update(ratio, now)
                        # Freeze cursor during a pinch to reduce click-target drift.
                        if mouse is not None:
                            if ratio >= click.release:
                                mouse.moveTo(round(smooth[0]), round(smooth[1]))
                            if fired:
                                mouse.click()
                        status = 'CLICK' if fired else f'ACTIVE | pinch {ratio:.2f}'
                else:
                    # Disarm after hand loss. Explicit Space is needed to resume.
                    if active:
                        active = False
                    click.reset()
                    smooth = None
                    status = 'NO HAND | press Space when hand returns'
                cv2.rectangle(frame, (int(w * args.margin), int(h * args.margin)),
                              (int(w * (1 - args.margin)), int(h * (1 - args.margin))), (200, 160, 0), 1)
                mode = 'DRY RUN' if args.dry_run else 'DESKTOP'
                cv2.putText(frame, f'{mode} | {status}', (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
                cv2.putText(frame, 'Space: start/pause | Q/Esc: quit', (12, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
                cv2.imshow(window, frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord('q')) or cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
                    break
                if key == ord(' '):
                    active = not active
                    click.reset()
                    smooth = None
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print(f'Hand Mouse stopped: {exc}', file=sys.stderr)
        sys.exit(1)
