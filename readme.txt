Code Structure:

We structure the code into several classes, allowing for the best use of Kivy modules and structure.

The app structure is broken down into three main files; game_layout.py, simulation.py, and molecule.py.

molecule.py is the standard file that contains any and all methods pertaining to the behavior of individual
molecules should be placed here. Currently, it contains methods mostly involving graphical updates and ensuring
the consistency of the molecules given different factors. Most notable among these is the Lennard-Jones calculator,
which is the fundamental driving factor in the molecular interactions within this simulation.
Also present are methods for adding and calculating forces, which are then used later in game_layout.py in order to run the simulation.
Finally, the two move methods, move and move_nonVerlet, describe two different ways in which a molecule may behave
based on its current forces and velocity; move uses the Verlet algorithm to update, whereas the other simply applies
changes to position based on velocity and changes to velocity based on forces directly.

game_layout.py is the file that manages all of the interactions between the molecules defined by molecule.py as well as
the simulation as a whole, containing methods for creating bonds between molecules, updating simulation parameters (more
on this later), and the full update method, which calculates all forces necessary and applies them in the appropriate manner.
Note that it also utilizes the verlet parameter to determine whether to call move or move_nonVerlet. It is advised
to expand this method to an enum-type variable in order to allow for more movement types.

simulation.py is the last main file, and it has access to a bunch of helper files that create new GUI components, i.e.
SliderBox, TextBlurb, SpinnerBox, and more. These have their own special graphical setups that are visible within their
respective files, but the most important thing here is understanding how they work with the Kivy GUI in order to create
new, modified versions for different purposes. Also, the way in which they are set up within simulation.py is straightforward;
by seting up each member as an instance of the given class, we can create slightly altered versions of each class to place
throughout the app layout, and the ability to apply functionality to each of them is possible through callbacks. To expand
upon this concept, the most important things to understand are how Kivy's GUI layout works and how callbacks can be used efficiently.