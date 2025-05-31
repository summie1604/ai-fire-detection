# AI-Based Fire Detection IoT System

This project integrates Arduino, ESP32, Python AI inference, and Firebase to create a real-time fire detection and response system.

## Components
- Arduino Mega reads MQ2, MQ7, IR, and Flame sensors
- Python script runs trained neural network model for FIRE/SAFE classification
- ESP32 uploads verdicts to Firebase
- Shortest path routing logic using Dijkstra is embedded in `inference.py`

## Folders
- `arduino/` – Arduino sensor code
- `esp32/` – ESP32 Firebase uploader code
- `python/` – Python scripts for inference and data logging
- `model/` – Trained models (`.h5` and `.pkl`)
- `data/` – Raw and processed sensor datasets
