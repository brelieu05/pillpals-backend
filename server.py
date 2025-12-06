from typing import Union, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import time
from datetime import datetime
import pytz
import os
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database file path - use absolute path based on this file's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "history.db")

def init_db():
    """Initialize the database and create the history and alarms tables if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Time TEXT NOT NULL,
            Date TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            days TEXT NOT NULL,
            time TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def get_pst_time():
    """Helper function to get current PST time"""
    pst_timezone = pytz.timezone('US/Pacific')
    now = datetime.now(pytz.utc).astimezone(pst_timezone)
    return {
        "Time": now.strftime('%Y-%m-%d'),
        "Date": now.strftime('%H:%M:%S'),
        "timestamp": now.isoformat()
    }

@app.get("/")
def read_root():
    pst_timezone = pytz.timezone('US/Pacific')
    return {"Time": datetime.now(pytz.utc).astimezone(pst_timezone).strftime('%Y-%m-%d'), "Date": datetime.now(pytz.utc).astimezone(pst_timezone).strftime('%H:%M:%S')}

@app.post("/history")
def add_history():
    """Add a new history entry with current time"""
    try:
        # Ensure database exists and is initialized
        init_db()
        time_data = get_pst_time()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO history (Time, Date, timestamp)
            VALUES (?, ?, ?)
        ''', (time_data["Time"], time_data["Date"], time_data["timestamp"]))
        conn.commit()
        conn.close()
        return {"Time": time_data["Time"], "Date": time_data["Date"]}
    except Exception as e:
        print(f"Error adding history: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.get("/history")
def get_history():
    """Get all history entries"""
    try:
        # Ensure database exists and is initialized
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT Time, Date FROM history ORDER BY timestamp DESC')
        rows = cursor.fetchall()
        conn.close()
        return [{"Time": row[0], "Date": row[1]} for row in rows]
    except Exception as e:
        print(f"Error fetching history: {e}")
        import traceback
        traceback.print_exc()
        return []

class AlarmRequest(BaseModel):
    days: List[str]
    time: str

@app.post("/alarm")
def set_alarm(alarm: AlarmRequest):
    """Save alarm settings to database"""
    try:
        init_db()
        pst_timezone = pytz.timezone('US/Pacific')
        created_at = datetime.now(pytz.utc).astimezone(pst_timezone).isoformat()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Delete existing alarms (only keep the most recent one)
        cursor.execute('DELETE FROM alarms')
        
        # Insert new alarm
        cursor.execute('''
            INSERT INTO alarms (days, time, created_at)
            VALUES (?, ?, ?)
        ''', (json.dumps(alarm.days), alarm.time, created_at))
        conn.commit()
        conn.close()
        
        return {"success": True, "days": alarm.days, "time": alarm.time}
    except Exception as e:
        print(f"Error setting alarm: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.get("/alarm")
def get_alarm():
    """Get the current alarm settings"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT days, time, created_at FROM alarms ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "days": json.loads(row[0]),
                "time": row[1],
                "created_at": row[2]
            }
        else:
            return {"days": [], "time": "", "created_at": None}
    except Exception as e:
        print(f"Error getting alarm: {e}")
        import traceback
        traceback.print_exc()
        return {"days": [], "time": "", "created_at": None}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
