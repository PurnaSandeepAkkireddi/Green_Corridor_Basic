import json
import socket
import threading

import database
from file_utils import load_json, log_event, save_json
from models import GreenCorridor, Hospital, Junction
from routing import build_graph, shortest_path

HOST, PORT = "127.0.0.1", 5050


class ControlRoom:
    def __init__(self, map_file="data/map.json"):
        data = load_json(map_file)
        self.junctions = {
            jid: Junction(jid, name) for jid, name in data["junctions"].items()
        }
        self.hospitals = {
            hid: Hospital(hid, h["name"], h["junction"])
            for hid, h in data["hospitals"].items()
        }
        self.graph = build_graph(data["roads"])
        self.corridors = {}  # transit_id -> GreenCorridor
        self.transit_info = {}  # transit_id -> dict for report
        self.lock = threading.Lock()

    # ---- helpers ----
    def _apply(self, transit_id, to_release, to_clear):
        for j in to_release:
            self.junctions[j].reset()
            database.log_signal(transit_id, j, "RESET")
            log_event(f"Transit {transit_id}: {self.junctions[j]} released")
        for j in to_clear:
            self.junctions[j].set_green()
            database.log_signal(transit_id, j, "GREEN")
            log_event(f"Transit {transit_id}: {self.junctions[j]} cleared")

    # ---- message handlers ----
    def handle(self, msg):
        kind = msg.get("type")
        with self.lock:
            if kind == "REQUEST":
                return self.on_request(msg)
            if kind == "POSITION":
                return self.on_position(msg)
            if kind == "ARRIVED":
                return self.on_arrived(msg)
        return {"status": "ERROR", "reason": "Unknown message type"}

    def on_request(self, msg):
        amb = database.get_ambulance(msg.get("ambulance_id"))
        if amb is None:
            return {"status": "ERROR", "reason": "Unknown ambulance"}
        source, hid = msg.get("source"), msg.get("hospital")
        if source not in self.junctions or hid not in self.hospitals:
            return {"status": "ERROR", "reason": "Unknown source or hospital"}
        hospital = self.hospitals[hid]
        route, eta = shortest_path(self.graph, source, hospital.junction)
        if route is None:
            return {"status": "ERROR", "reason": "No route"}
        transit_id = database.create_transit(amb[0], source, hid, route)
        database.set_ambulance_status(amb[0], "ON_DUTY")
        corridor = GreenCorridor(transit_id, route)
        self.corridors[transit_id] = corridor
        self.transit_info[transit_id] = {
            "ambulance": amb[0],
            "driver": amb[1],
            "hospital": hospital.name,
            "route": route,
            "eta_min": eta,
        }
        log_event(
            f"Transit {transit_id}: {amb[0]} -> {hospital.name} via {route} (ETA {eta} min)"
        )
        self._apply(transit_id, *corridor.update(route[0]))
        return {
            "status": "OK",
            "transit_id": transit_id,
            "route": route,
            "eta_min": eta,
            "hospital": hospital.name,
        }

    def on_position(self, msg):
        corridor = self.corridors.get(msg.get("transit_id"))
        if corridor is None or msg.get("junction") not in corridor.route:
            return {"status": "ERROR", "reason": "Bad transit or junction"}
        self._apply(corridor.transit_id, *corridor.update(msg["junction"]))
        green = sorted(corridor.cleared)
        return {"status": "OK", "green_junctions": green}

    def on_arrived(self, msg):
        tid = msg.get("transit_id")
        corridor = self.corridors.pop(tid, None)
        if corridor is None:
            return {"status": "ERROR", "reason": "Unknown transit"}
        self._apply(tid, corridor.release_all(), [])
        database.close_transit(tid)
        info = self.transit_info.pop(tid)
        database.set_ambulance_status(info["ambulance"], "IDLE")
        info["signal_log"] = database.get_signal_log(tid)
        save_json(f"reports/transit_{tid}.json", info)
        log_event(f"Transit {tid}: arrived. Corridor closed. Report saved.")
        return {"status": "OK", "message": "Corridor closed"}


def client_thread(conn, addr, room):
    log_event(f"Connected: {addr}")
    with conn:
        reader = conn.makefile("r")
        for line in reader:
            try:
                reply = room.handle(json.loads(line))
            except json.JSONDecodeError:
                reply = {"status": "ERROR", "reason": "Invalid JSON"}
            conn.sendall((json.dumps(reply) + "\n").encode())
    log_event(f"Disconnected: {addr}")


def main():
    database.init_db()
    room = ControlRoom()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    log_event(f"Control room listening on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=client_thread, args=(conn, addr, room), daemon=True
        ).start()


if __name__ == "__main__":
    main()
