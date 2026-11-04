"""Shortest path (Dijkstra)"""

INF = float("inf")


def build_graph(roads):
    graph = {}
    for a, b, w in roads:  # each road is [a, b, weight]
        graph.setdefault(a, []).append((b, w))  # neighbours stored as tuples
        graph.setdefault(b, []).append((a, w))
    return graph


def shortest_path(graph, start, goal):
    """Returns (path_list, total_time) or (None, INF)."""
    dist = {node: INF for node in graph}
    prev = {}
    unvisited = set(graph)
    dist[start] = 0
    while unvisited:
        current = min(unvisited, key=lambda n: dist[n])
        if dist[current] == INF:
            break
        unvisited.remove(current)
        if current == goal:
            break
        for neighbour, weight in graph[current]:
            if dist[current] + weight < dist[neighbour]:
                dist[neighbour] = dist[current] + weight
                prev[neighbour] = current
    if dist[goal] == INF:
        return None, INF
    path = [goal]
    while path[-1] != start:
        path.append(prev[path[-1]])
    path.reverse()
    return path, dist[goal]
