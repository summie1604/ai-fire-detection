import serial
import time
import numpy as np
import tensorflow as tf
import requests
import heapq
import matplotlib.pyplot as plt
import networkx as nx

# ==== Firebase ====
FIREBASE_URL = "https://use-this-one-70e96-default-rtdb.asia-southeast1.firebasedatabase.app/sensor_data.json"
FIREBASE_AUTH = "AIzaSyCErSd5aa9gRKzFKkyoPVxu70021FHqQqU"

# ==== Serial ====
SERIAL_PORT = "/dev/cu.usbmodem1101"
BAUD_RATE = 9600
FLAME_THRESHOLD = 700

# ==== Load Model ====
model = tf.keras.models.load_model('binary_classifier_nn.h5')

# ==== Graph ====
graph = {
    'A': {'B': 3, 'C': 1},
    'B': {'A': 3, 'D': 2, 'E': 4},
    'C': {'A': 1, 'F': 6},
    'D': {'B': 2},
    'E': {'B': 4, 'F': 1},
    'F': {'C': 6, 'E': 1}
}
fire_stations = ['D', 'F']

def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph}
    prev = {node: None for node in graph}
    dist[start] = 0
    q = [(0, start)]

    while q:
        d, u = heapq.heappop(q)
        for v, w in graph[u].items():
            if dist[v] > d + w:
                dist[v] = d + w
                prev[v] = u
                heapq.heappush(q, (dist[v], v))
    return dist, prev

def get_path(prev, node):
    path = []
    while node:
        path.insert(0, node)
        node = prev[node]
    return path

def draw_graph(graph, path):
    G = nx.Graph()
    for node, neighbors in graph.items():
        for neighbor, weight in neighbors.items():
            G.add_edge(node, neighbor, weight=weight)

    pos = nx.spring_layout(G, seed=42)
    edge_labels = nx.get_edge_attributes(G, 'weight')

    edge_colors = ['red' if (u in path and v in path and abs(path.index(u) - path.index(v)) == 1) else 'black' for u, v in G.edges()]
    node_colors = ['orange' if n in fire_stations else 'skyblue' for n in G.nodes()]

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color=edge_colors, node_size=800, font_size=14)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Fire Station Shortest Path")
    plt.show()

def predict(sensor_data):
    try:
        input_data = np.array(sensor_data).reshape(1, -1)
        model_output = model.predict(input_data, verbose=0)[0][0]
        return "FIRE" if model_output >= 0.5 and sensor_data[2] < FLAME_THRESHOLD else "SAFE"
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return "SAFE"

def upload_to_firebase(verdict, mq2, mq7, flame):
    data = {
        "verdict": verdict,
        "mq2": mq2,
        "mq7": mq7,
        "flame": flame,
        "timestamp": int(time.time() * 1000)
    }
    try:
        res = requests.post(f"{FIREBASE_URL}?auth={FIREBASE_AUTH}", json=data)
        print("✅ Firebase Upload" if res.status_code == 200 else f"❌ Firebase Error {res.status_code}")
    except Exception as e:
        print(f"❌ Upload Failed: {e}")

# ==== Serial Connection ====
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

fire_triggered = False
print("🔥 Monitoring...\n")

try:
    while not fire_triggered:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"📥 Raw Serial: {line}")
        try:
            values = [int(val.strip()) for val in line.split(",") if val.strip().isdigit()]
            if len(values) != 3:
                raise ValueError("Invalid sensor data")
            sensor_data = values
            verdict = predict(sensor_data)
            print(f"Sensor Data: {sensor_data} => {verdict}")
            ser.write((verdict + "\n").encode())
            upload_to_firebase(verdict, *sensor_data)

            if verdict == "FIRE":
                fire_triggered = True
                print("\n🚨 FIRE DETECTED!")

                while True:
                    source = input("🏠 Enter your house node (A-C): ").strip().upper()
                    if source in graph:
                        break
                    print("❌ Invalid node. Try again.")

                dist, prev = dijkstra(graph, source)
                nearest = min(fire_stations, key=lambda x: dist[x])
                path = get_path(prev, nearest)

                print(f"\n📍 Closest Fire Station: {nearest}")
                print(f"🛣️  Path: {' -> '.join(path)}")
                print(f"📏 Distance: {dist[nearest]}")
                draw_graph(graph, path)

        except ValueError as e:
            print(f"⚠️ Skipped: Bad input => {e}")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("🛑 Stopped by user.")

finally:
    ser.close()
