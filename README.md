# Automatic License Plate Recognition (ALPR) Toll Collection System 🚗🚦

An intelligent, computer vision-based barrier-free toll collection system. This project automatically detects vehicle license plates using a YOLOv8 detection model, extracts the license plate text using PaddleOCR, and processes the toll transaction against an SQLite database—all surfaced through a modern REST API and a React frontend.

---

## 🌟 Key Features

- **License Plate Detection:** High-accuracy license plate bounding box extraction using a fine-tuned YOLOv8 model (`license-plate-finetune-v1m.pt`).
- **Optical Character Recognition (OCR):** Uses PaddleOCR with angle classification to extract alphanumeric plate text under varying conditions.
- **Toll Processing Engine:** Automatically searches for the registered plate in the database and deducts the appropriate toll amount, returning the user's updated balance and transaction status.
- **RESTful API Backend:** A robust FastAPI backend exposing endpoints for health checks, user management, and image processing.
- **Modern Web Interface:** A fast and responsive frontend built with React, Vite, and TailwindCSS to interact with the API and display detections in real-time.
- **Real-Time Video/Image Processing:** A standalone `main.py` script to directly process video files (`.mp4`) or images via OpenCV to demonstrate the barrier-free system.

---

## 🛠️ Technology Stack

### Backend
- **Python 3.11**
- **FastAPI:** Fast, modern backend API architecture.
- **OpenCV (`cv2`):** Image and video frame processing.
- **Ultralytics (YOLOv8):** Custom-trained object detection model.
- **PaddleOCR:** Robust text recognition.
- **SQLite:** Lightweight local database for users and transactions.

### Frontend
- **React 19**
- **Vite:** High-performance built tool.
- **TailwindCSS 4:** Utility-first CSS framework for styling.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js (for the frontend)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/Sahil-2005/Toll_Collection_System.git
cd Toll_Collection_System
```

### 2. Backend Setup
Set up the Python virtual environment and install the required dependencies:

**For Windows:**
```bash
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
```

**For Mac/Linux:**
```bash
python3 -m venv myenv
source myenv/bin/activate
pip3 install -r requirements.txt
```

*(Note: The `models` directory contains the required YOLOv8 `.pt` weight files. Do not modify or delete them.)*

**Initialize the Database:**
You can seed the initial mock data into the SQLite database:
```bash
python seed_database.py
```

**Start the FastAPI Server:**
```bash
# Start the backend server on http://localhost:8000
uvicorn src.api:app --reload
```

*(Alternatively, to run the standalone OpenCV demo directly on a video or image feed, execute `python src/main.py`)*

### 3. Frontend Setup
In a new terminal window, initialize and run the React client:
```bash
cd client
npm install
npm run dev
```
The web application will be accessible at `http://localhost:5173`.

---

## 📁 Project Structure

```text
Toll_Collection_System/
│
├── client/                 # React + Vite frontend application
├── database/               # SQLite database directory containing toll_data.db
├── data/                   # Demo data (images/videos) for standalone testing
├── models/                 # Fine-tuned YOLOv8 weights (*.pt)
├── src/                    # Backend source code
│   ├── api.py              # FastAPI application and endpoints
│   ├── db_manager.py       # SQLite database connector and business logic
│   ├── detector.py         # YOLO License Plate Detection wrapper
│   ├── main.py             # OpenCV standalone demonstration script
│   └── ocr_engine.py       # PaddleOCR text extraction wrapper
│
├── requirements.txt        # Python backend dependencies
├── seed_database.py        # Database setup and mock data seed script
└── README.md               # Project documentation
```

---

## 📡 API Endpoints

- `GET /api/health` - Check backend health status.
- `GET /api/users` - Retrieve all registered users.
- `GET /api/users/{plate_number}` - Lookup a specific user by license plate.
- `POST /api/process-image` - Upload an image to run ALPR and process a toll transaction. Returns the cropped text, bounding box coordinates, and the updated database status.

---

## 👤 Author

Developed by **Sahil Gawade**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Sahil-2005)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sahil-gawade-920a0a242/)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:gawadesahil.dev@gmail.com)
[![LeetCode](https://img.shields.io/badge/LeetCode-FFA116?style=for-the-badge&logo=leetcode&logoColor=black)](https://leetcode.com/u/sahilgawade4321/)
[![Portfolio](https://img.shields.io/badge/Portfolio-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://sahil-gawade.vercel.app/)
