from pyquaternion import Quaternion
from matplotlib.animation import FuncAnimation  
from matplotlib.widgets import CheckButtons
import numpy as np
import math
import matplotlib.pyplot as plt


class Rect:
    def __init__(self, v1, v2, v3, v4):
        self.p1 = v1
        self.p2 = v2
        self.p3 = v3
        self.p4 = v4
    def as_array(self):
        return np.array([self.p1, self.p2, self.p3, self.p4])

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

def plot_vector_rotation(i, ax, vecs, q_axis, frames):
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

def plot_rect_rotation(i, ax, rect, q_axes, frames):
    for artist in plt.gca().lines + plt.gca().collections:
        artist.remove()
    q = Quaternion() #identity quaternion
    for q_axis in q_axes:
        q = q * Quaternion(axis=q_axis, angle=(np.linspace(0, math.pi * 2, frames))[i])
        plot_vector(ax, q.rotate(q_axis), 'blue')

    print(q.angle)

    points = rect.as_array()
    for p_index in range(0, points.size):

        p_a = points[p_index]
        p_b = points[p_index-1]

        a_base_prime = q.rotate(p_a.base)
        a_tick_prime = q.rotate(p_a.tick)
        b_base_prime = q.rotate(p_b.base)
        b_tick_prime = q.rotate(p_b.tick)

        ax.plot3D(np.linspace(a_base_prime[0], b_base_prime[0]), 
                  np.linspace(a_base_prime[1], b_base_prime[1]), 
                  np.linspace(a_base_prime[2], b_base_prime[2]), 'black')
        ax.plot3D(np.linspace(a_base_prime[0], a_tick_prime[0]),
                  np.linspace(a_base_prime[1], a_tick_prime[1]),
                  np.linspace(a_base_prime[2], a_tick_prime[2]), 'red')

def configure(ax):
    ax.axes.set_xlim3d(left=-1, right=1) 
    ax.axes.set_ylim3d(bottom=-1, top=1) 
    ax.axes.set_zlim3d(bottom=-1, top=1) 
    ax.set_xticks([-1, 0, 1])
    ax.set_yticks([-1, 0, 1])
    ax.set_zticks([-1, 0, 1])
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

def main():
    fig = plt.figure()
    
    ax = plt.axes(projection ='3d')
    configure(ax)
    
    q1 = np.array([0., 0., 1.])
    q2 = np.array([1., 0., 0])
    q_array = np.array([q1, q2])

    p1 = Vector(np.array([0.5, 0.25, 0]), np.array([0.5, 0.25, 0.125]))
    p2 = Vector(np.array([0.5, -0.25, 0]), np.array([0.5, -0.25, 0.125]))
    p3 = Vector(np.array([-0.5, -0.25, 0]), np.array([-0.5, -0.25, 0.125]))
    p4 = Vector(np.array([-0.5, 0.25, 0]), np.array([-0.5, 0.25, 0.125]))

    r = Rect(p1, p2, p3, p4)

    num_frames = 200
    args = [ax, r, q_array, num_frames]
    anim = FuncAnimation(fig, plot_rect_rotation, fargs=args, frames = num_frames, interval = 20)
    # anim = FuncAnimation(fig, plot_vector_rotation, fargs=args, frames = num_frames, interval = 20) 

    
    # anim.save('ok.mp4',  writer = 'ffmpeg', fps = 30) 

    # plot_vector(ax, v, 'black')
    # plot_vector(ax, quaternion_axis, 'blue')

    plt.show()

if (__name__ == "__main__"):
    main()