
import json
import socket
import sys
import time

HOST, PORT = "127.0.0.1", 5050


def send(sock_file, sock, message):
    sock.sendall((json.dumps(message) + "\n").encode())
    return json.loads(sock_file.readline())


def main():
    if len(sys.argv) == 4:
        amb_id, source, hospital = sys.argv[1:4]
    else:
        amb_id = input("Ambulance ID (AMB01/AMB02/AMB03): ")
        source = input("Current junction (J1-J8): ")
        hospital = input("Hospital (H1/H2/H3): ")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        f = s.makefile("r")
        reply = send(f, s, {"type": "REQUEST", "ambulance_id": amb_id,
                            "source": source, "hospital": hospital})
        if reply["status"] != "OK":
            print("Request failed:", reply["reason"])
            return
        print(f"Route to {reply['hospital']}: {' -> '.join(reply['route'])} (ETA {reply['eta_min']} min)")
        tid = reply["transit_id"]
        for junction in reply["route"]:
            time.sleep(1)  # simulated travel time
            r = send(f, s, {"type": "POSITION", "transit_id": tid, "junction": junction})
            print(f"At {junction}. Green junctions: {r['green_junctions']}")
        print(send(f, s, {"type": "ARRIVED", "transit_id": tid})["message"])


if __name__ == "__main__":
    main()
