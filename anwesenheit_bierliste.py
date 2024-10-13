#!/usr/bin/env python3

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from github import Auth, Github, InputFileContent
from bs4 import BeautifulSoup
from datetime import datetime


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


def parse_table(table_html):
    ignore_players = ["Thomas", "Wile", "Amin", "Nanda"]

    soup = BeautifulSoup(table_html, "html.parser")

    thead = soup.find("thead").find("tr")
    tbody = soup.find("tbody")
    header_data = [" "]

    for column in thead.find_all("th"):
        span = column.find("span", attrs={"title": True})
        if span:
            header_data.append(span["title"].split(",")[0])
        else:
            a = column.find("a", attrs={"title": True})
            if a:
                header_data.append(a["title"].split(">")[1][:-3])

    table_data = [header_data]

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
                table_data.append(row_data)

    return table_data


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


if __name__ == "__main__":
    AUTH_TOKEN = os.environ.get("GITHUB_AUTH_TOKEN")
    USERNAME = os.environ.get("VOLLEYBALL_USERNAME")
    PASSWORD = os.environ.get("VOLLEYBALL_PASSWORD")
    GIST_ID = os.environ.get("GIST_ID_VOLLEYBALL")
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
    markdown_table = generate_markdown_table(table_data)
    print("Parsed table to markdown.")

    update_md = f"#### Last Update: {datetime.now().strftime('%d %B %Y %H:%M')}\n"
    content = update_md + markdown_table
    upload_to_gist(content)
