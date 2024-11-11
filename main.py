#! /usr/bin/env python3

import os
import pickle
from datetime import datetime, timedelta

from utils.parse import parse_table
from utils.sheets import SheetsHelper
from utils.volleyball_freizeit_bot import VolleyballFreizeitBot


def get_next_practice(parsed_header):
    return datetime.strptime(parsed_header[1].split(", ")[1], "%d.%m").replace(
        year=datetime.today().year
    )

def update_bierlist(table_data):
    bierliste = {name: 0 for name in list(zip(*table_data))[0][1:]}
    with open("bierliste.pickle", "wb") as f:
        pickle.dump(bierliste, f)

def save_state():
    #TODO: save the current anmeldungsstate to a file
    pass

def add_beers():
    #TODO: logic that checks who needs to bring a beer
    pass


if __name__ == "__main__":
    USERNAME = os.environ.get("VOLLEYBALL_USERNAME", default="")
    PASSWORD = os.environ.get("VOLLEYBALL_PASSWORD", default="")

    vf_bot = VolleyballFreizeitBot(USERNAME, PASSWORD)
    table_html = vf_bot.get_table()
    vf_bot.quit()
    print("Got Attendance table.")

    table_data = parse_table(table_html)
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    next_practice = get_next_practice(table_data[0])

    if tomorrow == next_practice:
        save_state()

    elif today == next_practice:
        sheets_helper = SheetsHelper()
        values = sheets_helper.dowload_from_sheets()
        update_bierlist(values)
        add_beers()
        sheets_helper.upload_to_sheets(values)
        
        # TODO: this should compare with the entries from yesterday
        pass
    else:
        print(
            f"Next practice is on {table_data[0][1]}, which is not tomorrow ({tomorrow}). There is nothing to do."
        )
