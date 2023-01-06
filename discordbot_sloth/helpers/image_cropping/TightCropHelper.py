# image processing

import numpy as np
import matplotlib.pyplot as plt
from skimage import io

fname = 'horizontal_crop.png'


image = io.imread(f'./{fname}')
print(type(image))  # prints type ndarray
print(image.dtype)
print(image.shape)
print(image.min(), image.max())


fig, axs = plt.subplots(1, 2)


# Finding the vertical bar from the left.
print(
    f'Loaded: {fname}, type: {type(image)}, dim(image)={image.shape}, dim(image[0][:])={image[0][:].shape}, dim(image[:][0])={image[:][0].shape}')

# Why are images three dimensional? Some colour channel thing?
blank1 = np.ones((image.shape[1], image.shape[2]))*255
blank2 = np.ones((image.shape[0], image.shape[2]))*255
i = j = 0
print(f'Shapes: blank1={blank1.shape}, blank2={blank2.shape}')
while np.array_equal(blank1, image[i, :, :]):
    i = i + 1
while np.array_equal(blank2, image[:, j, :]):
    j = j + 1
top_left_corner = (i, j)
print(f'top_left_corner={top_left_corner}')  # top left corner achieved.

# now calculate the bottom right corner.
i, j = image.shape[0]-1, image.shape[1]-1
while np.array_equal(blank1, image[i, :, :]):
    i = i-1
while np.array_equal(blank2, image[:, j, :]):
    j = j - 1


bottom_right_corner = (i, j)
print(f'top_left_corner={top_left_corner}')  # top left corner achieved.
print(f'bottom_left_corner={bottom_right_corner}')

points = [[x, y] for x in {top_left_corner[0], bottom_right_corner[0]}
          for y in {top_left_corner[1], bottom_right_corner[1]}]
print(f'Points: {points}')


x = np.array([z[1] for z in points])
y = np.array([z[0] for z in points])
print(f'x={x},y={y}')
# np.array(points[:][1]) describes the y-coordinates of all the points.
axs[0].plot(x, y, marker='o')
# plt.plot([top_left_corner[0],bottom_right_corner[0]],[top_left_corner[1],bottom_right_corner[1]],marker='o')


axs[0].imshow(image)

cropped_image = image[top_left_corner[0]:bottom_right_corner[0],
                      top_left_corner[1]:bottom_right_corner[1], :]  # success
axs[1].imshow(cropped_image)
cropped_fname = fname[:-4] + r'_whiteless' + fname[-4:]
io.imsave(cropped_fname, cropped_image)

print(f'Saving to {cropped_fname}...')

plt.tight_layout()
plt.show()
