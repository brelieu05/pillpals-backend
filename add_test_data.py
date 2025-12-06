import sqlite3
from datetime import datetime, timedelta
import pytz

DB_PATH = "history.db"

def add_test_data():
    """Add test history entries to the database"""
    pst_timezone = pytz.timezone('US/Pacific')
    
    # Get current time in PST
    now = datetime.now(pytz.utc).astimezone(pst_timezone)
    
    # Create test data for the past 7 days with multiple entries per day
    test_entries = []
    
    # Today - 3 entries
    for i in range(3):
        entry_time = now - timedelta(hours=i*4)
        test_entries.append({
            "Time": entry_time.strftime('%Y-%m-%d'),
            "Date": entry_time.strftime('%H:%M:%S'),
            "timestamp": entry_time.isoformat()
        })
    
    # Yesterday - 2 entries
    yesterday = now - timedelta(days=1)
    for i in range(2):
        entry_time = yesterday.replace(hour=8 + i*6, minute=30, second=0)
        test_entries.append({
            "Time": entry_time.strftime('%Y-%m-%d'),
            "Date": entry_time.strftime('%H:%M:%S'),
            "timestamp": entry_time.isoformat()
        })
    
    # 2 days ago - 1 entry
    two_days_ago = now - timedelta(days=2)
    entry_time = two_days_ago.replace(hour=14, minute=15, second=0)
    test_entries.append({
        "Time": entry_time.strftime('%Y-%m-%d'),
        "Date": entry_time.strftime('%H:%M:%S'),
        "timestamp": entry_time.isoformat()
    })
    
    # 3 days ago - 2 entries
    three_days_ago = now - timedelta(days=3)
    for i in range(2):
        entry_time = three_days_ago.replace(hour=9 + i*5, minute=0, second=0)
        test_entries.append({
            "Time": entry_time.strftime('%Y-%m-%d'),
            "Date": entry_time.strftime('%H:%M:%S'),
            "timestamp": entry_time.isoformat()
        })
    
    # 4 days ago - 1 entry
    four_days_ago = now - timedelta(days=4)
    entry_time = four_days_ago.replace(hour=12, minute=45, second=0)
    test_entries.append({
        "Time": entry_time.strftime('%Y-%m-%d'),
        "Date": entry_time.strftime('%H:%M:%S'),
        "timestamp": entry_time.isoformat()
    })
    
    # 5 days ago - 2 entries
    five_days_ago = now - timedelta(days=5)
    for i in range(2):
        entry_time = five_days_ago.replace(hour=10 + i*4, minute=20, second=0)
        test_entries.append({
            "Time": entry_time.strftime('%Y-%m-%d'),
            "Date": entry_time.strftime('%H:%M:%S'),
            "timestamp": entry_time.isoformat()
        })
    
    # 6 days ago - 1 entry
    six_days_ago = now - timedelta(days=6)
    entry_time = six_days_ago.replace(hour=16, minute=30, second=0)
    test_entries.append({
        "Time": entry_time.strftime('%Y-%m-%d'),
        "Date": entry_time.strftime('%H:%M:%S'),
        "timestamp": entry_time.isoformat()
    })
    
    # Connect to database and insert test data
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM history')
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"Database already has {count} entries. Adding test data anyway...")
    
    # Insert test entries
    for entry in test_entries:
        cursor.execute('''
            INSERT INTO history (Time, Date, timestamp)
            VALUES (?, ?, ?)
        ''', (entry["Time"], entry["Date"], entry["timestamp"]))
    
    conn.commit()
    
    # Verify insertion
    cursor.execute('SELECT COUNT(*) FROM history')
    new_count = cursor.fetchone()[0]
    print(f"Successfully added {len(test_entries)} test entries!")
    print(f"Total entries in database: {new_count}")
    
    # Show some sample entries
    cursor.execute('SELECT Time, Date FROM history ORDER BY timestamp DESC LIMIT 5')
    rows = cursor.fetchall()
    print("\nSample entries (most recent 5):")
    for row in rows:
        print(f"  {row[0]} {row[1]}")
    
    conn.close()

if __name__ == "__main__":
    add_test_data()

