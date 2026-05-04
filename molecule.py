from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
import math

class Molecule(Widget):
    color_slow = [5, 0, 102, 255]
    color_fast = [255, 81, 220, 255]
    color = ListProperty([x / 255 for x in color_fast])
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

        self.size = (self.radius * 2, self.radius * 2)
        self.total_force = Vector(0, 0)

        self._draw_sphere()

    def _draw_sphere(self):
        # draws the molecule as a 3D sphere using stacked circles
        # note: self.pos is the center of the molecule visually
        # (this is a quirk of how this codebase works, kivy normally uses bottom-left)
        r, g, b = self.color[0], self.color[1], self.color[2]
        cx, cy = self.pos[0], self.pos[1]
        rad = self.radius

        with self.canvas:
        # soft glow around it, matches the color
            self.glow_color = Color(r, g, b, 0.18)
            gr = rad * 1.55
            self.glow_shape = Ellipse(pos=(cx - gr, cy - gr), size=(gr * 2, gr * 2))

            # dark base so it doesnt look like a flat circle
            self.base_color = Color(r * 0.15, g * 0.15, b * 0.15, 1.0)
            self.base_shape = Ellipse(pos=(cx - rad, cy - rad), size=(rad * 2, rad * 2))

            # main color of the ball - slightly smaller and shifted to fake a curved surface
            self.color_instruction = Color(r, g, b, 1.0)
            mr = rad * 0.85
            self.molecule_shape = Ellipse(
                pos=(cx - mr + rad * 0.04, cy - mr + rad * 0.06),
                size=(mr * 2, mr * 2)
            )

            # white specular dot - small highlight to give the ball a 3D look
            self.spec_color = Color(1.0, 1.0, 1.0, 0.80)
            sr = rad * 0.22
            self.spec_shape = Ellipse(
                pos=(cx + rad * 0.28, cy + rad * 0.32),
                size=(sr * 2, sr * 2)
            )

            # force arrow - cyan to orange shows how strong the force is
            self.arrow_color = Color(0, 0.8, 1, 1)
            self.arrow_line = Line(points=[], width=max(1.5, 4 * rad / 10))

    def _update_shape_positions(self):
        # just move all sphere layers to follow the molecule
        cx, cy = self.pos[0], self.pos[1]
        rad = self.radius

        gr = rad * 1.55
        self.glow_shape.pos  = (cx - gr, cy - gr)
        self.glow_shape.size = (gr * 2, gr * 2)

        self.base_shape.pos  = (cx - rad, cy - rad)
        self.base_shape.size = (rad * 2, rad * 2)

        mr = rad * 0.85
        self.molecule_shape.pos  = (cx - mr + rad * 0.04, cy - mr + rad * 0.06)
        self.molecule_shape.size = (mr * 2, mr * 2)

        sr = rad * 0.22
        self.spec_shape.pos  = (cx + rad * 0.28, cy + rad * 0.32)
        self.spec_shape.size = (sr * 2, sr * 2)

    def fix_speed(self):
        if self.total_velocity.length() > self.speed_cap:
            self.total_velocity *= self.speed_cap / self.total_velocity.length()

    def fix_force(self):
        fx, fy = self.total_force
        if not (abs(fx) < 1e15 and abs(fy) < 1e15):
            self.total_force = self.total_force * 0  # zero out inf/NaN
            return
        if self.total_force.length() > self.force_cap:
            self.total_force *= self.force_cap / self.total_force.length()

    def fix_radius(self, new_radius):
        self.pos = (self.pos[0] - new_radius + self.radius, self.pos[1] - new_radius + self.radius)
        self.radius = new_radius
        self.size = (self.radius * 2, self.radius * 2)
        # clear and redraw everything when the size actually changes
        self.canvas.clear()
        self._draw_sphere()

    def move(self, delta):   # Verlet integration
        self.fix_force()
        self.pos = self.total_velocity * delta + 0.5 * self.total_force * (delta ** 2) + self.pos
        self._update_shape_positions()
        self.bounce_off_walls()
        self.total_velocity += self.total_force * delta
        self.fix_speed()
        self.update_color_based_on_speed()
        self.update_force_arrow()

    def move_nonVerlet(self):
        self.total_velocity += self.total_force
        self.fix_speed()
        self.pos = self.total_velocity + self.pos
        self._update_shape_positions()
        self.bounce_off_walls()
        self.update_color_based_on_speed()
        self.update_force_arrow()

    def bounce_off_walls(self):
        # bounce when hitting wall
        if self.x <= self.parentpos[0] or self.right >= self.parentpos[0] + self.parentsize[0]:
            self.total_velocity = Vector(-self.total_velocity.x, self.total_velocity.y)
        if self.y <= self.parentpos[1] or self.top >= self.parentpos[1] + self.parentsize[1]:
            self.total_velocity = Vector(self.total_velocity.x, -self.total_velocity.y)
        self.keep_within_bounds()

    def rescale_position(self, new_pos, new_size):
        # move molecule to follow the window
        proportion_x = (self.pos[0] - self.parentpos[0]) / self.parentsize[0]
        proportion_y = (self.pos[1] - self.parentpos[1]) / self.parentsize[1]
        self.pos = (new_size[0] * proportion_x + new_pos[0], new_size[1] * proportion_y + new_pos[1])
        self.total_velocity = Vector(
            self.total_velocity.x * new_size[0] / self.parentsize[0],
            self.total_velocity.y * new_size[1] / self.parentsize[1]
        )
        self.fix_speed()
        self.update_color_based_on_speed()
        self._update_shape_positions()
        self.parentpos = new_pos
        self.parentsize = new_size
        self.keep_within_bounds()

    def keep_within_bounds(self):
        # keep molecule inside the box
        if self.x < self.parentpos[0]:
            self.x = self.parentpos[0]
        if self.right > self.parentpos[0] + self.parentsize[0]:
            self.right = self.parentpos[0] + self.parentsize[0]
        if self.y < self.parentpos[1]:
            self.y = self.parentpos[1]
        if self.top > self.parentpos[1] + self.parentsize[1]:
            self.top = self.parentpos[1] + self.parentsize[1]
        self._update_shape_positions()

    def collide_widget(self, other):
        distance = Vector(self.center).distance(other.center)
        return distance <= (self.width / 2 + other.width / 2)

    def resolve_collision(self, other):
        # 2D elastic collision stuff
        v1 = self.total_velocity
        v2 = other.total_velocity
        p1 = Vector(self.center)
        p2 = Vector(other.center)
        m1 = self.width / 2
        m2 = other.width / 2
        normal  = (p1 - p2).normalize()
        tangent = Vector(-normal[1], normal[0])
        v1n = normal.dot(v1);  v1t = tangent.dot(v1)
        v2n = normal.dot(v2);  v2t = tangent.dot(v2)
        v1n_new = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
        v2n_new = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)
        self.total_velocity  = v1n_new * normal + v1t * tangent
        other.total_velocity = v2n_new * normal + v2t * tangent
        self.fix_speed()
        other.fix_speed()

    def update_color_based_on_speed(self):
        # slow ones are dark blue, fast ones turn bright pink/magenta
        t = min(self.total_velocity.length(), self.speed_cap) / self.speed_cap
        r = (self.color_slow[0] + (self.color_fast[0] - self.color_slow[0]) * t) / 255
        g = (self.color_slow[1] + (self.color_fast[1] - self.color_slow[1]) * t) / 255
        b = (self.color_slow[2] + (self.color_fast[2] - self.color_slow[2]) * t) / 255
        self.color_instruction.rgb = [r, g, b]
        self.glow_color.rgba       = [r, g, b, 0.18]
        self.base_color.rgb        = [r * 0.15, g * 0.15, b * 0.15]

    def lennard_jones_force(self, other, epsilon, sigma, scale):
        # LJ potential - atoms pull on each other from far away but push when theyre close
        r = Vector(self.center).distance(other.center) / scale
        if r == 0:
            return Vector(0, 0)
        force_magnitude = 1000 * epsilon * ((2 * (sigma / r) ** 12) - ((sigma / r) ** 6)) / r ** 2
        force_direction = (Vector(self.center) - Vector(other.center)).normalize()
        return force_direction * force_magnitude

    def reset_total_force(self):
        self.total_force = Vector(0, 0)

    def add_force(self, force_to_add):
        self.total_force += force_to_add

    def update_force_arrow(self):
        if not self.forces_visible:
            self.arrow_line.points = []
            return
        if self.total_force.length():
            force_magnitude = math.log(self.total_force.length()) / math.log(10) + 5
        else:
            force_magnitude = 0
        t = max(min(force_magnitude / 5, 1), 0)
        arrow_length = self.radius * 3 * t
        # skip tiny stubs - below this threshold it just looks like a blob dot
        if arrow_length < self.radius * 0.8:
            self.arrow_line.points = []
            return
        arrow_endpoint = Vector(self.center) + self.total_force.normalize() * arrow_length
        self.arrow_line.points = [self.center_x, self.center_y, arrow_endpoint[0], arrow_endpoint[1]]
        # cyan when force is small, turns orange when its strong
        self.arrow_color.rgb = [t, 0.8 * (1 - t) + 0.3 * t, 1.0 * (1 - t)]
