from pyquaternion import Quaternion
from matplotlib.animation import FuncAnimation  
from matplotlib.widgets import CheckButtons, Slider
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
import numpy as np
import math
import matplotlib.pyplot as plt

#blue = axes of rotation
#green = "immediate" axis of rotation

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

class QuaternionChain:
    def __init__(self):
        self.chain = np.empty([0, 3])
    def pop(self, index):
        self.chain = np.delete(self.chain, index, axis=0)
    def pop(self):
        self.chain = np.delete(self.chain, -1, axis=0)
    def push(self, axis):
        self.chain = np.vstack([self.chain, axis])
    def size(self):
        return len(self.chain)
    def edit(self, index, new_axis):
        self.chain[index] = new_axis

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

def plot_rect_rotation_angle(rotation, ax, rect, quaternion_chain, frame):
    global update_delta_alpha
    update_delta_alpha(frame)
    for artist in ax.artists + ax.lines:
        artist.remove()
    q = Quaternion() #identity quaternion
    for i in range(len(quaternion_chain.chain)):
        q_axis = quaternion_chain.chain[i]
        if (q_axis[0]==q_axis[1]==q_axis[2]==0):
            continue
        if (i == 1):
            q = q * Quaternion(axis=q_axis, angle=rotation*1.5)
        else:
            q = q * Quaternion(axis=q_axis, angle=rotation)
        q = q * Quaternion(axis=q_axis, angle=rotation)
        plot_vector(ax, q.rotate(q_axis), color='blue')

    plot_vector(ax, q.axis, color="green")
    print(q.axis)
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

def plot_rect_rotation(i, ax, rect, quaternion_chain, frame):
    plot_rect_rotation_angle((np.linspace(0, math.pi * 2, frame))[i], ax, rect, quaternion_chain, i)

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

def toggle_animation(on, anim):
    if (on):
        anim.event_source.start()
    else:
        anim.event_source.stop()

def normalize(axis):
    magnitude = np.linalg.norm(axis)
    if magnitude == 0:
        return axis
    normalized_vector = (axis / magnitude).round(2)
    return normalized_vector

def main():
    fig = plt.figure()
    delta_alpha = plt.axes((0.5, 0.15, 0.25, 0.7))
    ax = plt.axes((-0.2, 0.06, 0.8, 0.8), projection ='3d')
    slider_ax = fig.add_axes([0.1, 0.9, 0.8, 0.1])   
    button_ax = fig.add_axes([0.825, 0.045, 0.15, 0.1]) 
    configure(ax)

    #initial example chain
    quaternion_chain = QuaternionChain()
    quaternion_chain.push(np.array([0, 0, 1]))
    quaternion_chain.push(np.array([1, 0, 0]))
    input_axes = []
    text_boxes = []

    def add_quaternion_input(label, initial=''):
        axbox = fig.add_axes([0.78, 0.8 - 0.1 * (len(input_axes) + 1), 0.2, 0.075])
        text_box = TextBox(ax=axbox, label=label, initial=initial)
        input_axes.append(axbox)
        text_box.on_submit(lambda dummylambda: refresh_quaternions(text_box))
        text_boxes.append(text_box)

    def refresh_inputs_push():
        if (len(quaternion_chain.chain) < 6):
            identity = np.array([0, 0, 0])
            quaternion_chain.push(identity)
            update_input_boxes()

    def refresh_inputs_pop():
        if (len(quaternion_chain.chain) > 0):
            quaternion_chain.pop()
            update_input_boxes()

    def refresh_quaternions(text_box):
        index = int((text_box.label.get_text()))
        axis = np.fromstring(text_box.text, sep=', ', dtype=float)
        axis = normalize(axis)
        text_box.set_val(str(axis.tolist())[1:-1])
        quaternion_chain.edit(index, axis)
        generate_delta_alpha_graph(quaternion_chain)

    global update_delta_alpha
    def update_delta_alpha(frame_num):
        global delta_alpha_values
        global num_frames
        delta_alpha.cla()
        delta_alpha.set_xlim([0, 2*math.pi])
        delta_alpha.set_ylim([0, 2*math.pi])
        delta_alpha.plot(delta_alpha_values[0:frame_num, 0], delta_alpha_values[0:frame_num, 1], 'green')

    def generate_delta_alpha_graph(q_chain):
        global delta_alpha_values
        delta_alpha_values = np.empty((0, 2))
        global num_frames
        for alpha in np.linspace(0, 2*math.pi, num_frames):
            base = Quaternion()
            for ax in q_chain.chain:
                base *= (Quaternion(axis=ax, angle=alpha))
            cur_angle = base.angle
            if (cur_angle < 0):
                cur_angle += 2*math.pi
            delta_alpha_values = np.vstack((delta_alpha_values, np.array([alpha, cur_angle])))
        print(delta_alpha_values)

    def update_input_boxes():
        text_boxes.clear()
        while (len(input_axes) > 0):
            fig.delaxes(input_axes[0])
            input_axes.pop(0)
        for i in range(quaternion_chain.size()):
            add_quaternion_input(i, str(quaternion_chain.chain[i].tolist())[1:-1])
        margin=0.007
        axadd = fig.add_axes([0.78, 0.8 - 0.1 * (len(input_axes) + 1), 0.1-margin, 0.075])
        axremove = fig.add_axes([0.88+margin, 0.8 - 0.1 * (len(input_axes) + 1), 0.1-margin, 0.075])
        global add_button
        global remove_button
        add_button = Button(axadd, "add", color="white")
        add_button.on_clicked(lambda dummylambda: refresh_inputs_push())
        remove_button = Button(axremove, "remove", color="white")
        remove_button.on_clicked(lambda dummylambda: refresh_inputs_pop())
        input_axes.append(axadd)
        input_axes.append(axremove)
        generate_delta_alpha_graph(quaternion_chain)
    
    generate_delta_alpha_graph(quaternion_chain)
    update_input_boxes()

    p1 = Vector(np.array([0.5, 0.25, 0]), np.array([0.5, 0.25, 0.125]))
    p2 = Vector(np.array([0.5, -0.25, 0]), np.array([0.5, -0.25, 0.125]))
    p3 = Vector(np.array([-0.5, -0.25, 0]), np.array([-0.5, -0.25, 0.125]))
    p4 = Vector(np.array([-0.5, 0.25, 0]), np.array([-0.5, 0.25, 0.125]))
    r = Rect(p1, p2, p3, p4)

    theta = 0
    angle_slider = Slider(
        ax=slider_ax,
        label='Theta\n(radians)',
        valmin=0,
        valmax=math.pi*2,
        valinit=0,
        dragging=True,
    )

    animate_button = CheckButtons(
        ax=button_ax,
        labels=["Animate"],
        actives=[1],
        frame_props={
            'sizes':np.array([100])
        },
        check_props={
            'sizes':np.array([100])
        },
    )

    args = [ax, r, quaternion_chain, num_frames]
    plot_args = []
    anim = FuncAnimation(fig, plot_rect_rotation, fargs=args, frames = num_frames, interval = 10)
    # plot_anim = FuncAnimation(fig, update_delta_alpha, fargs=plot_args, frames=num_frames, interval=10)
    angle_slider.on_changed(lambda new_angle: plot_rect_rotation_angle(new_angle, ax, r, quaternion_chain, int(new_angle/(2*math.pi)*num_frames)))
    angle_slider.on_changed(lambda dummy_lambda: animate_button.set_active(0) if animate_button.get_status()[0] == True else False)
    animate_button.on_clicked(lambda dummy_lambda: toggle_animation(animate_button.get_status()[0], anim))

    plot_rect_rotation(theta, ax, r, quaternion_chain, num_frames)

    plt.show()

if (__name__ == "__main__"):
    global num_frames
    num_frames = 120
    main()