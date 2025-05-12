# Visual Molecular Dynamics Demonstration (VMD Demo)

Developed by the Texas Advanced Computing Center (TACC) for display at their Visitor Center, this project serves as an interactive molecular dynamics simulation demonstration. Designed to make complex scientific principles accessible and engaging, the VMD Demo provides a real-time environment where users can visualize and manipulate virtual molecules to observe how they behave under different physical forces. This demonstration merges science and interactivity, offering an educational experience for visitors of all ages and backgrounds, showcasing TACC’s commitment to advancing scientific understanding through high-performance computing and visualization.

## Project Purpose

The VMD Demo offers an intuitive interface to explore molecular behaviors governed by fundamental physics. Visitors can adjust a variety of parameters—gravity, intermolecular forces, simulation speed, and more—to experiment with and understand molecular dynamics principles such as attraction, repulsion, bonding, and collisions. This visually engaging tool empowers users to witness how individual and collective molecular interactions respond to environmental changes, emphasizing TACC's role in scientific exploration and outreach.

## Features & Functionality

### Interactive Molecular Simulation

#### Dynamic Molecular Movement: Molecules move in response to user-defined physical forces, offering a realistic visualization of molecular behaviors.
#### Intermolecular Force Interactions: Toggleable intermolecular forces allow users to observe how molecules attract, repel, or remain neutral based on the Lennard-Jones potential, a widely-used model in molecular simulations.

### Physics-Based Parameter Controls

#### Gravity Adjustment: A gravity slider allows users to control the gravitational force on molecules, illustrating how increased gravity causes molecules to cluster and move in specific patterns.
#### Intermolecular Forces (Lennard-Jones Potential): Sliders to adjust epsilon (interaction depth) and sigma (interaction range) let users see how force intensity and proximity affect molecular behaviors.
#### Bond Spring Force: Bonds between molecules are modeled with spring-like forces, governed by adjustable spring constants and rest lengths, enabling users to see attraction and repulsion between bonded molecules.

### Simulation Speed Control

#### Speed Adjustment: A speed slider lets users accelerate or slow down the simulation, providing control over how rapidly molecules interact and move. The simulation’s time steps adjust in real time to reflect changes without interrupting the visual flow.
#### Start/Stop Simulation: A toggle button allows users to start or stop the simulation, letting them pause and resume molecular activity as they explore different parameters.

### Bonding and Collision Effects

#### User-Interactive Bond Formation: Users can select and bond molecules by clicking or tapping, with bonds visually represented as dynamic lines that update with movement, demonstrating how bonded molecules behave as connected entities.
#### Collision Response: Colliding molecules react with realistic behavior, adjusting velocities upon impact. This feature replicates chaotic, real-world molecular interactions, offering a dynamic environment for exploration.

### Visual Data and Feedback

#### Real-Time System Statistics: The simulation provides live feedback on key metrics such as total energy, temperature (related to kinetic energy), and pressure, updating as the simulation progresses.
#### Speed-Based Color Coding: Molecules change color based on speed, visually representing their velocity. This helps users identify high-speed molecules and understand speed relationships with parameters like gravity and force.

### Boundary and Size Adjustments

#### Resizable Simulation Area: The molecular environment automatically adapts to window size changes, ensuring a consistent experience across screens.
#### Safe Boundaries for User Interaction: Molecules created by user input stay within the visual field, ensuring interactions remain within the simulation boundaries for a clear and accessible demonstration.

## Educational Value
As an educational and exploratory tool, the VMD Demo provides visitors with a first-hand experience of molecular dynamics, making abstract scientific concepts tangible. Through its interactive features, users learn about principles such as forces, bonding, energy transfer, and temperature, with immediate visual feedback for each parameter adjustment. This project embodies TACC’s dedication to enhancing public understanding of science through advanced visualization, showcasing the power and accessibility of high-performance computing for scientific discovery.


## Running this project

#### Should be incredibly simple - Just make sure you have kivy installed
        pip install kivy (if necessary)
        pip install kivymd (if necessary)
        pip install kivy-garden.graph (if necessary)
#### Might be helpful to create a virtual environment for this 
        python3 -m venv {VENV_NAME}
        {VENV_NAME}/Scripts/activate (Windows) / source {VENV_NAME}/bin/activate (Mac / Linux)

### Then just run python3 main.py


### Specifically on the Vislab LASSO system

#### Open up a terminal - should be in C:\Users\visloc, if not navigate to that location
        cd C:\Users\visloc
#### Move to the molecular-dynamics-kivy folder
        cd molecular-dynamics-kivy
#### Activate the virtual environment (kivyenv)
        kivyenv\Scripts\activate
#### Run the project
        python main.py