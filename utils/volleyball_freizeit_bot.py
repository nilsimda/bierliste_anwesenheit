
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://www.volleyball-freizeit.de/"
TEAM_URL = URL + "team/administration/369"

class VolleyballFreizeitBot:
    def __init__(self, username, password):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
        self.username = username
        self.password = password

    def _accept_cookies(self):
        cookies_button = WebDriverWait(self.driver, 1).until(
            EC.presence_of_element_located(
            (By.XPATH, "//button[text()='Alles akzeptieren']")
            )
        )
        cookies_button.click()


    def _login(self):
        self.driver.find_element(by=By.ID, value="loginTrigger").click()
        self.driver.find_element(By.ID, "inputUsername_top").send_keys(self.username)
        self.driver.find_element(By.ID, "inputPassword_top").send_keys(self.password)
        self.driver.find_element(By.XPATH, "//button[text()='login']").click()


    def get_table(self):
        self._accept_cookies()
        self._login()
        table = WebDriverWait(self.driver, 1).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        return table.get_attribute("outerHTML")

    def quit(self):
        self.driver.quit()


