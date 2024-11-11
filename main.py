#! /usr/bin/env python3

import os
import pickle
from datetime import datetime, timedelta

from utils.parser import Parser
from utils.sheets import SheetsHelper
from utils.volleyball_freizeit_bot import VolleyballFreizeitBot


def update_change(values, attendance_new, attendance_old):
    n_beers = 0
    for key in attendance_new:
        if attendance_old[key] != "x" and attendance_new[key] != attendance_old[key]:
            values[key] += 1
            n_beers += 1
    return n_beers


def update_noentry(values, attendace):
    n_beers = 0
    for key, value in attendace.items():
        if value == "?" or value == "":
            attendace[key] = "x" #mark missed entries so they dont get added twice
            values[key] += 1
            n_beers += 1
    return n_beers

if __name__ == "__main__":
    USERNAME = os.environ.get("VOLLEYBALL_USERNAME", default="")
    PASSWORD = os.environ.get("VOLLEYBALL_PASSWORD", default="")
    SHEETS_ID = os.environ.get("SHEETS_ID", default="")
    CREDS_PATH = os.environ.get("CREDS_PATH", default="")
    TOKEN_PATH = os.environ.get("TOKEN_PATH", default="")

    vf_bot = VolleyballFreizeitBot(USERNAME, PASSWORD)
    table_html = vf_bot.get_table()
    vf_bot.quit()
    print("Got Attendance table.")

    parser = Parser(table_html)
    next_practice = parser.next_practice()
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    if tomorrow == next_practice and datetime.today().hour == 14:
        attendance = parser.get_attendance()
        sheets_helper = SheetsHelper(SHEETS_ID, CREDS_PATH, TOKEN_PATH)
        values = sheets_helper.dowload_from_sheets()

        n_beers = update_noentry(values, attendance)
        print(f"{n_beers} beers added.")

        with open("attendance1400.pickle", "wb") as f:
            pickle.dump(attendance, f)

        sheets_helper.upload_to_sheets(values)

    elif today == next_practice and datetime.today().hour == 20:
        attendance_new = parser.get_attendance()
        sheets_helper = SheetsHelper(SHEETS_ID, CREDS_PATH, TOKEN_PATH)
        values = sheets_helper.dowload_from_sheets()

        with open("attendance1400.pickle", "rb") as f:
            attendance_old = pickle.load(f)

        n_beers = update_change(values, attendance_new, attendance_old)
        print(f"{n_beers} beers added.")
        sheets_helper.upload_to_sheets(values)

    else:
        print(
            f"Next practice/game is on {next_practice}, which is not today ({today}) or tomorrow ({tomorrow}). There is nothing to do."
        )
