from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.clock import Clock
from performance_monitor import PerformanceMonitor

def integer_formatter(value):
    # Round and convert to int if want no decimals
    return str(int(round(value)))

class CPUUsageGraph(BoxLayout): 
    def __init__(self, monitor, **kwargs):
        super().__init__(**kwargs)
        self.monitor = monitor

        self.graph = Graph(
            xlabel='Time (s)',
            ylabel='CPU Usage (%)',
            x_ticks_minor=1,
            x_ticks_major=5,
            y_ticks_major=10,
            y_grid_label=True,
            x_grid_label=True,
            xmin=0,
            xmax=60,
            ymin=0,
            ymax=100,
            border_color=[1, 1, 1, 1],
            tick_color=[0.7, 0.7, 0.7, 1],
            label_options={'color': [1, 1, 1, 1], 'bold': True}
        )

        # the Y-axis to use integer labels
        self.graph.y_label_func = integer_formatter

        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.graph.add_plot(self.plot)
        self.add_widget(self.graph)

        self.cpu_data = []

        Clock.schedule_interval(self.update_graph, 1)  # to 1/60?? interesting result

    def update_graph(self, dt):
        cpu_usage = self.monitor.get_cpu_usage()
        self.cpu_data.append(cpu_usage)
        length = len(self.cpu_data)

        # Shift X-axis
        if length > 60:
            self.graph.xmin = length - 60
            self.graph.xmax = length
        else:
            self.graph.xmin = 0
            self.graph.xmax = 60

        # Keeping list from growing too large
        if len(self.cpu_data) > 120:
            self.cpu_data.pop(0)

        # Updating the plot
        self.plot.points = [(i, val) for i, val in enumerate(self.cpu_data)]

        #the Y-axis with buffer
        ymin = max(0, min(self.cpu_data) - 5)
        ymax = max(self.cpu_data) + 5
        self.graph.ymin = ymin
        self.graph.ymax = ymax
