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



# TO DO LIST 
# Import ARDUNIO IN HERE after doing all teh c wrapping and all the information when shaking teh 
# arduino the energy shoudl be converted into the scale factor and after being added to teh kinetic energy 
# + scale factor in thsi stype of form and ==> then show thsi as a display on teh side panel 


# Add ardunio reading into teh app itself
# after this make sure to do the force calulation impact for ths cpu

# and the more molecules the higher computational power tahts it!!!

import psutil
import os
import gc


class GameLayout(Widget):

    intermolecular_forces = BooleanProperty(True)  # Toggle for intermolecular forces
    epsilon = NumericProperty(1.0)  # Lennard-Jones potential depth
    sigma = NumericProperty(1.0)  # Lennard-Jones potential sigma
    spring_constant = 100.0
    spring_rest_length = 2.0
    molecule_radius_ratio = 0.03
    use_verlet = True
    

    def __init__(self, performance_monitor, **kwargs):
        super(GameLayout, self).__init__(**kwargs)
        # self.arduino = ArduinoReading('/dev/ttyUSB0')  # open serial once!!!! below connects twice and more
        try:
            self.arduino = ArduinoReading('/dev/ttyUSB0')
        except Exception as e:
            print(f"[WARNING] Arduino not connected: {e}")
            self.arduino = None


        with self.canvas.before:
            Color(0, 0, 0, 1)  # Set background color of the game area (black)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

        self.frame_counter = 0   # added this to make it less
        self.performance_monitor = performance_monitor

        self.molecules = []  # List of all molecules in the game        
        Clock.schedule_interval(self.monitor_performance, 1)
        set_global_monitor(self.performance_monitor) 

        

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

        # data from arduino shown on the screen as letters
        # Will be updated in real time inside the label
        self.arduino_data_label = Label(
            text="Arduino X: 0.00\nArduino Y: 0.00\nArduino Z: 0.00\nGravity Scale: 0.00",
            size_hint=(None, None),
            size=(350, 25),
            # pos=(10, Window.height - 30),
            pos=(-60, 990),
            color=(1, 1, 1, 1),  # white
            bold=True,
            font_size='16sp',
            halign='left',
            valign='top'
        )
        self.arduino_data_label.bind(size=self.arduino_data_label.setter('text_size'))
  
        # self.add_widget(self.arduino_data_label)




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
        self.setup_keyboard()
        
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
            self.update_event = Clock.schedule_interval(self.update, 1 / 60.0)  # Default speed at 60 FPS

    def stop_simulation(self):
        """Stop the simulation update loop."""
        if self.simulation_running:
            self.simulation_running = False
            if self.update_event is not None:
                self.update_event.cancel()
                self.update_event = None

    def set_speed(self, speed_factor):
        """Adjust the simulation speed by setting a new interval."""
        if self.update_event is not None:
            self.update_event.cancel()
        
        # Schedule with the new interval based on the speed factor
        new_interval = (1 / 60.0) / speed_factor  # Adjust interval according to speed factor <=== this is used for updatng simulation
        self.update_event = Clock.schedule_interval(self.update, new_interval)
        
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
        """
        total_energy = 0
        # ADD HERE ==> ARDUNO READING this is its initilization ==> added in init method above
        temperature = 0  # added to arduio when shaking + strong amount of shaking scale and small amountof shaking scale
        pressure = 0

        # getting data from arduino here!!!
        # arduino_data = self.arduino.get_xyz()
        arduino_data = self.arduino.get_xyz() if self.arduino else None
        if arduino_data:
            x, y, z = arduino_data
            accel_magnitude = (x**2 + y**2 + z**2) ** 0.5
            scale_factor = accel_magnitude / 16384.0  # MPU6050 normal gravity scale  ?? review

            self.gravity = 9.8 * scale_factor   # shake effect
            self.arduino_data_label.text = (
                    f"Arduino X: {x:.2f}\n"
                    f"Arduino Y: {y:.2f}\n"
                    f"Arduino Z: {z:.2f}\n"
                    f"Gravity Scale: {scale_factor:.2f}"
            )   

            print(f"Arduino Accel → ARDUINO X:{x}, ARDUINO Y:{y}, ARDUINOZ:{z}, Gravity scale: {scale_factor:.2f}")

        else:
            scale_factor = 1 # if no change just keep this way

        for molecule in self.molecules:
            molecule.reset_total_force()
            molecule.add_force(Vector(0, -self.gravity))  
            
        self.molecule_radius = self.size[0] * self.molecule_radius_ratio * self.size_factor
        self.apply_spring_force()

        self.frame_counter += 1
        if self.frame_counter % 10 == 0:
                visible = random.sample(self.molecules, min(len(self.molecules), 10))  # only update 10 molecules
                for molecule in visible:
                    molecule.update_color_based_on_speed()
                    if self.forces_visible:
                        molecule.update_force_arrow()


        for i in range(len(self.molecules)):
            molecule1 = self.molecules[i]
            molecule1.fix_radius(self.molecule_radius)
            for j in range(i + 1, len(self.molecules)):
                molecule2 = self.molecules[j]
                if molecule1.collide_widget(molecule2):
                    molecule1.resolve_collision(molecule2)
                    molecule1.update_color_based_on_speed()
                    molecule2.update_color_based_on_speed()
                if self.intermolecular_forces:  # consider this one for forces update within cpu
                    force = molecule1.lennard_jones_force(molecule2, self.epsilon, self.sigma, self.scale)
                    # print(force, i, j)
                    molecule1.add_force(force)
                    molecule2.add_force(-force)
                    
            molecule1.update_force_arrow()   # in here check !!!
            if self.use_verlet:
                molecule1.speed_cap = 500
                molecule1.move(self.delta)
            else:
                molecule1.speed_cap = 8
                molecule1.move_nonVerlet()

            # Calculate kinetic energy ==> send this 
            kinetic_energy = 0.5 * (molecule1.total_velocity.length2()) * scale_factor
            total_energy += kinetic_energy   # impact  here
            temperature += kinetic_energy  # + scale factor of arduion Temperature proportional to kinetic energy
            #### Here to ADD this is where the scale factor supposed to be 

            pressure += abs(molecule1.total_velocity.x) + abs(molecule1.total_velocity.y)  # Simplified pressure calculation

        self.total_energy_label.text = f"Total Energy: {total_energy:.2f}"  # can change by arduino
        self.temperature_label.text = f"Temperature: {(temperature / len(self.molecules)) if len(self.molecules) else 0:.2f}"
        self.pressure_label.text = f"Pressure: {pressure:.2f}"
        # Update bond lines after molecule movement
        self.update_bond_lines()
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

        self.performance_monitor.update_simulation_metrics(
            molecule_count=len(self.molecules),
            gravity=self.gravity,
            epsilon=self.epsilon,
            speed=self.speed_slider.value if self.speed_slider else 1.0,
            forces_on=self.intermolecular_forces
        )




    
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
        self.performance_monitor.trigger_boost(40.0)

        self.clear_molecules()
        for _ in range(50):  # Create 50 molecules
            x = uniform(self.pos[0] + 50, self.pos[0] + self.size[0] - 50)
            y = uniform(self.pos[1] + 50, self.pos[1] + self.size[1] - 50)
            vx = uniform(-50, 50)
            vy = uniform(-50, 50)
            self.create_molecule(x, y, vx, vy)

    def generate_gas(self):
        """Generate a gas-like arrangement of molecules."""
        self.performance_monitor.trigger_boost(40.0)

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
