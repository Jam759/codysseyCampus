import os

import cv2
import numpy as np
from matplotlib import pyplot as plt


DATA_DIR = 'C:\\Users\\3379p\\OneDrive\\Desktop\\vscode\\codysseyCampus\\data\\pr7'
DEFAULT_IMAGE = os.path.join(DATA_DIR, 'default.png')
QUIZ_IMAGE = os.path.join(DATA_DIR, 'quiz.png')


def load_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f'이미지를 열 수 없습니다: {image_path}')
    return image


def show_image(window_name, image):
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyWindow(window_name)


def task1_flip_and_rotate():
    image = load_image(DEFAULT_IMAGE)
    if image is None:
        return

    show_image('1. original', image)
    show_image('1. flip vertical', cv2.flip(image, 0))
    show_image('1. flip horizontal', cv2.flip(image, 1))
    show_image('1. rotate 90 cw', cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE))
    show_image('1. rotate 180', cv2.rotate(image, cv2.ROTATE_180))

    upsampled = cv2.pyrUp(image)
    show_image('1. upsample x2', upsampled)


def task2_resize_and_crop():
    image = load_image(DEFAULT_IMAGE)
    if image is None:
        return

    show_image('2. original', image)

    resized_vga = cv2.resize(image, (640, 480))
    show_image('2. 640x480', resized_vga)

    resized_xga = cv2.resize(image, (1024, 768))
    show_image('2. 1024x768', resized_xga)

    relative = cv2.resize(
        image,
        None,
        fx=0.3,
        fy=0.7,
        interpolation=cv2.INTER_LINEAR,
    )
    show_image('2. fx=0.3 fy=0.7', relative)

    height, width = image.shape[:2]
    start_y = height // 4
    end_y = (height * 3) // 4
    start_x = width // 4
    end_x = (width * 3) // 4
    cropped = image[start_y:end_y, start_x:end_x].copy()
    show_image('2. crop (deep copy)', cropped)


def task3_color_and_invert():
    image = load_image(DEFAULT_IMAGE)
    if image is None:
        return

    show_image('3. original', image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    show_image('3. gray', gray)

    inverted = cv2.bitwise_not(image)
    show_image('3. inverted', inverted)

    plt.figure('3. histogram')
    plt.subplot(1, 2, 1)
    plt.title('Original')
    plt.hist(image.ravel(), 256, [0, 256])
    plt.subplot(1, 2, 2)
    plt.title('Inverted')
    plt.hist(inverted.ravel(), 256, [0, 256])
    plt.tight_layout()
    plt.show()


def task4_binarize_and_edges():
    image = load_image(DEFAULT_IMAGE)
    if image is None:
        return

    show_image('4. original', image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    show_image('4. gray', gray)

    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    show_image('4. binary', binary)

    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel = cv2.convertScaleAbs(cv2.magnitude(sobel_x, sobel_y))
    show_image('4. sobel', sobel)

    laplacian = cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_64F))
    show_image('4. laplacian', laplacian)

    canny = cv2.Canny(gray, 100, 200)
    show_image('4. canny', canny)

    quiz = load_image(QUIZ_IMAGE)
    if quiz is None:
        return

    blurred = cv2.GaussianBlur(quiz, (15, 15), 0)
    show_image('4. blur', blurred)

    height, width = quiz.shape[:2]
    partial = quiz.copy()
    y1 = height // 4
    y2 = (height * 3) // 4
    x1 = width // 4
    x2 = (width * 3) // 4
    partial[y1:y2, x1:x2] = cv2.GaussianBlur(
        quiz[y1:y2, x1:x2],
        (25, 25),
        0,
    )
    show_image('4. partial blur', partial)


def task5_hsv_split():
    image = load_image(DEFAULT_IMAGE)
    if image is None:
        return

    show_image('5. original', image)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hue, saturation, value = cv2.split(hsv)
    show_image('5. H', hue)
    show_image('5. S', saturation)
    show_image('5. V', value)

    blue, green, red = cv2.split(image)
    show_image('5. B channel', blue)
    show_image('5. G channel', green)
    show_image('5. R channel', red)


def draw_label(canvas, text, anchor, label_offset, color):
    text_pos = (anchor[0] + label_offset[0], anchor[1] + label_offset[1])
    cv2.line(canvas, anchor, text_pos, color, 1)
    cv2.putText(
        canvas,
        text,
        (text_pos[0] + 4, text_pos[1] + 4),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        color,
        2,
    )


def task6_labeling():
    image = load_image(QUIZ_IMAGE)
    if image is None:
        image = load_image(DEFAULT_IMAGE)
    if image is None:
        return

    height, width = image.shape[:2]
    red = (0, 0, 255)

    objects = [
        {
            'name': 'Object A',
            'box': (
                int(width * 0.10),
                int(height * 0.15),
                int(width * 0.30),
                int(height * 0.35),
            ),
            'shape': 'rect',
        },
        {
            'name': 'Object B',
            'box': (
                int(width * 0.55),
                int(height * 0.20),
                int(width * 0.75),
                int(height * 0.40),
            ),
            'shape': 'circle',
        },
        {
            'name': 'Object C',
            'box': (
                int(width * 0.30),
                int(height * 0.60),
                int(width * 0.50),
                int(height * 0.85),
            ),
            'shape': 'triangle',
        },
    ]

    canvas = image.copy()
    for obj in objects:
        x1, y1, x2, y2 = obj['box']
        cv2.rectangle(canvas, (x1, y1), (x2, y2), red, 2)
        draw_label(canvas, obj['name'], (x2, y1), (40, -25), red)
    show_image('6. labeling', canvas)

    bonus = image.copy()
    for obj in objects:
        x1, y1, x2, y2 = obj['box']
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        if obj['shape'] == 'rect':
            cv2.rectangle(bonus, (x1, y1), (x2, y2), red, 2)
        elif obj['shape'] == 'circle':
            radius = min(x2 - x1, y2 - y1) // 2
            cv2.circle(bonus, (center_x, center_y), radius, red, 2)
        elif obj['shape'] == 'triangle':
            points = np.array(
                [[center_x, y1], [x1, y2], [x2, y2]],
                np.int32,
            )
            cv2.polylines(bonus, [points], True, red, 2)

        draw_label(bonus, obj['name'], (x2, y1), (40, -25), red)
    show_image('6. bonus shapes', bonus)


def main():
    task1_flip_and_rotate()
    task2_resize_and_crop()
    task3_color_and_invert()
    task4_binarize_and_edges()
    task5_hsv_split()
    task6_labeling()


if __name__ == '__main__':
    main()
