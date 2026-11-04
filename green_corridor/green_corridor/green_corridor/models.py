LOOKAHEAD = 2  # how many junctions ahead of the ambulance are kept green


class Vehicle:
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id

    def __str__(self):
        return f"Vehicle {self.vehicle_id}"


class Ambulance(Vehicle):  # inheritance
    def __init__(self, ambulance_id, driver, status="IDLE"):
        super().__init__(ambulance_id)
        self.driver = driver
        self.status = status

    def __str__(self):
        return f"Ambulance {self.vehicle_id} (driver: {self.driver}, {self.status})"


class Junction:
    def __init__(self, jid, name):
        self.jid = jid
        self.name = name
        self.signal = "RED"

    def set_green(self):
        self.signal = "GREEN"

    def reset(self):
        self.signal = "RED"

    def __str__(self):
        return f"{self.jid}-{self.name}[{self.signal}]"


class Hospital:
    def __init__(self, hid, name, junction):
        self.hid = hid
        self.name = name
        self.junction = junction


class GreenCorridor:
    """Tracks which junctions are held green for one ambulance trip."""

    def __init__(self, transit_id, route):
        self.transit_id = transit_id
        self.route = route  # list of junction ids
        self.cleared = set()  # junctions currently held green

    def update(self, junction_id):
        """Ambulance reached junction_id.
        Returns a tuple (to_release, to_clear) of lists."""
        index = self.route.index(junction_id)
        to_release = [j for j in self.route[:index] if j in self.cleared]
        ahead = self.route[index : index + LOOKAHEAD + 1]
        to_clear = [j for j in ahead if j not in self.cleared]
        self.cleared.difference_update(to_release)
        self.cleared.update(to_clear)
        return to_release, to_clear

    def release_all(self):
        remaining = list(self.cleared)
        self.cleared.clear()
        return remaining
