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
    """Initialize the database and create/update the history and alarms tables if they don't exist"""
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
            time TEXT,
            times TEXT,
            created_at TEXT NOT NULL
        )
    ''')

    # Backfill missing columns for existing DBs (adds times column if missing)
    cursor.execute("PRAGMA table_info(alarms)")
    columns = [row[1] for row in cursor.fetchall()]
    if "times" not in columns:
        cursor.execute("ALTER TABLE alarms ADD COLUMN times TEXT")

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
    times: List[str] | None = None
    time: str | None = None

@app.post("/alarm")
def set_alarm(alarm: AlarmRequest):
    """Save alarm settings to database (supports multiple times per day)"""
    try:
        init_db()
        pst_timezone = pytz.timezone('US/Pacific')
        created_at = datetime.now(pytz.utc).astimezone(pst_timezone).isoformat()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Delete existing alarms (only keep the most recent one)
        cursor.execute('DELETE FROM alarms')
        
        # Normalize payload: allow legacy single time or new times array
        normalized_times = alarm.times if alarm.times is not None else ([alarm.time] if alarm.time else [])
        legacy_time_value = alarm.time if alarm.time else (normalized_times[0] if normalized_times else "")
        
        # Insert new alarm with multiple times
        cursor.execute('''
            INSERT INTO alarms (days, times, time, created_at)
            VALUES (?, ?, ?, ?)
        ''', (json.dumps(alarm.days), json.dumps(normalized_times), legacy_time_value, created_at))
        conn.commit()
        conn.close()
        
        return {"success": True, "days": alarm.days, "times": normalized_times}
    except Exception as e:
        print(f"Error setting alarm: {e}")
        import traceback
        traceback.print_exc()
        raise

@app.get("/alarm")
def get_alarm():
    """Get the current alarm settings (supports multiple times)"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT days, times, time, created_at FROM alarms ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Support legacy single-time records if times is null
            times_value = row[1]
            if times_value:
                times = json.loads(times_value)
            elif row[2]:
                times = [row[2]]
            else:
                times = []
            return {
                "days": json.loads(row[0]) if row[0] else [],
                "times": times,
                "created_at": row[3]
            }
        else:
            return {"days": [], "times": [], "created_at": None}
    except Exception as e:
        print(f"Error getting alarm: {e}")
        import traceback
        traceback.print_exc()
        return {"days": [], "times": [], "created_at": None}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
