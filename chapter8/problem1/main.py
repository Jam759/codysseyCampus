import cv2
import os
from datetime import datetime


VIDEO_PATH = 'C:\\Users\\3379p\\OneDrive\\Desktop\\vscode\\codysseyCampus\\data\\pr7\\sample_10s_video.mp4'
IMAGE_PATHS = [
    'C:\\Users\\3379p\\OneDrive\\Desktop\\vscode\\codysseyCampus\\data\\pr7\\default.png',
    'C:\\Users\\3379p\\OneDrive\\Desktop\\vscode\\codysseyCampus\\data\\pr7\\quiz.png',
]

OUTPUT_DIR = 'C:\\Users\\3379p\\OneDrive\\Desktop\\vscode\\codysseyCampus\\data\\pr7\\output'
CAMERA_INDEX = 0
FRAME_DELAY = 33

ESC_KEY = 27
CTRL_Z_KEY = 26
CTRL_X_KEY = 24
CTRL_C_KEY = 3

WIDTH = 640
HEIGHT = 480


def make_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def make_time_filename(extension):
    now = datetime.now()
    filename = now.strftime('%Y%m%d_%H-%M-%S')
    return os.path.join(OUTPUT_DIR, f'{filename}.{extension}')


def show_images():
    for image_path in IMAGE_PATHS:
        image = cv2.imread(image_path)

        if image is None:
            print(f'이미지 파일을 열 수 없습니다: {image_path}')
            continue

        cv2.imshow('image', image)
        cv2.waitKey(0)
        cv2.destroyWindow('image')


def play_video():
    capture = cv2.VideoCapture(VIDEO_PATH)

    if not capture.isOpened():
        print(f'동영상 파일을 열 수 없습니다: {VIDEO_PATH}')
        return

    while True:
        ret, frame = capture.read()

        if not ret:
            break

        cv2.imshow('video', frame)

        key = cv2.waitKey(FRAME_DELAY) & 0xFF
        if key == ESC_KEY:
            break

    capture.release()
    cv2.destroyWindow('video')


def show_camera():
    capture = cv2.VideoCapture(CAMERA_INDEX)

    if not capture.isOpened():
        print('카메라를 열 수 없습니다.')
        return

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    while True:
        ret, frame = capture.read()

        if not ret:
            print('카메라 영상을 읽을 수 없습니다.')
            break

        cv2.imshow('camera', frame)

        key = cv2.waitKey(FRAME_DELAY) & 0xFF
        if key == ESC_KEY:
            break

    capture.release()
    cv2.destroyWindow('camera')


def create_video_writer(frame, codec):
    height, width = frame.shape[:2]

    if codec == 'mp4v':
        extension = 'mp4'
    else:
        extension = 'avi'

    output_path = make_time_filename(extension)
    fourcc = cv2.VideoWriter_fourcc(*codec)

    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        30.0,
        (width, height)
    )

    return writer, output_path


def play_video_with_shortcuts():
    make_output_dir()

    capture = cv2.VideoCapture(VIDEO_PATH)

    if not capture.isOpened():
        print(f'동영상 파일을 열 수 없습니다: {VIDEO_PATH}')
        return

    writer = None
    is_recording = False
    record_path = None

    while True:
        ret, frame = capture.read()

        if not ret:
            break

        cv2.imshow('video control', frame)

        if is_recording and writer is not None:
            writer.write(frame)

        key = cv2.waitKey(FRAME_DELAY) & 0xFF

        if key == ESC_KEY:
            break

        if key == CTRL_Z_KEY:
            image_path = make_time_filename('jpg')
            cv2.imwrite(image_path, frame)
            print(f'이미지 캡쳐 완료: {image_path}')

        elif key == CTRL_X_KEY:
            if not is_recording:
                writer, record_path = create_video_writer(frame, 'mp4v')
                is_recording = True
                print(f'녹화 시작: {record_path}')

        elif key == CTRL_C_KEY:
            if is_recording:
                is_recording = False

                if writer is not None:
                    writer.release()
                    writer = None

                print(f'녹화 중지: {record_path}')

    if writer is not None:
        writer.release()

    capture.release()
    cv2.destroyWindow('video control')


def main():

    show_images()

    # 보너스 과제
    # play_video()
    # show_camera()

    play_video_with_shortcuts()


if __name__ == '__main__':
    main()