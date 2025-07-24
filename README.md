# 🤖 AI Stork Watcher - Stork Detection Project

This project uses a Machine Learning model (YOLOv8) to detect storks in real-time from a YouTube video stream, aiming to analyze their behavior and presence in the nest.

---

## 📸 Detection Example
*(Tip: Upload one of your best detection images to the project folder and link it here. A picture is worth a thousand words!)*

![Detection Example](runs/detect/realtime/detection_20250723_173000.jpg)

---

## ✨ Key Features
- **Real-time Detection:** Analyzes a live video stream.
- **Custom Model:** Trained on a custom dataset to identify storks with high precision.
- **Automation:** Capable of running in a loop to monitor the nest at defined intervals.

---

## 🛠️ Tech Stack
- **Python**
- **YOLOv8 (Ultralytics)**
- **OpenCV**
- **PyTorch**

---

## 🚀 Getting Started

Follow these steps to get the project up and running on your own machine.

### 1. Prerequisites
- Python 3.9 or higher
- Git

### 2. Installation
```bash
# 1. Clone the repository
git clone [https://github.com/your-username/your-repository.git](https://github.com/your-username/your-repository.git)
cd your-repository

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install the dependencies
pip install -r requirements.txt