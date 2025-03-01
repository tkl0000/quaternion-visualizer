import sys
from pyquaternion import Quaternion
from matplotlib.animation import FuncAnimation  
from matplotlib.widgets import CheckButtons, Slider
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFrame
from PyQt5.QtCore import pyqtSignal, Qt
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

class QuaternionInputWindow(QWidget):
    quaternion_updated = pyqtSignal()  # Signal to notify changes

    def __init__(self, quaternion_chain):
        super().__init__()
        self.quaternion_chain = quaternion_chain
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Quaternions")
        self.setGeometry(100, 100, 300, 400)

        layout = QVBoxLayout()

        self.labels = []
        self.inputs = []

        frame = QFrame()
        frame_layout = QVBoxLayout(frame)

        # Create input fields for each quaternion
        for i in range(self.quaternion_chain.size()):
            label = QLabel(f"Quaternion {i}:")
            input_box = QLineEdit(", ".join(map(str, self.quaternion_chain.chain[i])))
            input_box.setAlignment(Qt.AlignCenter)
            input_box.editingFinished.connect(lambda i=i: self.update_quaternion(i))

            frame_layout.addWidget(label)
            frame_layout.addWidget(input_box)

            self.labels.append(label)
            self.inputs.append(input_box)

        layout.addWidget(frame)

        # Add buttons to update quaternions
        self.add_button = QPushButton("Add Quaternion")
        self.add_button.clicked.connect(self.add_quaternion)

        self.remove_button = QPushButton("Remove Last Quaternion")
        self.remove_button.clicked.connect(self.remove_quaternion)

        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)

    def update_quaternion(self, index):
        try:
            new_values = np.fromstring(self.inputs[index].text(), sep=',', dtype=float)
            if new_values.size == 3:
                new_values = normalize(new_values)
                new_values = np.append(new_values, 1)  # Add multiplier if missing
            if new_values.size == 4:
                new_values = normalize(new_values)
                self.quaternion_chain.edit(index, new_values)
                self.quaternion_updated.emit()  # Notify update
            # print(self.quaternion_chain.chain[index].astype(str))
            text_replace = ", ".join(self.quaternion_chain.chain[index].astype(str))
            self.inputs[index].setText(text_replace)
            generate_angle_values(self.quaternion_chain)
        except ValueError:
            pass  # Ignore invalid input

    def add_quaternion(self):
        self.quaternion_chain.push(np.array([0, 0, 1, 1])) 
        self.refresh_inputs()
        self.quaternion_updated.emit()  
        generate_angle_values(self.quaternion_chain)

    def remove_quaternion(self):
        if self.quaternion_chain.size() > 0:
            self.quaternion_chain.pop()
            self.refresh_inputs()
            self.quaternion_updated.emit()  
            generate_angle_values(self.quaternion_chain)

    def refresh_inputs(self):
        # Clear layout
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.labels.clear()
        self.inputs.clear()

        # Recreate input fields
        for i in range(self.quaternion_chain.size()):
            label = QLabel(f"Quaternion {i}:")
            input_box = QLineEdit(", ".join(map(str, self.quaternion_chain.chain[i])))
            input_box.setAlignment(Qt.AlignCenter)
            input_box.editingFinished.connect(lambda i=i: self.update_quaternion(i))
            self.layout().addWidget(label)
            self.layout().addWidget(input_box)

            self.labels.append(label)
            self.inputs.append(input_box)

        self.layout().addWidget(self.add_button)
        self.layout().addWidget(self.remove_button)

class QuaternionChain:
    def __init__(self):
        self.chain = np.empty([0, 4])
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

def generate_angle_values(quaternion_chain):
    global angle_values
    global num_frames
    angle_values = np.empty((0, 5))
    for alpha in np.linspace(0, 2*math.pi, num_frames):
        q = Quaternion()
        for i in range(len(quaternion_chain.chain)):
            q_axis = quaternion_chain.chain[i][0:3]
            q_multiplier = quaternion_chain.chain[i][3]
            if (q_axis[0]==q_axis[1]==q_axis[2]==0):
                continue
            q = q * Quaternion(axis=q_axis, angle=alpha*q_multiplier)
        cur_angle = q.angle
        cur_axis = q.axis
        if (cur_angle < 0):
            cur_angle += 2*math.pi
        angle_values = np.vstack((angle_values, np.array([alpha, cur_axis[0], cur_axis[1], cur_axis[2], cur_angle])))
    print("New Angle Values Generated")
    # print(angle_values)

def plot_vector(ax, vec, color='green'):
    x = np.linspace(0, vec[0])
    y = np.linspace(0, vec[1])
    z = np.linspace(0, vec[2])
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
    xyz = axis[0:3]
    magnitude = np.linalg.norm(xyz)
    if magnitude == 0:
        return axis
    xyz = (xyz / magnitude).round(3)
    return np.append(xyz, [axis[3]])

def main():

    app = QApplication(sys.argv)

    fig = plt.figure()
    ax = plt.axes((0.1, 0.1, 0.8, 0.8), projection ='3d')  
    button_ax = fig.add_axes([0.825, 0.045, 0.15, 0.1]) 
    configure(ax)

    fig2 = plt.figure(figsize=(4, 6))
    ax2 = plt.axes((0.15, 0.15, 0.7, 0.8))

    fig3 = plt.figure(figsize=(6, 1))
    slider_ax = fig3.add_axes([0.2, 0.5, 0.6, 0.1]) 

    # initial example chain
    # axis = [x, y, z, multiplier]

    quaternion_chain = QuaternionChain()
    quaternion_chain.push(np.array([0, 0, 1, 1]))
    quaternion_chain.push(np.array([1, 0, 0, 1]))

    input_window = QuaternionInputWindow(quaternion_chain)
    input_window.show()
    # input_window.quaternion_updated.connect(lambda: update_plot(angle_slider.val, ax, quaternion_chain))
    input_window.quaternion_updated.connect(lambda: {})

    # def update_plot(new_angle, ax, quaternion_chain):
    #     plot_rect_rotation_angle(new_angle, ax, quaternion_chain)
    #     plt.draw()
    
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

    def plot_angle_from_frame(i):
        i = max(0, i-1)
        global angle_values
        ax2.cla()
        ax2.set_title(f'theta = {round(angle_values[i][1], 3)}')
        ax2.set_xlim([0, 2*math.pi])
        ax2.set_ylim([0, 2*math.pi])
        ax2.plot(angle_values[0:i, 0], angle_values[0:i, 4], 'green')
        fig2.canvas.draw_idle() 

    def plot_rect_rotation_angle(rotation, ax, rect, quaternion_chain, frame):

        global angle_values

        for artist in ax.artists + ax.lines:
            artist.remove()
        q = Quaternion() #identity quaternion
        for i in range(len(quaternion_chain.chain)):
            q_axis = quaternion_chain.chain[i][0:3]
            q_multiplier = quaternion_chain.chain[i][3]
            if (q_axis[0]==q_axis[1]==q_axis[2]==0):
                continue
            q = q * Quaternion(axis=q_axis, angle=rotation*q_multiplier)
            plot_vector(ax, q.rotate(q_axis), color='blue')

        plot_vector(ax, q.axis, color="green")
        ax.set_title(q)
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
            
        # resultant path
        # print(angle_values)
        ax.plot3D(angle_values[1:, 1], angle_values[1:, 2], angle_values[1:, 3], color="purple")
    
        fig.canvas.draw_idle() 

    def plot_rect_rotation_from_frame(i, ax, rect, quaternion_chain, num_frames):
        plot_rect_rotation_angle((np.linspace(0, math.pi * 2, num_frames))[i], ax, rect, quaternion_chain, i)

    args = [ax, r, quaternion_chain, num_frames]
    args2 = [ax2, r, quaternion_chain, num_frames]
    anim = FuncAnimation(fig, plot_rect_rotation_from_frame, fargs=args, frames = num_frames, interval = 10)
    anim2 = FuncAnimation(fig2, plot_angle_from_frame, frames = num_frames, interval=10)
    # plot_anim = FuncAnimation(fig, update_delta_alpha, fargs=plot_args, frames=num_frames, interval=10)
    angle_slider.on_changed(lambda new_angle: plot_rect_rotation_angle(new_angle, ax, r, quaternion_chain, int(new_angle/(2*math.pi)*num_frames)))
    angle_slider.on_changed(lambda new_angle: plot_angle_from_frame(int(new_angle/(2*math.pi)*num_frames)))
    angle_slider.on_changed(lambda dummy_lambda: animate_button.set_active(0) if animate_button.get_status()[0] == True else False)
    animate_button.on_clicked(lambda dummy_lambda: toggle_animation(animate_button.get_status()[0], anim))
    animate_button.on_clicked(lambda dummy_lambda: toggle_animation(animate_button.get_status()[0], anim2))

    generate_angle_values(quaternion_chain)
    plot_rect_rotation_from_frame(theta, ax, r, quaternion_chain, num_frames)
    

    plt.show()

if (__name__ == "__main__"):
    global num_frames
    num_frames = 120
    main()