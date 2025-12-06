from typing import Union

from fastapi import FastAPI

import time

app = FastAPI()

from datetime import datetime
import pytz

@app.get("/")
def read_root():
    pst_timezone = pytz.timezone('US/Pacific')
    return {"Time": datetime.now(pytz.utc).astimezone(pst_timezone).strftime('%Y-%m-%d'), "Date": datetime.now(pytz.utc).astimezone(pst_timezone).strftime('%H:%M:%S')}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
