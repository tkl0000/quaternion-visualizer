from pyquaternion import Quaternion
from matplotlib.animation import FuncAnimation  
import numpy as np
import math
import matplotlib.pyplot as plt

class Vector:
    def __init__(self, base, tick):
        self.base = base
        self.tick = tick



def plot_vector(ax, vec, color='green'):
    x = np.linspace(0, vec[0])
    y = np.linspace(0, vec[1])
    z = np.linspace(0, vec[2])
    
    # plotting
    ax.plot3D(x, y, z, color)

def plot_rotation(i, ax, vecs, q_axis, frames):
    for artist in plt.gca().lines + plt.gca().collections:
        artist.remove()
    q_x = np.linspace(0, q_axis[0])
    q_y = np.linspace(0, q_axis[1])
    q_z = np.linspace(0, q_axis[2])
    ax.plot3D(q_x, q_y, q_z, 'blue')
    q = Quaternion(axis=q_axis, angle=(np.linspace(0, math.pi * 2, frames))[i])
    for v in vecs:
        base_prime = q.rotate(v.base)
        tick_prime = q.rotate(v.tick)
        x_base = np.linspace(0, base_prime[0])
        y_base = np.linspace(0, base_prime[1])
        z_base = np.linspace(0, base_prime[2])
        x_tick = np.linspace(base_prime[0], tick_prime[0])
        y_tick = np.linspace(base_prime[1], tick_prime[1])
        z_tick = np.linspace(base_prime[2], tick_prime[2])
        ax.plot3D(x_base, y_base, z_base, 'black')
        ax.plot3D(x_tick, y_tick, z_tick, 'red')

fig = plt.figure()
 
# syntax for 3-D projection
ax = plt.axes(projection ='3d')
ax.axes.set_xlim3d(left=-1, right=1) 
ax.axes.set_ylim3d(bottom=-1, top=1) 
ax.axes.set_zlim3d(bottom=-1, top=1) 
ax.set_xticks([-1, 0, 1])
ax.set_yticks([-1, 0, 1])
ax.set_zticks([-1, 0, 1])
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
 
#"basis" vector


# for i in np.linspace(0, math.pi * 2):
#     print(i)
#     q = Quaternion(axis=quaternion_axis, angle=i)
#     v_prime = q.rotate(v)
#     plot_vector(ax, v_prime)

quaternion_axis = np.array([1., 1., 1.])
v = Vector(np.array([1, 0, 0]), np.array([1, 0, 0.25]))

num_frames = 200
args = [ax, [v], quaternion_axis, num_frames]
anim = FuncAnimation(fig, plot_rotation, fargs=args, frames = num_frames, interval = 20) 
  
# anim.save('ok.mp4',  
#           writer = 'ffmpeg', fps = 30) 

# plot_vector(ax, v, 'black')
# plot_vector(ax, quaternion_axis, 'blue')


plt.show()