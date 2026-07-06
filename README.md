### IDEAS - Institute of Data Engineering, Analytics and Science Foundation
**Spring Internship Program 2026**

---

## 📌 Project Overview
This project serves as an introductory practical notebook covering fundamental computer vision concepts, basic image manipulations via **OpenCV**, and data engineering pipelines for deep learning using **PyTorch** and **Torchvision**. 

The assignment is split into two primary sections:
1. **Geometric Manipulations & OpenCV Basics:** Loading, changing color spaces, translating, resizing, and rotating images.
2. **PyTorch Data Pipelines:** Unzipping dataset archives, building dynamic augmentation pipelines using `transforms.Compose`, creating custom dataset loaders with `ImageFolder`, and batching data via `DataLoader`.

---

## 🛠️ Prerequisites & Installation

To run this notebook successfully, ensure you have Python 3.8+ installed along with the required frameworks:

```bash
pip install numpy opencv-python torch torchvision

```

---

## 📂 Detailed Question Workings & Outputs

### Question 1: Import Libraries and Load Image (5 Marks)

* **Task:** Load `moon-pexels-frank-cone.jpg` using OpenCV and print its shape.
* **Working:** `cv2.imread()` reads the file paths and maps them into a NumPy N-dimensional array. `.shape` retrieves the image properties as `(Height, Width, Channels)`.
* **Code Execution:**
```python
import cv2
import numpy as np

original_image = cv2.imread('moon-pexels-frank-cone.jpg')
if original_image is not None:
    print(original_image.shape)
else:
    print("Error: Image not found. Please check the file path.")

```


* **Output:**
```text
(800, 640, 3)

```



---

### Question 2: Convert to Grayscale (5 Marks)

* **Task:** Convert the original image to a grayscale canvas.
* **Working:** Uses the luma transform formula internally via `cv2.COLOR_BGR2GRAY`:

$$Y = 0.299R + 0.587G + 0.114B$$



This drops the 3rd (channel) dimension entirely.
* **Code Execution:**
```python
grayscale_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
print(grayscale_image.shape)

```


* **Output:**
```text
(800, 640)

```



---

### Question 3: Save the Grayscale Image (5 Marks)

* **Task:** Save the converted array locally to disk as `graymoon.jpg`.
* **Working:** `cv2.imwrite()` compresses the active NumPy matrix array back into a standard file format specified by the suffix target extension.
* **Code Execution:**
```python
cv2.imwrite('graymoon.jpg', grayscale_image)
print("File 'graymoon.jpg' has been successfully saved to your workspace.")

```


* **Output:**
```text
File 'graymoon.jpg' has been successfully saved to your workspace.

```



---

### Question 4: Shift the Image (10 Marks)

* **Task:** Translate the canvas 50px right and 100px down.
* **Working:** Maps pixel locations using an affine translation matrix $M$:

$$M = \begin{bmatrix} 1 & 0 & t_x \\ 0 & 1 & t_y \end{bmatrix} = \begin{bmatrix} 1 & 0 & 50 \\ 0 & 1 & 100 \end{bmatrix}$$


* **Code Execution:**
```python
M = np.float32([[1, 0, 50], [0, 1, 100]])
rows, cols = original_image.shape[:2]
shifted_image = cv2.warpAffine(original_image, M, (cols, rows))
print(shifted_image.shape)

```


* **Output:**
```text
(800, 640, 3)

```



---

### Question 5: Resize the Image (10 Marks)

* **Task:** Shrink/stretch the image dimensions to $150 \times 100$ (Width $\times$ Height).
* **Working:** Uses bilinear pixel interpolation down-sampling to map the original resolution to the hardcoded `(width, height)` target tuple.
* **Code Execution:**
```python
new_dimensions = (150, 100)
resized_image = cv2.resize(original_image, new_dimensions)
print(resized_image.shape)

```


* **Output:**
```text
(100, 150, 3)

```



---

### Question 6: Rotate the Image (10 Marks)

* **Task:** Rotate the canvas 90° counter-clockwise around its center point.
* **Working:** Calculates an affine transformation matrix based on an anchoring coordinate center, scale scaling factor, and target angle using trigonometry.
* **Code Execution:**
```python
(h, w) = original_image.shape[:2]
center = (w // 2, h // 2)
M = cv2.getRotationMatrix2D(center, 90, 1.0)
rotated_image = cv2.warpAffine(original_image, M, (h, w))
print(rotated_image.shape)

```


* **Output:**
```text
(640, 800, 3)

```



---

### Question 7: Download and Unzip Cat/Dog Data (10 Marks)

* **Task:** Unpack training and evaluation image datasets from archive compression files.
* **Working:** Executes an asynchronous bash sub-process stream extraction pattern to map files out of `.zip`.
* **Code Execution:**
```python
import os
!unzip -q Cat_Dog_data.zip
if os.path.exists('Cat_Dog_data'):
    print("Success: 'Cat_Dog_data' directory created and extracted!")
    print("Contents:", os.listdir('Cat_Dog_data'))
else:
    print("Error: 'Cat_Dog_data.zip' not found in the sidebar. Please upload it first.")

```


* **Output:**
```text
Success: 'Cat_Dog_data' directory created and extracted!
Contents: ['test', 'train', '.DS_Store']

```



---

### Question 8: Create an Image Transform Pipeline (15 Marks)

* **Task:** Standardize and augment raw visual features before tensor execution.
* **Working:** `Compose` links functional steps sequence operations sequentially: Resizes $\rightarrow$ Bernoulli $p=0.5$ dynamic flip $\rightarrow$ Matrix array scaling range normalizes from $[0, 255]$ integers down to $[0.0, 1.0]$ float tensors.
* **Code Execution:**
```python
import torch
from torchvision import transforms

train_transform = transforms.Compose([
    transforms.Resize((255, 255)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor()
])
print(train_transform)

```


* **Output:**
```text
Compose(
    Resize(size=(255, 255), interpolation=bilinear, max_size=None, antialias=True)
    RandomHorizontalFlip(p=0.5)
    ToTensor()
)

```



---

### Question 9: Create an ImageFolder Dataset (15 Marks)

* **Task:** Map a physical multi-class folder tree layout directly into structured datasets.
* **Working:** Evaluates subdirectory leaf folder arrays (`/train/cat`, `/train/dog`) dynamically matching subdirectory names to target labels automatically.
* **Code Execution:**
```python
from torchvision import datasets

train_dir = 'Cat_Dog_data/train'
train_dataset = datasets.ImageFolder(root=train_dir, transform=train_transform)
print(f"Total number of images in the training dataset: {len(train_dataset)}")

```


* **Output:**
```text
Total number of images in the training dataset: 22500

```



---

### Question 10: Create a DataLoader (15 Marks)

* **Task:** Construct a mini-batching generation pipeline engine with active shuffling.
* **Working:** Combines isolated item structural patterns into target vector arrays using an automated iterator abstraction loop.
* **Code Execution:**
```python
import torch

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)
images, labels = next(iter(train_loader))
print(f"Images batch shape: {images.shape}")
print(f"Labels batch shape: {labels.shape}")

```


* **Output:**
```text
Images batch shape: torch.Size([64, 3, 255, 255])
Labels batch shape: torch.Size([64])

```



---

## 🎯 Final Pipeline Dimensions Summary

* **Augmented Image Size:** $255 \times 255$ pixels across 3 RGB channels.
* **Mini-batch Configuration:** 64 items per parallel execution window batch step with automatic structural shuffling active.
```

```
