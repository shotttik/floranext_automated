from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
import os
from selenium.webdriver.support.select import Select
from dotenv import load_dotenv
from selenium.webdriver.common.keys import Keys
from config import config_browser
from tools import drag_and_drop_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
import json


def access_floranext():
    try:
        config_browser_data = config_browser(headless=False)
        chrome_options = webdriver.ChromeOptions()

        [
            chrome_options.add_argument(option)
            for option in config_browser_data["options"]
        ]

        [
            chrome_options.add_experimental_option(option[0], option[1])
            for option in config_browser_data["experimental_options"]
        ]

        if config_browser_data["browser"] == 'chrome':
            driver = webdriver.Chrome(service=Service(
                ChromeDriverManager().install()), options=chrome_options)

        elif config_browser_data["browser"] == 'firefox':
            driver = webdriver.Firefox(service=Service(
                GeckoDriverManager().install()), options=chrome_options)
        else:
            assert ("Support for Firefox or Chrome only!")

        # avoid recaptcha error
        user_agent = ""
        for o in config_browser_data["options"]:
            if "user-agent" in o:
                user_agent = o.replace("user-agent=", "")
                break
        stealth(driver,
                user_agent=user_agent,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        driver.get(config_browser_data["base_url"])
        '''
        In the code down, Selenium will wait for a maximum of
        10 seconds for an element matching the given criteria to be found.
        If no element is found in that time, a TimeoutException is thrown
        we are trying to get user input if we get it, we get access to floranext
        '''
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "body"))
        )
        return {"Driver": driver, "Config_Browser": config_browser_data}
    except Exception as e:
        print(e)
        driver.quit()
        return {"Exception": e}


def get_recaptcha_score(driver, config_browser_data):
    driver.get(config_browser_data["recaptcha_score_url"])
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, ".go").click()
    time.sleep(5)
    response = driver.find_element(By.CSS_SELECTOR, ".response").text
    json_response = json.loads(response)
    driver.get(config_browser_data["base_url"])
    return json_response["score"]


def authorization(driver):
    try:
        load_dotenv(".env")
        # email = os.getenv("ADMIN_EMAIL")
        email = "Dev@BloomNWA.com"
        # pswd = os.getenv("ADMIN_PASSWORD")
        pswd = "Dev&1234"
        # email, pswd = get_cretendtials() if we have credentials.txt inside email:passwd
        time.sleep(5)
        email_inputs = driver.find_elements(
            By.CSS_SELECTOR, '#username')
        if (len(email_inputs) != 0):
            email_input = email_inputs[0]
            email_input.send_keys("for")
            time.sleep(3)
            email_input.clear()
            time.sleep(3)
            email_input.send_keys(email)
            time.sleep(3)
            # print(email_input.get_attribute('value'))
            # we sleep program to avoid any issues/errors during automation process
            pswd_input = driver.find_element(By.CSS_SELECTOR, "#login")
            pswd_input.send_keys("for")
            time.sleep(2)
            pswd_input.clear()
            time.sleep(2)
            pswd_input.send_keys(pswd)
            # print(pswd_input.get_attribute('value'))
            # driver.execute_script(
            # f"document.querySelector('#login').value = '{pswd}'")
            time.sleep(3)
            login_btn = driver.find_element(
                By.XPATH, "//div[@class='actions']//button[contains(class, action-login)]")
            login_btn.click()
        # Check if admin webpage loaded and authorization finished successfully
        # In teh code down, Selenium will find Orders link from top nav bar and redirect to the orders page
        time.sleep(10)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "#menu-magento-sales-sales > a"))
        )[0].click()
        time.sleep(3)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='submenu']//li[@data-ui-id='menu-magento-sales-sales-order']"))
        ).click()
        time.sleep(5)
        return {"Sucessfully": "Sucessfully"}
    except Exception as e:
        error = driver.find_elements(By.CSS_SELECTOR, ".message-error div")
        if error:
            print(error[0].text)
            driver.find_element(By.CSS_SELECTOR, ".logo-img").click()
        print(e)
        return {"Exception": e}


def find_order(driver, order_number):
    try:
        time.sleep(3)
        search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#partialText"))
        )
        search.clear()
        search.send_keys(order_number)
        time.sleep(2)
        driver.execute_script(
            f"document.querySelector('#partialText').value = '{order_number}'")
        time.sleep(2)
        search.click()
        time.sleep(2)
        search.send_keys("A")
        search.send_keys(Keys.BACKSPACE)
        time.sleep(2)
        search.send_keys(Keys.ENTER)
        time.sleep(2)
        # enter ito search
        # wait for search results
        # if order not found raise exceptionapapp
        time.sleep(15)
        driver.find_element(
            By.XPATH, f"//div[contains(text(), '{order_number}')]")
        return {"Sucessfully": "Sucessfully"}
    except Exception as e:
        return {"Exception": e}


def check_deliverydate(driver, order_number):
    try:
        # for ex. dd = 'Aug 1, 2022'
        time.sleep(2)
        dd = driver.find_element(
            By.XPATH, f"//div[contains(text(), '{order_number}')]//..//../td[3]/div").text
        # string to datetime object with format  for this example 'Aug 1, 2022'
        dd_obj = datetime.strptime(dd, "%b %d, %Y").date()
        today_date = datetime.today().date()
        # checking if Delivery Date is in the past
        if today_date > dd_obj:
            return {"Error": "Error"}
        # Clicking veiw blue button
        time.sleep(2)
        view_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[contains(text(), '{order_number}')]//..//..//a[@class='action-menu-item']"))
        )
        actions = ActionChains(driver)
        actions.move_to_element(view_btn)
        actions.click(view_btn)
        actions.perform()
        time.sleep(10)
        return {"Sucessfully": "Sucessfully"}
    except Exception as e:
        return {"Exception": e}


def check_product_photo(driver):
    try:
        time.sleep(5)
        image_rmv_btn = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'image-uploader-preview')]//div[@class='actions']//button")
        if image_rmv_btn:
            btn = image_rmv_btn[0]
            # clicking to the trash button
            actions = ActionChains(driver)
            actions.move_to_element(btn)
            actions.click(btn)
            actions.perform()
            time.sleep(10)
            return "Deleted"
        return "Noexist"
    except Exception as e:
        return {"Exception": e}


def upload_image(driver, img_name):
    try:
        img_path = os.getcwd() + "/" + img_name
        input_img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 "//div[@class='file-uploader-summary product-image-wrapper']"))
        )

        drag_and_drop_file(input_img, img_path)
        # @TODO need to cchange to iframe click done and thats it
        time.sleep(20)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH, "//button[@class='doka--button doka--button-app doka--button-action-confirm doka--button-icon-fallback']"))
        ).click()

        time.sleep(20)
        uploaded_img = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'image-uploader-preview')]//div[@class='actions']//button")
        # Double Check that image was successfully uploaded.
        if not uploaded_img:
            time.sleep(5)
            uploaded_img = driver.find_elements(
                By.CSS_SELECTOR, "#sales_order_view_tabs_order_info_content > div > div.box-right > div > fieldset > div > section > section > section > section > img")
            if uploaded_img:
                return "Successfully"
            else:
                return "Error"
        else:
            return "Successfully"
    except Exception as e:
        return {"Exception": e}


def back_to_orders(driver):
    time.sleep(2)
    # Scrolling up to top of the page to click back button without issues
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(2)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[@id='back']"))
    ).click()
    '''
    Wait before orders page not loaded
    we are checking for search orders input if it loaded webpage loaded.
    if not it will raise an exception
    '''
    time.sleep(10)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@id='partialText']"))
    )


def select_designer(driver, designer):
    try:
        time.sleep(2)
        '''
        we are trying to find our designer in options
        if we dont find it we will return error and script will continue
        '''
        options = driver.find_elements(
            By.CSS_SELECTOR, "#designer-order > option")
        our_option = [option for option in options if option.text == designer]
        if not our_option:
            return "Error"
        our_option[0].click()
        time.sleep(3)
        return "Successfully"
    except Exception as e:
        return {"Exception": e}


def change_status(driver):
    try:
        time.sleep(2)
        order_type = driver.find_element(
            By.CSS_SELECTOR, ".order-store-details-information-table tr:nth-child(3) td").text.split(" / ")[1]
        change_status = f"Ready for {order_type}"
        options = driver.find_elements(
            By.CSS_SELECTOR, "#order_status > option")
        # Getting select element to easily get which status is selected
        select = Select(driver.find_element(
            By.CSS_SELECTOR, "#order_status"))
        current = select.first_selected_option.text
        if current == "Order Received" or current == "In Progress" or current == "Design Complete":

            must_select = [
                option for option in options if option.text == change_status
            ]
            if not must_select:
                return "Error"
            must_select[0].click()
            time.sleep(5)
            send_text_message_popup = driver.find_elements(
                By.XPATH, '//footer//button[@class="action-secondary action-dismiss"]')
            if send_text_message_popup:
                send_text_message_popup[0].click()
            changed = select.first_selected_option.text
            # double Checking if order status changed
            # if not changed try again to change order status
            if changed == change_status:
                return current, changed
            must_select[0].click()
            time.sleep(2)
            changed = select.first_selected_option.text
            if changed == change_status:
                return current, changed
            return "Error"
        else:
            return {"Current": current}
    except Exception as e:
        return {"Exception": e}
