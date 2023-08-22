from selenium.webdriver.common.by import By


class MainLocators:
    BODY = (By.CSS_SELECTOR, "body")
    CARD_BODY_ALERTS = (By.XPATH, "//div[@class='card-body']")
