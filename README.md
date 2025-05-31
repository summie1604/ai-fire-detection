#  AI-Based Fire Detection System (IoT + AI + Firebase)

An intelligent, real-time fire detection system using **Arduino Mega**, **ESP32**, **Firebase Realtime Database**, and a trained **neural network**. This system continuously monitors multiple sensors, predicts fire using an AI model, and triggers cloud alerts with optimized shortest-path logic using **Dijkstra’s algorithm**.


##  Key Features
-  Multi-sensor support: MQ2, MQ7, IR, Flame sensor
-  Real-time AI prediction with 94.5% accuracy
- ☁ Firebase Realtime Database integration
-  ESP32-based wireless data transmission
-  Dijkstra’s algorithm for emergency route optimization
- Sensor data logging and inference in Python



## 🛠️Technologies Used

| Component         | Tools / Hardware                          |
|------------------|--------------------------------------------|
| Microcontrollers | Arduino Mega, ESP32                        |
| Sensors          | MQ2 (smoke), MQ7 (CO), IR, Flame sensor    |
| AI/ML Frameworks | TensorFlow, Scikit-learn                   |
| Cloud Platform   | Firebase Realtime Database                 |
| Programming      | Python, C++ (Arduino IDE)                  |



## 📁 Project Structure

├── arduino/          
├── esp32/            
├── python/           
├── model/            
├── data/             
├── README.md         
└── LICENSE          



##  AI Model Performance

| Metric     | Value   |
|------------|---------|
| Accuracy   | 94.5%   |
| Precision  | 92.3%   |
| Recall     | 95.8%   |
| F1-Score   | 94.0%   |
