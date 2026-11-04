# Hospital Transit & Green Corridor (Python)

An ambulance asks the control room for a route to a hospital. The server finds the
shortest path and turns the traffic signals GREEN a few junctions ahead of the
ambulance, then releases them as it passes.

## Run
Terminal 1:  python server.py
Terminal 2:  python ambulance_client.py
History:     python database.py

## Syllabus mapping

| Database | database.py (sqlite3: ambulances, transits, signal_log) |
| Socket programming | server.py (TCP + threads), ambulance_client.py |
| Lists, sets, tuples, OOP | models.py (inheritance, set of cleared junctions), routing.py |
| JSON files | data/map.json (input), reports/transit_N.json (output) |
| File handling | file_utils.py (append logs/corridor.log, read/write JSON) |
