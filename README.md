🚦 Smart Traffic Management System using Raspberry Pi & YOLO
This project is a real-time vehicle detection and counting system for smart traffic management, designed to run efficiently on edge devices like the Raspberry Pi using YOLOv3-tiny and YOLOv4-tiny models.

📁 Project Structure
bash
Copy
Edit
📦 Smart-Traffic-Management/
├── the orginal.py             # Full vehicle detection script
├── tiny vehicle.py           # Lightweight script for Raspberry Pi
├── yolov3-tiny.cfg           # Config file for YOLOv3-tiny
├── yolov4-tiny.weights       # Pre-trained YOLOv4-tiny weights
🎯 Features
Real-time vehicle detection on low-power edge devices

Utilizes YOLOv3/YOLOv4-tiny for fast object detection

Counts vehicles passing through a frame

Modular code to switch between full and lightweight versions

💡 Use Case
This system can be deployed at traffic junctions or toll booths to:

Monitor traffic density

Collect traffic statistics

Enable dynamic signal control in smart cities

🛠️ Requirements
Raspberry Pi 4 (or compatible)

Camera Module (USB or PiCam)

Python 3.7+

OpenCV (opencv-python)

NumPy

imutils

Install dependencies:

bash
Copy
Edit
pip install opencv-python numpy imutils
⚙️ Setup Instructions
Clone the Repository:

bash
Copy
Edit
git clone https://github.com/yourusername/smart-traffic-management.git
cd smart-traffic-management
Download Weights & Config Files
Ensure yolov3-tiny.cfg and yolov4-tiny.weights are present in the project folder.

Run the Script:

To run the full detection script (desktop or Jetson Nano):

bash
Copy
Edit
python "the orginal.py"
To run the lightweight version (for Raspberry Pi):

bash
Copy
Edit
python "tiny vehicle.py"
🔄 Switching Between YOLO Versions
Inside the script, change the cfg and weights path to switch between YOLOv3 and YOLOv4 tiny versions:

python
Copy
Edit
configPath = "yolov3-tiny.cfg"
weightsPath = "yolov4-tiny.weights"
📊 Output
Detected vehicles are outlined in bounding boxes.

Console prints or GUI overlay show vehicle counts.

Can be extended to trigger GPIO-based signal changes or log data.

🧠 Credits
Developed by Amruthesh Mahesh
Powered by YOLOv3/YOLOv4-tiny and OpenCV
