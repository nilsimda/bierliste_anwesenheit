#!/usr/bin/env python3

import os
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from github import Auth, Github, InputFileContent
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
    driver = webdriver.Chrome(options=options)
    return driver


def accept_cookies():
    cookies_button = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[text()='Alles akzeptieren']")
        )
    )
    cookies_button.click()


def login():
    driver.find_element(by=By.ID, value="loginTrigger").click()
    driver.find_element(By.ID, "inputUsername_top").send_keys(USERNAME)
    driver.find_element(By.ID, "inputPassword_top").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[text()='login']").click()


def get_table():
    table = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
    return table.get_attribute("outerHTML")


def generate_markdown_table(data):
    if not data:
        return "No data to generate table."

    # Determine the maximum width of each column
    col_widths = [max(len(str(item)) for item in col) for col in zip(*data)]

    # Generate the header row
    header = (
        "| "
        + " | ".join(str(data[0][i]).ljust(col_widths[i]) for i in range(len(data[0])))
        + " |"
    )
    separator = "|-" + "-|-".join("-" * width for width in col_widths) + "-|"

    emoji_map = {"ja": ":+1:", "nein": ":-1:", "?": ":grey_question:"}
    # Generate the data rows
    rows = []
    for row in data[1:]:
        mapped_row = [
            emoji_map[entry] if entry in emoji_map else entry for entry in row
        ]
        rows.append(
            "| "
            + " | ".join(
                str(mapped_row[i]).ljust(col_widths[i]) for i in range(len(row))
            )
            + " |"
        )

    # Combine all parts of the table
    return "\n".join([header, separator] + rows)


def parse_header(soup):
    thead = soup.find("thead").find("tr")
    header_data = [" "]

    for column in thead.find_all("th"):
        span = column.find("span", attrs={"title": True})
        if span:
            header_data.append(span.contents[0])
        else:
            a = column.find("a", attrs={"title": True})
            if a:
                header_data.append(a.contents[0])

    return header_data


def parse_body(soup, ignore_players):
    tbody = soup.find("tbody")
    body_data = []

    for row in tbody.find_all("tr"):
        columns = row.find_all("td")
        if columns:
            row_data = []
            for i, column in enumerate(columns):
                if i == 0:
                    row_data.append(column.text.strip())
                else:
                    span = column.find("span", attrs={"data-value": True})
                    if span:
                        row_data.append(span["data-value"])
                    else:
                        button = column.find("button")
                        if button:
                            i_el = button.find("span").find("i")
                            if not i_el:
                                row_data.append("")
                            else:
                                map = {
                                    "fa-thumbs-down": "nein",
                                    "fa-thumbs-up": "ja",
                                    "fa-question": "?",
                                }
                                row_data.append(map[i_el["class"][1]])

            if len(row_data) > 1 and not any(
                row_data[0].startswith(player) for player in ignore_players
            ):
                body_data.append(row_data)

    return body_data


def parse_table(table_html):
    ignore_players = ["Thomas", "Wile", "Amin", "Nanda"]

    soup = BeautifulSoup(table_html, "html.parser")

    table_data = [parse_header(soup)]
    table_data += parse_body(soup, ignore_players)

    return table_data


def get_next_practice(parsed_header):
    return datetime.strptime(parsed_header[1].split(", ")[1], "%d.%m").replace(
        year=datetime.today().year
    )


def upload_to_gist(content):
    auth = Auth.Token(AUTH_TOKEN)
    g = Github(auth=auth)
    g.get_user().login
    gist = g.get_gist(id=GIST_ID)

    gist.edit(
        description="",
        files={"Anwesenheit_Bierliste.md": InputFileContent(content)},
    )
    print("Uploaded to Gist.")


def update_bierlist(table_data):
    bierliste = {name: 0 for name in list(zip(*table_data))[0][1:]}
    with open("bierliste.pickle", "wb") as f:
        pickle.dump(bierliste, f)


if __name__ == "__main__":
    AUTH_TOKEN = os.environ.get("GITHUB_AUTH_TOKEN", default="")
    USERNAME = os.environ.get("VOLLEYBALL_USERNAME", default="")
    PASSWORD = os.environ.get("VOLLEYBALL_PASSWORD", default="")
    GIST_ID = os.environ.get("GIST_ID_VOLLEYBALL", default="")
    URL = "https://www.volleyball-freizeit.de/"
    TEAM_URL = URL + "team/administration/369"

    driver = init_driver()
    driver.get(URL)

    try:
        accept_cookies()
        login()
        print("Login successful!")
        driver.get(TEAM_URL)
    finally:
        table_html = get_table()
        driver.quit()

    assert table_html, "No table found"
    print("Got Attendance table.")

    table_data = parse_table(table_html)
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    next_practice = get_next_practice(table_data[0])

    if tomorrow == next_practice:
        markdown_table = generate_markdown_table(table_data)
        print("Parsed table to markdown.")

        update_md = f"#### Last Update: {datetime.now().strftime('%d %B %Y %H:%M')}\n"
        content = update_md + markdown_table
        upload_to_gist(content)
    elif today == next_practice:
        # TODO: this should compare with the entries from yesterday
        pass
    else:
        print(
            f"Next practice is on {table_data[0][1]}, which is not tomorrow ({tomorrow}). There is nothing to do."
        )
    update_bierlist(table_data)
