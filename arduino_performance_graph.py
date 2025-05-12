<<<<<<< HEAD:arduino_performance_graph.py
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color
from collections import deque

# Responsible for transfering daat that is collected from the arduino to the display of the app
class ArduinoPerfomanceGraph(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.energy_history = deque(maxlen=100)  # Store the last 100 data points
        self.graph_color = (0,1,0,1)  # yeah green lol

        
    def update_graph(self, new_energy_value):
        self.energy_history.append(new_energy_value)
        self.draw_graph()
        self.update_graph_color(new_energy_value)

    def draw_graph(self):
        self.canvas_clear()
        if not self.energy_history:
            return
        
        with self.canvas():
            Color(self.graph_color)
            max_energy = max(self.energy_history)
            min_energy = min(self.energy_history)
            width,height = self.width, self.height
            points= []
            for i, energy, in enumerate(self.energy_history):
                x = i * width / len(self.energy_history)
                y = height * (energy - min_energy) / (max_energy - min_energy)
                



        


        
    

=======
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color
from collections import deque

# Responsible for transfering daat that is collected from the arduino to the display of the app
class ArduinoPerfomanceGraph(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.energy_history = deque(maxlen=100)  # Store the last 100 data points
        self.graph_color = (0,1,0,1)  # yeah green lol


    def update_graph(self, new_energy_value):
        self.energy_history.append(new_energy_value)
        self.draw_graph()
        self.update_graph_color(new_energy_value)

    def draw_graph(self):
        self.canvas_clear()
        if not self.energy_history:
            return
        
        with self.canvas():
            Color(self.graph_color)
            max_energy = max(self.energy_history)
            min_energy = min(self.energy_history)
            width,height = self.width, self.height
            points= []
            for i, energy, in enumerate(self.energy_history):
                x = i * width / len(self.energy_history)
                y = height * (energy - min_energy) / (max_energy - min_energy)
                



        


        
    

>>>>>>> 66de32636f7bcaf91b565dd16c2168a2759d80cb:performance_graph.py
