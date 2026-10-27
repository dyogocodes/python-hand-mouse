"""Download the official Google MediaPipe float16 hand landmark model."""
from pathlib import Path
import urllib.request

URL = 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
TARGET = Path(__file__).parent / 'models/hand_landmarker.task'


def main():
    if TARGET.is_file():
        print(f'Model already exists: {TARGET}')
        return
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    temporary = TARGET.with_suffix('.download')
    try:
        with urllib.request.urlopen(URL, timeout=60) as response, temporary.open('wb') as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        if temporary.stat().st_size < 1_000_000:
            raise RuntimeError('Unexpectedly small download; model was not installed.')
        temporary.replace(TARGET)
        print(f'Saved {TARGET}')
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
