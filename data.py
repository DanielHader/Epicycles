from __future__ import division
from PIL import Image

im_raw = Image.open('mathologer.bmp')
im = im_raw.convert('RGB')

pixels = []

scale = max(im.width, im.height)

for x in range(im.width):
    for y in range(im.height):
        r, g, b = im.getpixel((x, y))
        if r == g == b == 0:
            pixels.append(complex(x, y) / scale)

print len(pixels)