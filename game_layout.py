from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.properties import NumericProperty, BooleanProperty
from kivy.vector import Vector
from molecule import Molecule  # Import the Molecule class
from kivy.core.window import Window
from random import uniform, randint
import math
from performance_monitor import PerformanceMonitor
from performance_monitor import set_global_monitor
from arduino_reading import ArduinoReading  # imported its reading right now!!!
# from arduino_receiver_fixed_reading_c import ArduinoReading
import serial
import time
import re
from kivy.uix.label import Label
import random
import psutil
import os
import gc
from kivy.animation import Animation


# TO DO LIST 
# Import ARDUNIO IN HERE after doing all teh c wrapping and all the information when shaking teh 
# arduino the energy shoudl be converted into the scale factor and after being added to teh kinetic energy 
# + scale factor in thsi stype of form and ==> then show thsi as a display on teh side panel 


# Add ardunio reading into teh app itself
# after this make sure to do the force calulation impact for ths cpu

# and the more molecules the higher computational power tahts it!!!

class GameLayout(Widget):

    intermolecular_forces = BooleanProperty(True)  # Toggle for intermolecular forces
    epsilon = NumericProperty(1.0)  # Lennard-Jones potential depth
    sigma = NumericProperty(1.0)  # Lennard-Jones potential sigma
    spring_constant = 100.0
    spring_rest_length = 2.0
    molecule_radius_ratio = 0.03
    use_verlet = True
    

    def __init__(self, performance_monitor, arduino_graph = None, **kwargs):
        super(GameLayout, self).__init__(**kwargs)
        # self.arduino = ArduinoReading('/dev/ttyUSB0')  # open serial once!!!! below connects twice and more
        try:
            # pay attention to env overrides and auto-detection from ArduinoReading
            self.arduino = ArduinoReading()
            print(f"[INFO] Arduino serial opened on {self.arduino.port} @ {self.arduino.baud_rate}")
        except Exception as e:
            print(f"[WARNING] Arduino not connected or no permission: {e}")
            print("         Hint: set ARDUINO_PORT=/dev/ttyACM0 and ensure you are in the 'dialout' group, then re-run.")
            self.arduino = None


        with self.canvas.before:
            Color(0.01, 0.01, 0.04, 1)  # Very dark navy — richer than pure black
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.frame_counter = 0   # added this to make it less
        self.performance_monitor = performance_monitor

        self.arduino_graph = arduino_graph

        self.molecules = []  # List of all molecules in the game        
        Clock.schedule_interval(self.monitor_performance, 1)
        set_global_monitor(self.performance_monitor)
        
        # run cleanup every 60 secs so memory doesnt get out of hand
        Clock.schedule_interval(self.periodic_cleanup, 60)  # Every 60 seconds 

        # --- Smooth performance helpers (low-risk) ---
        self.ui_update_every = 5           # update labels every 5 frames
        self.arrow_update_every = 5        # update force arrows at most every 5 frames
        self._arduino_log_accum = 0.0      # throttle arduino prints to ~1 Hz
        self._sec_accum = 0.0              # generic per-frame time accumulator
        self.arduino_activity = 0.0        # Arduino accelerometer activity (0-100)
        
        # keep track of prev acceleration so we can detect shaking
        self._prev_accel = None            # Previous (x, y, z) accelerometer values
        self._shake_intensity = 0.0        # Current shake intensity (0-100)

        # when cpu gets high slow down the updates
        self._governor_state = 'normal'    # normal or throttle mode
        self._governor_high_time = 0.0     # seconds above threshold
        self._governor_low_time = 0.0      # seconds below threshold
        self._governor_multiplier = 1.0    # 1.0 normal, >1.0 slows updates
        self._forces_hidden_by_governor = False

        # keep track of scheduling so governor doesnt mess with user speed
        self._speed_factor = 1.0
        self._base_interval = 1 / 30.0
        self._current_interval = self._base_interval

        # remember which radius we had so we dont redraw if nothing changed
        self._last_molecule_radius = 0.0

        # keyboard just needs to be set up once
        self._keyboard = None
        self._keyboard_initialized = False
        # track when keys were pressed so we dont get repeat events
        self._key_last_press = {}
        self._key_cooldown = 0.08   # 80 ms minimum between repeat events for the same key

        # garbage collection runs every 30 seconds
        # (not in monitor_performance cuz that runs every second and would create tons of timers!!)
        Clock.schedule_interval(lambda dt: gc.collect(), 30)

        # check governor stuff every half second
        Clock.schedule_interval(self._governor_update, 0.5)

        # mission manager gets hooked up later from simulation.py
        self.mission_manager = None

        self.bonds = {}  # store the bond lines here  
        # print(self.molecule_radius)
        self.old_pos = self.pos[:]
        self.old_size = self.size[:]
        self.pos_in_between = self.pos[:]
        self.size_in_between = self.size[:]
        self.scale = 10 ** (2)
        self.gravity = 0  # start with no gravity
        self.delta = 1 / 60.0  # Time step
        self.selected_molecule = None  # first molecule we touched for bonding
        self.simulation_running = False  # is the sim actually running rn
        self.size_factor = 0.6
        self.molecule_radius = self.size[0] * self.molecule_radius_ratio * self.size_factor # Radius of the molecule
        self.forces_visible = True

        # use LJ cutoff so it doesnt lag
        self.enable_lj_cutoff = True
        self.lj_cutoff_sigma = 2.5  # cutoff distance with sigma value

        self.arduino_data_label = Label(
            text="Arduino X: 0.00\nArduino Y: 0.00\nArduino Z: 0.00\nGravity Scale: 0.00",
            size_hint=(0.2, 0.15),  # Take up 20% width and 15% height of parent
            pos_hint={"x": 0.02, "top": 0.98},  # Near top-left corner
            color=(1, 1, 1, 1),  # white
            bold=True,
            font_size=Window.height * 0.035,  # 3.5% of screen height (much larger)
            halign='left',
            valign='top'
        )
        self.arduino_data_label.bind(size=self.arduino_data_label.setter('text_size'))

        # floating flash label — shows what a Makey Makey key just did
        self._feedback_label = Label(
            text='', markup=True,
            size_hint=(None, None), size=(260, 48),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            font_size='18sp', bold=True,
            halign='center', valign='middle',
            color=(0, 1, 1, 0),          # starts fully transparent
        )
        self.add_widget(self._feedback_label)

    # spatial hash got removed (just using simple approach now)


# Performance and CPU monitoring stuff
    def monitor_performance(self, dt):
        cpu_usage = self.performance_monitor.get_cpu_usage()
        atom_count = len(self.molecules)
        print(f"Atoms: {atom_count}, CPU Usage: {cpu_usage:.2f}%")

        # variable to store the scheduled update thing
        # self.update_event = None
        # Labels for stats
        # self.total_energy_label = Label(text="Total Energy: 0", size_hint=(None, None), pos_hint={})
        # self.temperature_label = Label(text="Temperature: 0", size_hint=(None, None), pos_hint={})
        # self.pressure_label = Label(text="Pressure: 0", size_hint=(None, None), pos_hint={})
        # # self.add_widget(self.total_energy_label)
        # self.add_widget(self.temperature_label)
        # self.add_widget(self.pressure_label)
        
        # key mappings for keyboard controls
        self.key_mapping = {
            'gravity_increase': 'w',
            'gravity_decrease': 's',
            'epsilon_increase': 'e',
            'epsilon_decrease': 'd',
            'sigma_increase': 'r',
            'sigma_decrease': 'f',
            'delta_increase': 't',
            'delta_decrease': 'g',
            'speed_increase': 'y',
            'speed_decrease': 'h',
            'size_increase' : 'u',
            'size_decrease' : 'j'
        }

        # set up the update schedule
        self.update_event = None
        if not self._keyboard_initialized:
            self.setup_keyboard()
            self._keyboard_initialized = True
        
        # GC is already set up in __init__, dont add another one here every second!
        
    def setup_keyboard(self):
        """set up keyboard bindings for slider controls"""
        if self._keyboard:
            try:
                self._keyboard.unbind(on_key_down=self.on_key_down)
            except Exception:
                pass
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down)

    def _keyboard_closed(self):
        """keyboard was released — unbind and immediately re-request so Makey Makey keeps working"""
        try:
            self._keyboard.unbind(on_key_down=self.on_key_down)
        except Exception:
            pass
        self._keyboard = None
        self._keyboard_initialized = False
        Clock.schedule_once(lambda _dt: self.setup_keyboard(), 0.05)

    def on_key_down(self, keyboard, keycode, text, modifiers):
        """Handle key press events for controlling sliders.

        Makey Makey board key layout:
          Arrow keys (base board / Makey Mouse) : up/down = gravity, left/right = epsilon
          Player 2 D-pad                        : a=gravity+, s=gravity-, w=gravity+, d=epsilon-
          Player 2 / Makey Max buttons          : f=sigma-, g=delta-
          Makey Max full keyboard section       : w/a=gravity+, s=gravity-, d/epsilon-,
                                                  f=sigma-, g=delta-
          Space (any board)                     : spawn molecule
        """
        key = keycode[1]

        # Debounce — dont fire same key twice in quick succession (stops UI from freezing)
        now = time.monotonic()
        if now - self._key_last_press.get(key, 0) < self._key_cooldown:
            return True
        self._key_last_press[key] = now

        if key == self.key_mapping['gravity_increase']:      # w
            self.adjust_gravity(1.0)
            self.show_key_feedback('Gravity  +')
        elif key == self.key_mapping['gravity_decrease']:    # s
            self.adjust_gravity(-1.0)
            self.show_key_feedback('Gravity  -')
        elif key == self.key_mapping['epsilon_increase']:    # e
            self.adjust_epsilon(0.5)
            self.show_key_feedback('Epsilon  +')
        elif key == self.key_mapping['epsilon_decrease']:    # d
            self.adjust_epsilon(-0.5)
            self.show_key_feedback('Epsilon  -')
        elif key == self.key_mapping['sigma_increase']:      # r
            self.adjust_sigma(0.2)
            self.show_key_feedback('Sigma  +')
        elif key == self.key_mapping['sigma_decrease']:      # f
            self.adjust_sigma(-0.2)
            self.show_key_feedback('Sigma  -')
        elif key == self.key_mapping['delta_increase']:      # t
            self.adjust_delta(1 / 60.0)
            self.show_key_feedback('Delta  +')
        elif key == self.key_mapping['delta_decrease']:      # g
            self.adjust_delta(-1 / 60.0)
            self.show_key_feedback('Delta  -')
        elif key == self.key_mapping['speed_increase']:      # y
            self.adjust_speed(0.1)
        elif key == self.key_mapping['speed_decrease']:      # h
            self.adjust_speed(-0.1)
        elif key == self.key_mapping['size_increase']:       # u
            self.adjust_size(0.05)
        elif key == self.key_mapping['size_decrease']:       # j
            self.adjust_size(-0.05)
        elif key == 'a':
            self.adjust_gravity(1.0)
            self.show_key_feedback('Gravity  +')
        elif key == 'up':
            self.adjust_gravity(1.0)
            self.show_key_feedback('Gravity  +')
        elif key == 'down':
            self.adjust_gravity(-1.0)
            self.show_key_feedback('Gravity  -')
        elif key == 'right':
            self.adjust_epsilon(0.5)
            self.show_key_feedback('Epsilon  +')
        elif key == 'left':
            self.adjust_epsilon(-0.5)
            self.show_key_feedback('Epsilon  -')
        elif key == 'spacebar':
            cx = self.pos[0] + self.size[0] / 2
            cy = self.pos[1] + self.size[1] / 2
            self.spawn_molecule_at_touch(type('_T', (), {'pos': (cx, cy)})())
            self.show_key_feedback('Spawned!')
        return True

    def show_key_feedback(self, text):
        """Flash a label in the centre of the game area for 0.7 s."""
        lbl = self._feedback_label
        lbl.text = f'[b][color=00cfff]{text}[/color][/b]'
        lbl.color = (0, 1, 1, 1)
        Animation.cancel_all(lbl)
        Animation(color=(0, 1, 1, 0), duration=0.7).start(lbl)

    def adjust_gravity(self, change):
        """change gravity value and update the slider"""
        self.gravity = max(0, min(self.gravity + change, 10))
        if self.gravity_slider:
            self.gravity_slider.value = self.gravity

    def adjust_epsilon(self, change):
        """change epsilon value and update slider"""
        self.epsilon = max(0, min(self.epsilon + change, 10))
        if self.epsilon_slider:
            self.epsilon_slider.value = self.epsilon

    def adjust_sigma(self, change):
        """change sigma value and update slider"""
        self.sigma = max(0.1, min(self.sigma + change, 3))
        if self.sigma_slider:
            self.sigma_slider.value = self.sigma

    def adjust_delta(self, change):
        """change timestep value and update slider"""
        self.delta = max(1 / 600, min(self.delta + change, 1))
        if self.delta_slider:
            self.delta_slider.value = self.delta

    def adjust_speed(self, change):
        """change simulation speed and update slider"""
        new_speed = max(0.1, min(self.speed_slider.value + change, 1)) if self.speed_slider else 1.0

        # change speed slider and set up schedule again with new time
        if self.speed_slider:
            self.speed_slider.value = new_speed
        
        self.set_speed(new_speed)
        
    def adjust_size(self, change):
        """change size factor and update slider"""
        self.size_factor = max(0.2, min(self.size_factor + change, 1))
        if self.size_slider:
            self.size_slider.value = self.size_factor
            
        self.molecule_radius = self.size[0] * self.molecule_radius_ratio * self.size_factor
        for molecule in self.molecules:
            molecule.fix_radius(self.molecule_radius)

    def create_bond(self, molecule1, molecule2):
        """create a bond line between two molecules"""
        if (molecule1, molecule2) not in self.bonds and (molecule2, molecule1) not in self.bonds:

        # make a line between the molecules
            with self.canvas:
                line = Line(points=[molecule1.center_x, molecule1.center_y, molecule2.center_x, molecule2.center_y], width=2)
                self.bonds[(molecule1, molecule2)] = line

    def remove_bond(self, molecule1, molecule2):
        """delete a bond between two molecules"""
        if (molecule1, molecule2) in self.bonds:
            bond = (molecule1, molecule2)
        elif (molecule2, molecule1) in self.bonds:
            bond = (molecule2, molecule1)
        else:
            return False
        
        self.canvas.remove(self.bonds[bond])
        del self.bonds[bond]
        return True
            
    def clear_bonds(self):
        """remove all bonds from the canvas"""
        for bond, line in self.bonds.items():
            self.canvas.remove(line)
        self.bonds.clear()
    
    def periodic_cleanup(self, dt):
        """clean up memory every so often so it doesnt get bloated"""
        try:
            # run garbage collection
            gc.collect()
            
            # if there are no molecules clean up the canvas
            if len(self.molecules) == 0:
                self.canvas.clear()
                # redraw the background
                with self.canvas.before:
                    Color(0, 0, 0, 1)
                    self.rect = Rectangle(pos=self.pos, size=self.size)
            
            print(f"[DEBUG] cleanup: {len(self.molecules)} molecules, {len(self.bonds)} bonds")
        except Exception as e:
            print(f"[WARNING] cleanup failed: {e}")

    def update_bond_lines(self):
        """update where all the bond lines are drawn"""
        with self.canvas:
            Color(0.4, 0.85, 1.0, 0.65)  # Cyan glow instead of flat white
            for bond in self.bonds:
                line = self.bonds[bond]
                line.points = [bond[0].center_x, bond[0].center_y, bond[1].center_x, bond[1].center_y]
                
    def apply_spring_force(self):
        """apply spring forces to bonded molecules"""
        for molecule1, molecule2 in self.bonds:
            # figure out spring force between molecules (Hooke's law)
            r12 = Vector(molecule2.center_x - molecule1.center_x, molecule2.center_y - molecule1.center_y)
            distance = r12.length()
            
            if distance > 0:
                # spring constant and equilibrium distance
                k_spring = 0.5
                r_eq = 100
                force_magnitude = k_spring * (distance - r_eq)
                force_vector = (force_magnitude / distance) * r12
                # push them apart or together
                molecule1.add_force(-force_vector)
                molecule2.add_force(force_vector)

    def update_rect(self, instance, value):
        # save where we were
        self.old_pos = self.pos_in_between[:]
        self.old_size = self.size_in_between[:]

        # Print current and new sizes and positions
        # print(f"Previous pos: {self.old_pos}, Previous size: {self.old_size}")
        # print(f"New pos: {self.pos}, New size: {self.size}")
        # print(f"Updating because of: {instance} with value: {value}")

        # save the new pos/size for next time
        self.pos_in_between = self.pos[:]
        self.size_in_between = self.size[:]

        # move the rect to match
        self.rect.pos = self.pos
        self.rect.size = self.size
        
        self.canvas.ask_update()
        
        self.molecule_radius = self.size[0] * self.molecule_radius_ratio * self.size_factor
        # Call the resize logic
        self.on_resize()

    def on_touch_down(self, touch):
        # if self.is_safe_touch(touch):
        #     self.spawn_molecule_at_touch(touch)
        # return
        """when user touches screen, select a molecule or create a bond between them"""
        
        selected_molecule = None

        # if touch near a molecule, maybe select it
        for molecule in self.molecules:
            if Vector(touch.pos).distance(molecule.center) <= molecule.radius * 2:
                selected_molecule = molecule
                break

        if selected_molecule:
            if self.selected_molecule:
                # First molecule selected
                if not self.remove_bond(selected_molecule, self.selected_molecule):
                    self.create_bond(selected_molecule, self.selected_molecule)
                self.selected_molecule = None
            else:
                self.selected_molecule = selected_molecule
        else:
            # If no molecule is selected, spawn a new molecule at the touch position
            if self.is_safe_touch(touch):
                self.spawn_molecule_at_touch(touch)
            self.selected_molecule = None

    def is_safe_touch(self, touch):
        """
        Check if the touch is within safe bounds to prevent the molecule from extending past the edges.
        """
        safe_margin_x = self.molecule_radius
        safe_margin_y = self.molecule_radius

        return (
            self.pos[0] + safe_margin_x <= touch.x <= self.right - safe_margin_x and
            self.pos[1] + safe_margin_y <= touch.y <= self.top - safe_margin_y
        )

    def spawn_molecule_at_touch(self, touch):
        """spawn a mol at touch with random velocity"""
        # pick random direction
        angle = uniform(-math.pi, math.pi)
        
        
        vx = 300 * math.cos(angle)
        vy = 300 * math.sin(angle)
        
        molecule = Molecule(molecule_center=(touch.pos[0] + 50 - self.molecule_radius, touch.pos[1] + 50 - self.molecule_radius), molecule_radius=self.molecule_radius, molecule_vx=vx, molecule_vy=vy,
                    parent_pos=self.pos[:], parent_size=self.size[:], forces_visible=self.forces_visible)

        molecule.update_color_based_on_speed()  # update color based on how fast its going
        self.add_widget(molecule)
        self.molecules.append(molecule)
        
    def start_simulation(self):
        """start the update loop"""
        if not self.simulation_running:
            self.simulation_running = True
            self._base_interval = 1 / 30.0
            self._current_interval = self._base_interval * self._governor_multiplier
            self.update_event = Clock.schedule_interval(self.update, self._current_interval)

    def stop_simulation(self):
        """stop the update loop"""
        if self.simulation_running:
            self.simulation_running = False
            if self.update_event is not None:
                self.update_event.cancel()
                self.update_event = None
            
            # clean up memory when we stop
            gc.collect()

    def set_speed(self, speed_factor):
        """change simulation speed"""
        self._speed_factor = max(0.1, float(speed_factor))
        self._base_interval = (1 / 30.0) / self._speed_factor
        self._apply_update_interval()

    def _apply_update_interval(self):
        """apply the interval based on governor settings"""
        effective = self._base_interval * self._governor_multiplier
        if self.update_event is not None:
            try:
                self.update_event.cancel()
            except Exception:
                pass
        self._current_interval = effective
        self.update_event = Clock.schedule_interval(self.update, effective)
        
    def set_size(self, size_factor):
        """Adjust the simulation speed by setting a new interval."""
        # set up schedule with new time based on the speed
        self.size_factor = size_factor
        self.molecule_radius = self.size[0] * self.molecule_radius_ratio * self.size_factor
        for molecule in self.molecules:
            molecule.fix_radius(self.molecule_radius)
            
    def toggle_update_mode(self):
        self.use_verlet = not self.use_verlet


    # 
    def update(self, dt):   # update take data ==> send thsi to monitor for performance
        """
        Update molecule positions, handle collisions, and update bonds.
        Arduino integration affects: gravity, kinetic energy, temperature, and pressure.
        """
        total_energy = 0
        temperature = 0
        pressure = 0

        # grab arduino shake data and figure out how much to scale by
        arduino_data = self.arduino.get_xyz() if self.arduino else None
        if arduino_data:
            x, y, z = arduino_data
            accel_magnitude = (x**2 + y**2 + z**2) ** 0.5
            # MPU6050 at rest reads ~16384 per axis at 1g
            # Scale factor: 1.0 = normal gravity, >1.0 = shaking/movement
            scale_factor = max(accel_magnitude / 16384.0, 0.1)  # Minimum 0.1 to avoid zero

                # figure out shake intensity from how fast things are changing
            if self._prev_accel is not None:
                prev_x, prev_y, prev_z = self._prev_accel
                # Measure how much each axis changed (delta)
                delta_x = abs(x - prev_x)
                delta_y = abs(y - prev_y)
                delta_z = abs(z - prev_z)
                
                # total shake = quick acceleration changes
                shake_delta = (delta_x**2 + delta_y**2 + delta_z**2) ** 0.5
                
                # Scale to 0-100 with better calibration
                # normal is like 10-50, shaking is 100-2000
                # use like a log scale thing for the crazy range
                if shake_delta < 20:
                    # Very stable - almost no shake
                    shake_raw = 0
                elif shake_delta < 100:
                    # Minimal movement - map 20-100 to 0-20%
                    shake_raw = (shake_delta - 20) / 4.0
                elif shake_delta < 500:
                    # Light to moderate shake - map 100-500 to 20-50%
                    shake_raw = 20 + (shake_delta - 100) * 0.075
                else:
                    # Strong shake - map 500+ to 50-100%
                    shake_raw = 50 + min((shake_delta - 500) * 0.05, 50)
                
                # Cap at 100
                shake_raw = min(shake_raw, 100)
                
                # smooth it out but still snappy
                self.arduino_activity = 0.5 * self.arduino_activity + 0.5 * shake_raw
            else:
                # first time - no old data yet
                self.arduino_activity = 0
            
                # save current reading for next compare
                self._prev_accel = (x, y, z)

            # set gravity based on shaking
            self.gravity = 9.8 * scale_factor
            
            # show shake on the label
            self.arduino_data_label.text = (
                f"Arduino X: {x:.0f}\n"
                f"Arduino Y: {y:.0f}\n"
                f"Arduino Z: {z:.0f}\n"
                f"Shake Intensity: {self.arduino_activity:.0f}%"
            )
            
            # Feed shake intensity to graph along with raw values
            if self.arduino_graph:
                self.arduino_graph.feed_arduino(x, y, z, self.arduino_activity)

            # dont spam console with logging
            self._arduino_log_accum += dt
            if self._arduino_log_accum >= 1.0:
                print(f"Arduino → X:{x:.2f}, Y:{y:.2f}, Z:{z:.2f}, Scale:{scale_factor:.2f}")
                self._arduino_log_accum = 0.0
        else:
            # no arduino so just use normal gravity
            scale_factor = 1.0

        for molecule in self.molecules:
            molecule.reset_total_force()
            molecule.add_force(Vector(0, -self.gravity))

        # only resize molecules when the radius actually changes (slider moved or window resized)
        # fix_radius was being called every frame for every molecule before - thats why it was so laggy!
        new_radius = self.size[0] * self.molecule_radius_ratio * self.size_factor
        if abs(new_radius - self._last_molecule_radius) > 0.1:
            self.molecule_radius = new_radius
            self._last_molecule_radius = new_radius
            for mol in self.molecules:
                mol.fix_radius(self.molecule_radius)
        self.apply_spring_force()

        self.frame_counter += 1
        if self.frame_counter % 5 == 0:  # update bond lines every 5 frames
            self.update_bond_lines()
        if self.frame_counter % 10 == 0:
            visible = random.sample(self.molecules, min(len(self.molecules), 10))  # just update 10
            for molecule in visible:
                molecule.update_color_based_on_speed()
                if self.forces_visible:
                    molecule.update_force_arrow()
            # update bonds too
            self.update_bond_lines()


        # figure out cutoff distance squared if needed
        if self.enable_lj_cutoff:
            cutoff_dist = (self.lj_cutoff_sigma * self.sigma * self.scale)
            cutoff2 = cutoff_dist * cutoff_dist
        else:
            cutoff2 = None

        for i in range(len(self.molecules)):
            molecule1 = self.molecules[i]
            for j in range(i + 1, len(self.molecules)):
                molecule2 = self.molecules[j]
                # quick check - if boxes dont overlap skip the hard stuff
                dx = molecule2.center_x - molecule1.center_x
                dy = molecule2.center_y - molecule1.center_y
                sum_r = (molecule1.width + molecule2.width) * 0.5
                if abs(dx) <= sum_r and abs(dy) <= sum_r and molecule1.collide_widget(molecule2):
                    molecule1.resolve_collision(molecule2)
                    molecule1.update_color_based_on_speed()
                    molecule2.update_color_based_on_speed()
                if self.intermolecular_forces:
                    # skip if theyre too far away
                    if cutoff2 is not None:
                        r2 = dx*dx + dy*dy
                        if r2 > cutoff2:
                            continue
                    force = molecule1.lennard_jones_force(molecule2, self.epsilon, self.sigma, self.scale)
                    molecule1.add_force(force)
                    molecule2.add_force(-force)
            # change force arrows less often
            if self.forces_visible and (self.frame_counter % self.arrow_update_every == 0):
                molecule1.update_force_arrow()
            if self.use_verlet:
                molecule1.speed_cap = 500
                molecule1.move(self.delta)
            else:
                molecule1.speed_cap = 8
                molecule1.move_nonVerlet()

            # Physics calculations with Arduino scale factor applied
            # turn pixel speeds to normal units
            # pixels are like 0-500 per frame so normalize that down
            velocity_magnitude = molecule1.total_velocity.length()
            normalized_velocity = velocity_magnitude / 50.0  # Scale down by 50x
            
            # Kinetic Energy: KE = 0.5 * m * v^2 (mass assumed = 1)
            kinetic_energy = 0.5 * (normalized_velocity ** 2)
            
            # Total Energy: includes kinetic energy amplified by Arduino movement
            # Arduino shaking adds energy (simulates external heating/vibration)
            total_energy += kinetic_energy * scale_factor
            
            # temp is just how much molecules move around
            # more movement = higher temp
            temperature += kinetic_energy * scale_factor
            
            # pressure is when they smash into walls
            # sum up speed and thats it
            momentum = (abs(molecule1.total_velocity.x) + abs(molecule1.total_velocity.y)) / 50.0
            pressure += momentum * scale_factor

        # show all the stuff we figured out
        num_molecules = len(self.molecules) if len(self.molecules) > 0 else 1
        avg_temperature = temperature / num_molecules  # available to mission tick every frame

        if self.frame_counter % self.ui_update_every == 0:
            # Total Energy: arbitrary units (AU), realistic scale 0-1000
            self.total_energy_label.text = f"Total Energy: {total_energy:.2f}"

            # Temperature: Kelvin-like units, realistic molecular scale
            self.temperature_label.text = f"Temperature: {avg_temperature:.2f}"
            
            # Pressure: how hard molecules hit walls (doesnt mean physicsreal units)
            self.pressure_label.text = f"Pressure: {pressure:.2f}"
        # change bond lines after molecules move
        # self.update_bond_lines()
        # memMb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024.0/1024.0
        # print ("%5.1f MByte" % (memMb))
        
        # # Get current process
        # process = psutil.Process(os.getpid())

        # # Measure CPU usage of this process
        # cpu_usage = process.cpu_percent(interval=0)
        # print(f"Python Process CPU Usage: {cpu_usage}%")
        
        # process = psutil.Process()
        # current_memory = process.memory_info().rss  # In bytes
        # print(f"Current memory usage: {current_memory / (1024 * 1024)} MB")

        # make speedometer show all the stuff
        self.performance_monitor.update_simulation_metrics(
            molecule_count=len(self.molecules),
            gravity=self.gravity,
            epsilon=self.epsilon,
            speed=self.speed_slider.value if self.speed_slider else 1.0,
            forces_on=self.intermolecular_forces,
            arduino_activity=self.arduino_activity,
            total_energy=total_energy
        )
        # accumulate time for whatever time-based stuff is going on
        self._sec_accum += dt

        # pass to mission system whats happening now
        if self.mission_manager and self.mission_manager.state == 'active':
            self.mission_manager.tick(dt, avg_temperature, self.performance_monitor.get_cpu_usage(), len(self.molecules))


        # self.performance_monitor.trigger_boost(15)  # Boost per update
        
        # process = psutil.Process()
        
        # CPU Usage (Total system % and current process %)
        # total_cpu = psutil.cpu_percent(interval=0)  # Total CPU usage across all cores
        # process_cpu = process.cpu_percent(interval=0)  # This process CPU usage

        # RAM Usage (in MB)
        # total_memory = psutil.virtual_memory().percent / (1024 * 1024)  # Total system RAM used
        # process_memory = process.memory_info().rss / (1024 * 1024)  # This process RAM usage

        # print(f"Total CPU Usage: {total_cpu:.2f}% | Total RAM Usage: {total_memory:.2f} MB")
        # print(f"Process CPU Usage: {process_cpu:.2f}% | Process RAM Usage: {process_memory:.2f} MB")

    def on_resize(self):
        # when window gets bigger/smaller, rescale molecule stuff
        for molecule in self.molecules:
            molecule.rescale_position(self.pos[:], self.size[:])
            molecule.fix_radius(self.molecule_radius)
    # 
    def set_gravity(self, value):
        """Update gravity for all molecules based on slider value."""
        self.gravity = value
        # for molecule in self.molecules:
        #     molecule.gravity = self.gravity

    def set_epsilon(self, value):
        """Update the epsilon parameter for Lennard-Jones potential."""
        self.epsilon = value

    def set_sigma(self, value):
        """Update the sigma parameter for Lennard-Jones potential."""
        self.sigma = value
        
    def set_delta(self, value):
        """Update the timestep for Verlet integration."""
        self.delta = value

    def toggle_intermolecular_forces(self):
        """Toggle intermolecular forces on or off."""
        self.intermolecular_forces = not self.intermolecular_forces

    def toggle_forces_visible(self):
        """Toggle intermolecular forces on or off."""
        self.forces_visible = not self.forces_visible
        # say if force arrows show for this molecule
        for molecule in self.molecules:
            molecule.forces_visible = self.forces_visible
            molecule.update_force_arrow()

    # --- Gentle CPU governor ---
    def _governor_update(self, dt):
        """adjust update rate based on cpu usage"""
        try:
            cpu = self.performance_monitor.get_cpu_usage()
        except Exception:
            return
        threshold = 90.0
        if cpu >= threshold:
            self._governor_high_time += dt
            self._governor_low_time = 0.0
        else:
            self._governor_low_time += dt
            self._governor_high_time = 0.0

        # Enter throttle after 2 seconds high CPU
        if self._governor_state == 'normal' and self._governor_high_time >= 2.0:
            self._governor_state = 'throttle'
            self._governor_multiplier = 1.25
            # Hide arrows while throttling (remember if we changed it)
            if self.forces_visible:
                self._forces_hidden_by_governor = True
                self.forces_visible = False
            self._apply_update_interval()

        # Exit throttle after 5 seconds low CPU
        if self._governor_state == 'throttle' and self._governor_low_time >= 5.0:
            self._governor_state = 'normal'
            self._governor_multiplier = 1.0
            if self._forces_hidden_by_governor:
                self.forces_visible = True
                self._forces_hidden_by_governor = False
            self._apply_update_interval()

    def _apply_physics_preset(self, gravity, epsilon, sigma):
        """Set gravity, epsilon and sigma and sync their sliders."""
        self.set_gravity(gravity)
        self.set_epsilon(epsilon)
        self.set_sigma(sigma)
        if self.gravity_slider:
            self.gravity_slider.value = gravity
        if self.epsilon_slider:
            self.epsilon_slider.value = epsilon
        if self.sigma_slider:
            self.sigma_slider.value = sigma

    def generate_solid(self):
        """make a solid-like arrangement of molecules"""
        # Strong bonds (high epsilon), tight packing (low sigma), no gravity
        self._apply_physics_preset(gravity=0, epsilon=5.0, sigma=0.8)

        self.clear_molecules()
        rows, cols = 11, 25
        spacing_x = self.size[0] * 0.039
        spacing_y = self.size[1] * 0.09
        start_x = self.pos[0] + spacing_x
        start_y = self.pos[1] + spacing_y

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y
                self.create_molecule(x, y, 0, 0)

    def generate_liquid(self):
        """make a liquid-like arrangement"""
        try:
            if hasattr(self.performance_monitor, 'trigger_boost'):
                self.performance_monitor.trigger_boost(40.0)
        except Exception:
            print("[Slider boost error] trigger_boost unavailable")

        # medium attraction, normal spacing, gravity pulls down
        self._apply_physics_preset(gravity=3.0, epsilon=2.0, sigma=1.0)

        self.clear_molecules()
        for _ in range(50):
            x = uniform(self.pos[0] + 50, self.pos[0] + self.size[0] - 50)
            y = uniform(self.pos[1] + 50, self.pos[1] + self.size[1] - 50)
            vx = uniform(-50, 50)
            vy = uniform(-50, 50)
            self.create_molecule(x, y, vx, vy)

    def generate_gas(self):
        """make a gas-like arrangement"""
        try:
            if hasattr(self.performance_monitor, 'trigger_boost'):
                self.performance_monitor.trigger_boost(40.0)
        except Exception:
            print("[Slider boost error] trigger_boost unavailable")

        # Weak interactions (low epsilon), large spacing (high sigma), minimal gravity
        self._apply_physics_preset(gravity=0.5, epsilon=0.3, sigma=1.5)

        self.clear_molecules()
        for _ in range(15):
            x = uniform(self.pos[0] + 50, self.pos[0] + self.size[0] - 50)
            y = uniform(self.pos[1] + 50, self.pos[1] + self.size[1] - 50)
            vx = uniform(-300, 300)
            vy = uniform(-300, 300)
            self.create_molecule(x, y, vx, vy)

    def clear_molecules(self):
        """remove all molecules from the game"""
        for molecule in self.molecules:
            self.remove_widget(molecule)
        self.molecules.clear()
        gc.collect()

        # self.performance_monitor.simulation_load = 0.0 # to clear molecules back to normal
    
    def create_molecule(self, x, y, vx, vy):
        """make and add a molecule to the game"""
        molecule = Molecule(
            molecule_center=(x, y),
            molecule_radius=self.size[0] * self.molecule_radius_ratio * self.size_factor,
            molecule_vx=vx,
            molecule_vy=vy,
            parent_pos=self.pos[:],
            parent_size=self.size[:],
            forces_visible=self.forces_visible,
        )
        self.add_widget(molecule)
        self.molecules.append(molecule)
