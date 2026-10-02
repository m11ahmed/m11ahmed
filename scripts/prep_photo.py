"""Prep a photo for ASCII: remove bg (rembg), boost contrast (CLAHE), white background.
usage: python scripts/prep_photo.py photo.jpg"""
import sys, numpy as np
from PIL import Image

src = sys.argv[1]
img = Image.open(src).convert("RGB")
try:
    from rembg import remove
    rgba = remove(img)                      # subject isolated
except Exception as e:
    print("rembg unavailable, keeping background:", e)
    rgba = img.convert("RGBA")
bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
bg.alpha_composite(rgba)
gray = np.array(bg.convert("L"))
try:
    import cv2
    gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)
    # re-whiten the removed background after equalization
    mask = np.array(rgba.split()[-1]) < 20
    gray[mask] = 255
except Exception as e:
    print("opencv unavailable, skipping CLAHE:", e)
Image.fromarray(gray).save("source-prepped.png")
print("wrote source-prepped.png")
