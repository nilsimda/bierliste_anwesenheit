from datetime import datetime

from bs4 import BeautifulSoup


class Parser:
    def __init__(self, table_html, ignore_ls=["Thomas", "Wile", "Amin", "Nanda"]):
        self.soup = BeautifulSoup(table_html, "html.parser")
        self.ignore_ls = ignore_ls

        self.table_data = [self._parse_header()]
        self.table_data += self._parse_body()


    def _parse_header(self):
        thead = self.soup.find("thead").find("tr")
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


    def _parse_body(self):
        tbody = self.soup.find("tbody")
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
                                        "fa-thumbs-down": "ja",
                                        "fa-thumbs-up": "nein",
                                        "fa-question": "?",
                                    }
                                    row_data.append(map[i_el["class"][1]])

                if len(row_data) > 1 and not any(
                    row_data[0].startswith(player) for player in self.ignore_ls
                ):
                    body_data.append(row_data)

        return body_data

    def next_practice(self):
        next_date = self.table_data[0][1] # first row second column
        return datetime.strptime(next_date.split(", ")[1], "%d.%m").replace(
            year=datetime.today().year
        )

    def get_attendance(self):
        table_cols = list(zip(*self.table_data))
        return {name: value for name, value in zip(table_cols[0][1:], table_cols[1][1:])}

