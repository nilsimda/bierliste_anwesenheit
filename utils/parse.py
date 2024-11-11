from bs4 import BeautifulSoup


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
    ignore_players = ["Thomas", "Wile", "Amin", "Nanda", "Anastasija"]

    soup = BeautifulSoup(table_html, "html.parser")

    table_data = [parse_header(soup)]
    table_data += parse_body(soup, ignore_players)

    return table_data
