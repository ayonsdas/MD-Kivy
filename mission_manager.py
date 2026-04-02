# mission manager - handles all the game mission logic
# pure python, no kivy stuff in here so its easy to test separately
# simulation.py calls tick() every frame to check if the player won or lost

MISSIONS = [
    {
        'id': 'heat_gas',
        'name': 'Heat the Gas',
        'description': 'Raise temperature to the\ntarget range within the time limit.\nFewer molecules = more budget saved.',
        'goal_type': 'temp_range',
        'target_min': 120,
        'target_max': 250,
        'time_limit': 90,
        'molecule_limit': 25,   # cant use more than this many molecules
        'cpu_budget': 600,
        'preset': 'Gas',
        'difficulty': 'Easy',
        'difficulty_color': (0.3, 0.9, 0.3, 1),
        'hint': 'Increase epsilon or shake the Arduino!',
    },
    {
        'id': 'deep_freeze',
        'name': 'Deep Freeze',
        'description': 'Slow the molecules until temperature\ndrops below the target.\nControl gravity and forces carefully.',
        'goal_type': 'temp_max',
        'target_max': 28,
        'time_limit': 75,
        'molecule_limit': 30,
        'cpu_budget': 450,
        'preset': 'Liquid',
        'difficulty': 'Medium',
        'difficulty_color': (1.0, 0.8, 0.2, 1),
        'hint': 'Remove molecules to reduce kinetic energy.',
    },
    {
        'id': 'budget_run',
        'name': 'Budget Run',
        'description': 'Run the simulation for the full time.\nEvery extra molecule drains your budget faster.',
        'goal_type': 'survive',
        'time_limit': 90,
        'cpu_budget': 280,      # tight budget - more molecules drains it faster!
        'difficulty': 'Hard',
        'difficulty_color': (1.0, 0.5, 0.1, 1),
        'hint': 'Use fewer molecules and lower epsilon.',
    },
    {
        'id': 'precision',
        'name': 'Precision Control',
        'description': 'Hold temperature in a narrow range\nfor 5 continuous seconds.\nStability is everything.',
        'goal_type': 'temp_hold',
        'target_min': 75,
        'target_max': 105,
        'hold_time': 5.0,       # must stay in range for 5 full seconds
        'time_limit': 120,
        'cpu_budget': 900,
        'preset': 'Gas',
        'difficulty': 'Expert',
        'difficulty_color': (1.0, 0.2, 0.4, 1),
        'hint': 'Fine-tune sigma and epsilon slowly.',
    },
]


class MissionManager:
    def __init__(self):
        self.missions = MISSIONS
        self.state = 'idle'         # idle, active, success, or fail
        self.current = None
        self.elapsed = 0.0
        self.cpu_used = 0.0         # how much compute budget has been used so far
        self.hold_elapsed = 0.0     # how long the temp has been in the target range (for precision mission)
        self.fail_reason = ''
        self.score = 0
        self.last_temperature = 0.0

        # these get set by the UI so it knows when to show the result screen
        self.on_success = None
        self.on_fail = None
        self.on_tick = None

    def start(self, mission_index):
        self.current = self.missions[mission_index]
        self.state = 'active'
        self.elapsed = 0.0
        self.cpu_used = 0.0
        self.hold_elapsed = 0.0
        self.fail_reason = ''
        self.score = 0

    def stop(self):
        self.state = 'idle'
        self.current = None

    def tick(self, dt, temperature, cpu_usage, molecule_count):
        # called every frame - checks if the player won, lost, or is still going
        if self.state != 'active' or self.current is None:
            return

        self.last_temperature = temperature
        m = self.current
        self.elapsed += dt

        # more molecules = budget drains faster (thats the whole point of the budget mechanic!)
        weight = max(molecule_count, 1) / 5.0
        self.cpu_used += (cpu_usage / 100.0) * dt * weight

        # check if player broke any rules
        if m.get('molecule_limit') and molecule_count > m['molecule_limit']:
            self._fail(f"Too many molecules! Max: {m['molecule_limit']}")
            return

        if self.cpu_used >= m['cpu_budget']:
            self._fail('Compute budget exhausted!')
            return

        if self.elapsed >= m['time_limit']:
            if m['goal_type'] == 'survive':
                self._success()
            else:
                self._fail('Time is up!')
            return

        # check if the goal is done
        goal = m['goal_type']
        if goal == 'temp_range':
            if m['target_min'] <= temperature <= m['target_max']:
                self._success()

        elif goal == 'temp_max':
            if temperature <= m['target_max']:
                self._success()

        elif goal == 'temp_hold':
            if m['target_min'] <= temperature <= m['target_max']:
                self.hold_elapsed += dt
                if self.hold_elapsed >= m.get('hold_time', 5.0):
                    self._success()
            else:
                # slowly lose hold progress if you drift out of range
                self.hold_elapsed = max(0.0, self.hold_elapsed - dt * 2)

        if self.on_tick:
            self.on_tick(self.get_progress())

    def _success(self):
        self.state = 'success'
        m = self.current
        # bonus points for finishing fast and using less compute budget
        time_bonus   = max(0, m['time_limit'] - self.elapsed)
        budget_bonus = max(0, m['cpu_budget'] - self.cpu_used)
        self.score   = int(1000 + time_bonus * 10 + budget_bonus * 2)
        if self.on_success:
            self.on_success(self.score)

    def _fail(self, reason):
        self.state = 'fail'
        self.fail_reason = reason
        self.score = 0
        if self.on_fail:
            self.on_fail(reason)

    def get_progress(self):
        # returns everything the HUD needs to display - no kivy objects, just plain data
        if self.current is None:
            return {}
        m = self.current
        budget_frac = max(0.0, 1.0 - self.cpu_used / m['cpu_budget'])
        time_left   = max(0.0, m['time_limit'] - self.elapsed)
        time_frac   = time_left / m['time_limit']
        hold_frac   = (self.hold_elapsed / m.get('hold_time', 5.0)) if m['goal_type'] == 'temp_hold' else 0.0
        return {
            'state':            self.state,
            'name':             m['name'],
            'description':      m['description'],
            'goal_type':        m['goal_type'],
            'target_min':       m.get('target_min', 0),
            'target_max':       m.get('target_max', 999),
            'temperature':      self.last_temperature,
            'time_left':        time_left,
            'time_frac':        time_frac,
            'budget_frac':      budget_frac,
            'hold_frac':        hold_frac,
            'hold_time':        m.get('hold_time', 0),
            'score':            self.score,
            'fail_reason':      self.fail_reason,
            'difficulty':       m.get('difficulty', ''),
            'difficulty_color': m.get('difficulty_color', (1, 1, 1, 1)),
            'hint':             m.get('hint', ''),
        }
