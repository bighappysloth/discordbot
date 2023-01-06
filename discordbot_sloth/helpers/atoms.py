import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define unit cube vertices
vertices = [[0,0,0], [1,0,0], [1,1,0], [0,1,0], [0,0,1], [1,0,1], [1,1,1], [0,1,1]]

# Set x, y, and z limits
x_lim = (0,2)
y_lim = (0,2)
z_lim = (0,2)

# Set background color
bg_color = 'k'

# Create figure and 3D axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot unit cube vertices
for vertex in vertices:
  ax.scatter(vertex[0], vertex[1], vertex[2], c='r', marker='o')
  ax.text(vertex[0]+0.1, vertex[1]+0.1, vertex[2]+0.1, f'({vertex[0]}, {vertex[1]}, {vertex[2]})')

# Set plot limits and background color
ax.set_xlim(x_lim)
ax.set_ylim(y_lim)
ax.set_zlim(z_lim)
ax.set_facecolor(bg_color)


plt.show()