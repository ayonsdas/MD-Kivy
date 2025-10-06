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
import serial
import time
import re
from kivy.uix.label import Label
import random
import psutil
import os
import gc


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
            # Respect env overrides and auto-detection logic inside ArduinoReading
            self.arduino = ArduinoReading()
            print(f"[INFO] Arduino serial opened on {self.arduino.port} @ {self.arduino.baud_rate}")
        except Exception as e:
            print(f"[WARNING] Arduino not connected or no permission: {e}")
            print("         Hint: set ARDUINO_PORT=/dev/ttyACM0 and ensure you are in the 'dialout' group, then re-run.")
            self.arduino = None


        with self.canvas.before:
            Color(0, 0, 0, 1)  # Set background color of the game area (black)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.frame_counter = 0   # added this to make it less
        self.performance_monitor = performance_monitor

        self.arduino_graph = arduino_graph

        self.molecules = []  # List of all molecules in the game        
        Clock.schedule_interval(self.monitor_performance, 1)
        set_global_monitor(self.performance_monitor) 

        # --- Smooth performance helpers (low-risk) ---
        self.ui_update_every = 5           # update labels every 5 frames
        self.arrow_update_every = 5        # update force arrows at most every 5 frames
        self._arduino_log_accum = 0.0      # throttle arduino prints to ~1 Hz
        self._sec_accum = 0.0              # generic per-frame time accumulator
        self.arduino_activity = 0.0        # Arduino accelerometer activity (0-100)

        # Gentle CPU governor: slow update interval and hide arrows when CPU is high
        self._governor_state = 'normal'    # 'normal' | 'throttle'
        self._governor_high_time = 0.0     # seconds above threshold
        self._governor_low_time = 0.0      # seconds below threshold
        self._governor_multiplier = 1.0    # 1.0 normal, >1.0 slows updates
        self._forces_hidden_by_governor = False

        # Track scheduling to apply governor without changing user speed semantics
        self._speed_factor = 1.0
        self._base_interval = 1 / 30.0
        self._current_interval = self._base_interval

        # Keyboard should be set up once
        self._keyboard_initialized = False

        # Schedule gentle governor checks
        Clock.schedule_interval(self._governor_update, 0.5)

        self.bonds = {}  # Dictionary to store Line objects for each bond
        # print(self.molecule_radius)
        self.old_pos = self.pos[:]
        self.old_size = self.size[:]
        self.pos_in_between = self.pos[:]
        self.size_in_between = self.size[:]
        self.scale = 10 ** (2)
        self.gravity = 0  # Initialize gravity
        self.delta = 1 / 60.0  # Time step
        self.selected_molecule = None  # Track the first selected molecule for bonding
        self.simulation_running = False  # Track if simulation is running
        self.size_factor = 0.6
        self.molecule_radius = self.size[0] * self.molecule_radius_ratio * self.size_factor # Radius of the molecule
        self.forces_visible = True

        # Safe performance cutoff for Lennard-Jones interactions (standard practice)
        self.enable_lj_cutoff = True
        self.lj_cutoff_sigma = 2.5  # cutoff radius = 2.5 * sigma

        self.arduino_data_label = Label(
            text="Arduino X: 0.00\nArduino Y: 0.00\nArduino Z: 0.00\nGravity Scale: 0.00",
            size_hint=(0.2, 0.15),  # Take up 20% width and 15% height of parent
            pos_hint={"x": 0.02, "top": 0.98},  # Near top-left corner
            color=(1, 1, 1, 1),  # white
            bold=True,
            font_size=Window.height * 0.028,  # 2.8% of screen height (larger for visibility)
            halign='left',
            valign='top'
        )
        self.arduino_data_label.bind(size=self.arduino_data_label.setter('text_size'))

        # self.add_widget(self.arduino_data_label)

    # Spatial hash config removed (reverted to ensure stability)


# Work on this part to log CPU usage and Memory Usage
    def monitor_performance(self, dt):
        cpu_usage = self.performance_monitor.get_cpu_usage()
        atom_count = len(self.molecules)
        print(f"Atoms: {atom_count}, CPU Usage: {cpu_usage:.2f}%")

        # Variable to store the scheduled update event
        # self.update_event = None
        # Labels for stats
        # self.total_energy_label = Label(text="Total Energy: 0", size_hint=(None, None), pos_hint={})
        # self.temperature_label = Label(text="Temperature: 0", size_hint=(None, None), pos_hint={})
        # self.pressure_label = Label(text="Pressure: 0", size_hint=(None, None), pos_hint={})
        # # self.add_widget(self.total_energy_label)
        # self.add_widget(self.temperature_label)
        # self.add_widget(self.pressure_label)
        
        # Key bindings for controlling sliders
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

        # Schedule the update event
        self.update_event = None
        if not self._keyboard_initialized:
            self.setup_keyboard()
            self._keyboard_initialized = True
        
        Clock.schedule_interval(lambda dt: gc.collect(), 5)
        
    def setup_keyboard(self):
        """Initialize keyboard binding for slider controls."""
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down)

    def _keyboard_closed(self):
        """Unbind keyboard events when keyboard is closed."""
        self._keyboard.unbind(on_key_down=self.on_key_down)
        self._keyboard = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        """Handle key press events for controlling sliders."""
        key = keycode[1]
        if key == self.key_mapping['gravity_increase']:
            self.adjust_gravity(0.1)
        elif key == self.key_mapping['gravity_decrease']:
            self.adjust_gravity(-0.1)
        elif key == self.key_mapping['epsilon_increase']:
            self.adjust_epsilon(0.1)
        elif key == self.key_mapping['epsilon_decrease']:
            self.adjust_epsilon(-0.1)
        elif key == self.key_mapping['sigma_increase']:
            self.adjust_sigma(0.05)
        elif key == self.key_mapping['sigma_decrease']:
            self.adjust_sigma(-0.05)
        elif key == self.key_mapping['delta_increase']:
            self.adjust_delta(1 / 60.0)
        elif key == self.key_mapping['delta_decrease']:
            self.adjust_delta(-1 / 60.0)
        elif key == self.key_mapping['speed_increase']:
            self.adjust_speed(0.1)
        elif key == self.key_mapping['speed_decrease']:
            self.adjust_speed(-0.1)
        elif key == self.key_mapping['size_increase']:
            self.adjust_size(0.05)
        elif key == self.key_mapping['size_decrease']:
            self.adjust_size(-0.05)
        return True

    def adjust_gravity(self, change):
        """Adjust gravity by a specified increment and update the slider."""
        self.gravity = max(0, min(self.gravity + change, 10))
        if self.gravity_slider:
            self.gravity_slider.value = self.gravity

    def adjust_epsilon(self, change):
        """Adjust epsilon by a specified increment and update the slider."""
        self.epsilon = max(0, min(self.epsilon + change, 10))
        if self.epsilon_slider:
            self.epsilon_slider.value = self.epsilon

    def adjust_sigma(self, change):
        """Adjust sigma by a specified increment and update the slider."""
        self.sigma = max(0.1, min(self.sigma + change, 3))
        if self.sigma_slider:
            self.sigma_slider.value = self.sigma

    def adjust_delta(self, change):
        """Adjust delta by a specified increment and update the slider."""
        self.delta = max(1 / 600, min(self.delta + change, 1))
        if self.delta_slider:
            self.delta_slider.value = self.delta

    def adjust_speed(self, change):
        """Adjust simulation speed factor by a specified increment and update the slider."""
        new_speed = max(0.1, min(self.speed_slider.value + change, 1)) if self.speed_slider else 1.0

        # Update speed slider and reschedule with new interval
        if self.speed_slider:
            self.speed_slider.value = new_speed
        
        self.set_speed(new_speed)
        
    def adjust_size(self, change):
        """Adjust size by a specified increment and update the slider."""
        self.size_factor = max(0.2, min(self.size_factor + change, 1))
        if self.size_slider:
            self.size_slider.value = self.size_factor
            
        self.molecule_radius = self.size[0] * self.molecule_radius_ratio * self.size_factor
        for molecule in self.molecules:
            molecule.fix_radius(self.molecule_radius)

    def create_bond(self, molecule1, molecule2):
        """Creates a bond between two molecules and a Line object to represent it."""
        if (molecule1, molecule2) not in self.bonds and (molecule2, molecule1) not in self.bonds:

            # Create a Line object for the bond
            with self.canvas:
                line = Line(points=[molecule1.center_x, molecule1.center_y, molecule2.center_x, molecule2.center_y], width=1)
                # Store the line associated with this bond in bond_lines
                self.bonds[(molecule1, molecule2)] = line

    def remove_bond(self, molecule1, molecule2):
        """Removes a bond between two molecules and its associated Line object."""
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
        """Clears all bonds and removes bond lines from the canvas."""
        for bond, line in self.bonds.items():
            self.canvas.remove(line)
        self.bonds.clear()

    def update_bond_lines(self):
        """Update the positions of all bond lines."""
        # Ensure the color is white when updating bond lines
        with self.canvas:
            Color(1, 1, 1, 1)  # Set the color to white
            for bond in self.bonds:
                line = self.bonds[bond]
                line.points = [bond[0].center_x, bond[0].center_y, bond[1].center_x, bond[1].center_y]
                
    def apply_spring_force(self):
        """Apply spring force to all bonded pairs of molecules."""
        for molecule1, molecule2 in self.bonds:
            # Vector between molecule1 and molecule2
            r12 = Vector(molecule2.center_x - molecule1.center_x, molecule2.center_y - molecule1.center_y)
            distance = r12.length()

            # Calculate the spring force using Hooke's law
            force_magnitude = -self.spring_constant * (distance - self.spring_rest_length)

            if distance > 0:
                force_vector = (force_magnitude / distance) * r12  # Normalize the force vector
                # Apply the force to both molecules
                molecule1.add_force(-force_vector)
                molecule2.add_force(force_vector)

    def update_rect(self, instance, value):
        # Store the current position and size before updating
        self.old_pos = self.pos_in_between[:]
        self.old_size = self.size_in_between[:]

        # Print current and new sizes and positions
        # print(f"Previous pos: {self.old_pos}, Previous size: {self.old_size}")
        # print(f"New pos: {self.pos}, New size: {self.size}")
        # print(f"Updating because of: {instance} with value: {value}")

        # Store old size and position for future reference
        self.pos_in_between = self.pos[:]
        self.size_in_between = self.size[:]

        # Update the rectangle position and size
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
        """Handle touch events for creating bonds between two selected molecules."""
        
        selected_molecule = None

        # Check if the touch is near any molecule
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
        """
        Spawn a molecule at the touch position with a random initial velocity.
        """
        # Generate random angle
        angle = uniform(-math.pi, math.pi)
        
        
        vx = 300 * math.cos(angle)
        vy = 300 * math.sin(angle)
        
        molecule = Molecule(molecule_center=(touch.pos[0] + 50 - self.molecule_radius, touch.pos[1] + 50 - self.molecule_radius), molecule_radius=self.molecule_radius, molecule_vx=vx, molecule_vy=vy,
                    parent_pos=self.pos[:], parent_size=self.size[:], forces_visible=self.forces_visible)

        molecule.update_color_based_on_speed()  # Ensure the color is updated based on initial speed
        self.add_widget(molecule)
        self.molecules.append(molecule)
        
    def start_simulation(self):
        """Start the simulation update loop."""
        if not self.simulation_running:
            self.simulation_running = True
            self._base_interval = 1 / 30.0
            self._current_interval = self._base_interval * self._governor_multiplier
            self.update_event = Clock.schedule_interval(self.update, self._current_interval)

    def stop_simulation(self):
        """Stop the simulation update loop."""
        if self.simulation_running:
            self.simulation_running = False
            if self.update_event is not None:
                self.update_event.cancel()
                self.update_event = None

    def set_speed(self, speed_factor):
        """Adjust the simulation speed by setting a new interval."""
        self._speed_factor = max(0.1, float(speed_factor))
        self._base_interval = (1 / 30.0) / self._speed_factor
        self._apply_update_interval()

    def _apply_update_interval(self):
        """Apply effective interval considering governor multiplier."""
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
        # Schedule with the new interval based on the speed factor
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

        # Get Arduino accelerometer data and calculate scale factor
        arduino_data = self.arduino.get_xyz() if self.arduino else None
        if arduino_data:
            x, y, z = arduino_data
            accel_magnitude = (x**2 + y**2 + z**2) ** 0.5
            # MPU6050 at rest reads ~16384 per axis at 1g
            # Scale factor: 1.0 = normal gravity, >1.0 = shaking/movement
            scale_factor = max(accel_magnitude / 16384.0, 0.1)  # Minimum 0.1 to avoid zero

            # Update gravity based on Arduino acceleration
            self.gravity = 9.8 * scale_factor
            
            self.arduino_data_label.text = (
                f"Arduino X: {x:.2f}\n"
                f"Arduino Y: {y:.2f}\n"
                f"Arduino Z: {z:.2f}\n"
                f"Gravity Scale: {scale_factor:.2f}"
            )
            
            if self.arduino_graph:
                self.arduino_graph.feed_arduino(x, y, z)

            # Store Arduino activity for later use in speedometer calculation
            # Don't directly set target here - let update_simulation_metrics combine it
            self.arduino_activity = min((accel_magnitude / 16384.0) * 100, 100)

            # Throttle logging to ~1 Hz to avoid console flood
            self._arduino_log_accum += dt
            if self._arduino_log_accum >= 1.0:
                print(f"Arduino → X:{x:.2f}, Y:{y:.2f}, Z:{z:.2f}, Scale:{scale_factor:.2f}")
                self._arduino_log_accum = 0.0
        else:
            # No Arduino data - use baseline values
            scale_factor = 1.0

        for molecule in self.molecules:
            molecule.reset_total_force()
            molecule.add_force(Vector(0, -self.gravity))  
            
        self.molecule_radius = self.size[0] * self.molecule_radius_ratio * self.size_factor
        self.apply_spring_force()

        self.frame_counter += 1
        if self.frame_counter % 5 == 0:  # Only update bond lines every 5 frames
            self.update_bond_lines()
        if self.frame_counter % 10 == 0:
            visible = random.sample(self.molecules, min(len(self.molecules), 10))  # only update 10 molecules
            for molecule in visible:
                molecule.update_color_based_on_speed()
                if self.forces_visible:
                    molecule.update_force_arrow()
            # Update bonds once after batch
            self.update_bond_lines()


        # Precompute LJ cutoff distance squared (in screen units) if enabled
        if self.enable_lj_cutoff:
            cutoff_dist = (self.lj_cutoff_sigma * self.sigma * self.scale)
            cutoff2 = cutoff_dist * cutoff_dist
        else:
            cutoff2 = None

        for i in range(len(self.molecules)):
            molecule1 = self.molecules[i]
            molecule1.fix_radius(self.molecule_radius)
            for j in range(i + 1, len(self.molecules)):
                molecule2 = self.molecules[j]
                # Cheap broad-phase: skip expensive checks when boxes don't overlap
                dx = molecule2.center_x - molecule1.center_x
                dy = molecule2.center_y - molecule1.center_y
                sum_r = (molecule1.width + molecule2.width) * 0.5
                if abs(dx) <= sum_r and abs(dy) <= sum_r and molecule1.collide_widget(molecule2):
                    molecule1.resolve_collision(molecule2)
                    molecule1.update_color_based_on_speed()
                    molecule2.update_color_based_on_speed()
                if self.intermolecular_forces:
                    # Apply distance cutoff for LJ to skip far pairs
                    if cutoff2 is not None:
                        r2 = dx*dx + dy*dy
                        if r2 > cutoff2:
                            continue
                    force = molecule1.lennard_jones_force(molecule2, self.epsilon, self.sigma, self.scale)
                    molecule1.add_force(force)
                    molecule2.add_force(-force)
            # Update per-molecule force arrows less frequently
            if self.forces_visible and (self.frame_counter % self.arrow_update_every == 0):
                molecule1.update_force_arrow()
            if self.use_verlet:
                molecule1.speed_cap = 500
                molecule1.move(self.delta)
            else:
                molecule1.speed_cap = 8
                molecule1.move_nonVerlet()

            # Physics calculations with Arduino scale factor applied
            # Convert screen-space velocities to normalized physics units
            # Typical velocity range: 0-500 pixels/frame → normalize to 0-10 units
            velocity_magnitude = molecule1.total_velocity.length()
            normalized_velocity = velocity_magnitude / 50.0  # Scale down by 50x
            
            # Kinetic Energy: KE = 0.5 * m * v^2 (mass assumed = 1)
            kinetic_energy = 0.5 * (normalized_velocity ** 2)
            
            # Total Energy: includes kinetic energy amplified by Arduino movement
            # Arduino shaking adds energy (simulates external heating/vibration)
            total_energy += kinetic_energy * scale_factor
            
            # Temperature: proportional to average kinetic energy per molecule
            # In physics: T ∝ <KE>, higher values = more molecular motion
            temperature += kinetic_energy * scale_factor
            
            # Pressure: momentum transfers with walls (velocity × mass)
            # Simplified as sum of velocity components, normalized
            momentum = (abs(molecule1.total_velocity.x) + abs(molecule1.total_velocity.y)) / 50.0
            pressure += momentum * scale_factor

        # Update labels with calculated, realistic values
        num_molecules = len(self.molecules) if len(self.molecules) > 0 else 1
        
        if self.frame_counter % self.ui_update_every == 0:
            # Total Energy: arbitrary units (AU), realistic scale 0-1000
            self.total_energy_label.text = f"Total Energy: {total_energy:.2f}"
            
            # Temperature: Kelvin-like units, realistic molecular scale
            # Typical range: 0-500K depending on molecular motion
            avg_temperature = temperature / num_molecules
            self.temperature_label.text = f"Temperature: {avg_temperature:.2f}"
            
            # Pressure: arbitrary units (AU), represents wall collisions
            # Higher values = more frequent/forceful collisions
            self.pressure_label.text = f"Pressure: {pressure:.2f}"
        # Update bond lines after molecule movement
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

        # Update speedometer with comprehensive metrics including Arduino and energy
        self.performance_monitor.update_simulation_metrics(
            molecule_count=len(self.molecules),
            gravity=self.gravity,
            epsilon=self.epsilon,
            speed=self.speed_slider.value if self.speed_slider else 1.0,
            forces_on=self.intermolecular_forces,
            arduino_activity=self.arduino_activity,
            total_energy=total_energy
        )
        # Accumulate dt for any time-based features
        self._sec_accum += dt


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
        # When the game layout is resized, rescale molecules' positions
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
        # Set whether force arrows should be visible for this molecule
        for molecule in self.molecules:
            molecule.forces_visible = self.forces_visible
            molecule.update_force_arrow()

    # --- Gentle CPU governor ---
    def _governor_update(self, dt):
        """Adjust update rate and arrow visibility based on CPU usage."""
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

    def generate_solid(self):
        """Generate a solid-like arrangement of molecules."""
        # self.performance_monitor.trigger_boost(40.0)   # added to help it

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
        """Generate a liquid-like arrangement of molecules."""
        try:
            if hasattr(self.performance_monitor, 'trigger_boost'):
                self.performance_monitor.trigger_boost(40.0)
        except Exception:
            print("[Slider boost error] trigger_boost unavailable")

        self.clear_molecules()
        for _ in range(50):  # Create 50 molecules
            x = uniform(self.pos[0] + 50, self.pos[0] + self.size[0] - 50)
            y = uniform(self.pos[1] + 50, self.pos[1] + self.size[1] - 50)
            vx = uniform(-50, 50)
            vy = uniform(-50, 50)
            self.create_molecule(x, y, vx, vy)

    def generate_gas(self):
        """Generate a gas-like arrangement of molecules."""
        try:
            if hasattr(self.performance_monitor, 'trigger_boost'):
                self.performance_monitor.trigger_boost(40.0)
        except Exception:
            print("[Slider boost error] trigger_boost unavailable")

        self.clear_molecules()
        for _ in range(15):  # Create 30 molecules
            x = uniform(self.pos[0] + 50, self.pos[0] + self.size[0] - 50)
            y = uniform(self.pos[1] + 50, self.pos[1] + self.size[1] - 50)
            vx = uniform(-200, 200)
            vy = uniform(-200, 200)
            self.create_molecule(x, y, vx, vy)

    def clear_molecules(self):
        """Clear all molecules from the canvas and list."""
        for molecule in self.molecules:
            self.remove_widget(molecule)
        self.molecules.clear()
        gc.collect()

        # self.performance_monitor.simulation_load = 0.0 # to clear molecules back to normal
    
    def create_molecule(self, x, y, vx, vy):
        """Create and add a molecule to the game layout."""
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
