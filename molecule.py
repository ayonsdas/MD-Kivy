from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
import math

class Molecule(Widget):
    # gravity = NumericProperty(0)  # Gravity value affecting the molecule
    color_slow = [5, 0, 102, 255]
    color_fast = [255, 81, 220, 255]
    color = ListProperty([x / 255 for x in color_fast])  # Initial color is red (RGBA)
    speed_cap = 500
    force_cap = 30000

    def __init__(self, **kwargs):
        
        self.center = kwargs.pop("molecule_center")
        self.radius = kwargs.pop("molecule_radius")
        self.total_velocity = Vector(kwargs.pop("molecule_vx"), kwargs.pop("molecule_vy"))
        
        self.parentpos = kwargs.pop("parent_pos")
        self.parentsize = kwargs.pop("parent_size")
        self.forces_visible = kwargs.pop("forces_visible")
        
        super().__init__(**kwargs)
        
        self.size = (self.radius * 2, self.radius * 2)  # Define the size of the molecule
        self.total_force = Vector(0, 0)
        
        with self.canvas:
            self.color_instruction = Color(*self.color)  # Set initial color
            self.molecule_shape = Ellipse(pos=self.pos, size=self.size)  # Set initial position and size
            self.arrow_color = Color(0, 0, 1, 1)  # Blue for initial arrow color
            self.arrow_line = Line(points=[], width=4 * self.radius / 10)  # Arrow to represent force
            
    def fix_speed(self):
        
        if self.total_velocity.length() > self.speed_cap:
            self.total_velocity *= self.speed_cap / self.total_velocity.length()
            
    def fix_force(self):
        
        if self.total_force.length() > self.force_cap:
            self.total_force *= self.force_cap / self.total_force.length()

    def fix_radius(self, new_radius):
        self.pos = (self.pos[0] - new_radius + self.radius, self.pos[1] - new_radius + self.radius)
        self.radius = new_radius
        self.size = (self.radius * 2, self.radius * 2)
        self.canvas.clear()
        with self.canvas:
            self.color_instruction = Color(*self.color)  # Set initial color
            self.molecule_shape = Ellipse(pos=self.pos, size=self.size)  # Set initial position and size
            self.arrow_color = Color(0, 0, 1, 1)  # Blue for initial arrow color
            self.arrow_line = Line(points=[], width=4 * self.radius / 20)  # Arrow to represent force

    def move(self, delta):   # For Verlet integration
        
        self.fix_force()
        ####  ## Verlet integration
        self.pos = self.total_velocity * delta + 0.5 * self.total_force * (delta ** 2) + self.pos
        self.molecule_shape.pos = (self.pos[0] - self.radius, self.pos[1] - self.radius) # Update the molecule's position in the canvas
        self.bounce_off_walls()
        
        self.total_velocity += self.total_force * delta   #can chnage velocity for the testing purposes
        self.fix_speed()
        
        # print(self.total_force.length())
        
        self.update_color_based_on_speed()
        self.update_force_arrow()
        
    def move_nonVerlet(self): # For Verlet integration
        
        self.total_velocity += self.total_force
        self.fix_speed()
        
        
        self.pos = self.total_velocity + self.pos
        self.molecule_shape.pos = self.pos  # Update the ball's position in the canvas
        self.bounce_off_walls()
        
        self.update_color_based_on_speed()
        self.update_force_arrow()

    def bounce_off_walls(self):
        # Bounce off the walls of the layout, accounting for the molecule's size
        if self.x <= self.parentpos[0] or self.right >= self.parentpos[0] + self.parentsize[0]:
            self.total_velocity = Vector(-self.total_velocity.x, self.total_velocity.y)
            
        if self.y <= self.parentpos[1] or self.top >= self.parentpos[1] + self.parentsize[1]:
            self.total_velocity = Vector(self.total_velocity.x, -self.total_velocity.y)
            
        self.keep_within_bounds()

    def rescale_position(self, new_pos, new_size):
        """
        Proportionally rescale the molecule's position according to the new layout dimensions.
        """
        # Calculate the proportional change in size
        proportion_x = (self.pos[0] - self.parentpos[0]) / self.parentsize[0]
        proportion_y = (self.pos[1] - self.parentpos[1]) / self.parentsize[1]
        # print(f"Previous size: {self.parentpos}, New size: {new_size}")

        # Adjust the position of the molecule relative to the new layout size
        self.pos = (new_size[0] * proportion_x + new_pos[0], new_size[1] * proportion_y + new_pos[1])
        
        self.total_velocity = Vector(   self.total_velocity.x * new_size[0] / self.parentsize[0],
                                        self.total_velocity.y * new_size[1] / self.parentsize[1])
        
        self.fix_speed()
        self.update_color_based_on_speed()
        
        # Update the molecule's position on the canvas
        self.molecule_shape.pos = self.pos
        
        self.parentpos = new_pos
        self.parentsize = new_size
        self.keep_within_bounds()

    def keep_within_bounds(self):
        """
        Ensure the molecule stays within the bounds of the layout after a resize.
        Adjust the position if it's out of bounds.
        """
        # Clamp the x position
        if self.x < self.parentpos[0]:
            self.x = self.parentpos[0]
        if self.right > self.parentpos[0] + self.parentsize[0]:
            self.right = self.parentpos[0] + self.parentsize[0]

        # Clamp the y position
        if self.y < self.parentpos[1]:
            self.y = self.parentpos[1]
        if self.top > self.parentpos[1] + self.parentsize[1]:
            self.top = self.parentpos[1] + self.parentsize[1]

        # Update the shape's position
        self.molecule_shape.pos = self.pos

    def collide_widget(self, other):
        """
        Check if the molecule collides with another widget (another molecule).
        """
        distance = Vector(self.center).distance(other.center)
        return distance <= (self.width / 2 + other.width / 2)

    def resolve_collision(self, other):
        """
        Resolve a collision between two molecules using basic 2D collision mechanics.
        """
        v1 = self.total_velocity
        v2 = other.total_velocity

        p1 = Vector(self.center)
        p2 = Vector(other.center)

        m1 = self.width / 2
        m2 = other.width / 2

        normal = (p1 - p2).normalize()
        tangent = Vector(-normal[1], normal[0])

        v1n = normal.dot(v1)
        v1t = tangent.dot(v1)

        v2n = normal.dot(v2)
        v2t = tangent.dot(v2)

        v1n_new = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
        v2n_new = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)

        v1t_new = v1t
        v2t_new = v2t

        v1n_new_vec = v1n_new * normal
        v1t_new_vec = v1t_new * tangent

        v2n_new_vec = v2n_new * normal
        v2t_new_vec = v2t_new * tangent

        self.total_velocity = v1n_new_vec + v1t_new_vec
        other.total_velocity = v2n_new_vec + v2t_new_vec
        
        self.fix_speed()
        other.fix_speed()

    def update_color_based_on_speed(self):
        """
        Update the molecule's color based on its speed, interpolating between slow and fast colors.
        """
        
        t = min(self.total_velocity.length(), self.speed_cap) / self.speed_cap  # t is between 0 and 1 based on the speed
        self.color_instruction.rgb = [(self.color_slow[0] + (self.color_fast[0] - self.color_slow[0]) * t) / 255,
                                      (self.color_slow[1] + (self.color_fast[1] - self.color_slow[1]) * t) / 255,
                                      (self.color_slow[2] + (self.color_fast[2] - self.color_slow[2]) * t) / 255]
        
    def lennard_jones_force(self, other, epsilon, sigma, scale):
        """
        Calculate the Lennard-Jones force between this molecule and another molecule.
        :param other: The other molecule object.
        :param epsilon: Depth of the potential well.
        :param sigma: Distance at which the potential is zero.
        :return: A Vector representing the force applied on this molecule due to the other molecule.
        """
        r = (Vector(self.center).distance(other.center)) / scale # Calculate distance between two molecules
        
        if r == 0:
            return Vector(0, 0)  # Avoid division by zero if the molecules are at the same position

        # Lennard-Jones force formula
        force_magnitude = 1000 * epsilon * ((2 * (sigma / r) ** 12) - ((sigma / r) ** 6)) / r ** 2
        force_direction = (Vector(self.center) - Vector(other.center)).normalize()  # Direction of the force
        
        return force_direction * force_magnitude

    def reset_total_force(self):
        self.total_force = Vector(0, 0)

    def add_force(self, force_to_add):
        self.total_force += force_to_add

    def update_force_arrow(self):
        """
        Update the arrow direction, length, and color based on the total force.
        :param total_force: The total Lennard-Jones force applied to this molecule.
        """
        
        if not self.forces_visible:
            self.arrow_line.points = []
            return
        
        # Calculate the arrow's end position based on the force magnitude and direction
        if self.total_force.length():
            force_magnitude = math.log(self.total_force.length()) / math.log(10) + 5
        else:
            force_magnitude = 0
        
        t = max(min(force_magnitude / 5, 1), 0)  # Scale t between 0 and 1 for color interpolation
        
        arrow_length = self.radius * 3 * t # Limit arrow length to 30
        arrow_endpoint = Vector(self.center) + self.total_force.normalize() * arrow_length

        # Update the arrow points
        self.arrow_line.points = [self.center_x, self.center_y, arrow_endpoint[0], arrow_endpoint[1]]

        # Color the arrow based on the magnitude of the force (blue to red scale)
        self.arrow_color.rgb = [t, 0, 1 - t]  # Transition from blue to red
