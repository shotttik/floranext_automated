from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
import os
from selenium.webdriver.support.select import Select
from dotenv import load_dotenv


def access_floranext():
    try:
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.headless = True  # if you want to see webdriver window make it false
        prefs = {"download.default_directory": "./"}
        chrome_options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome("./chromedriver", options=chrome_options)
        driver.get("https://pos.floranext.com/bloomnwa_com/admin/")

        '''
        In the code down, Selenium will wait for a maximum of
        10 seconds for an element matching the given criteria to be found.
        If no element is found in that time, a TimeoutException is thrown
        we are trying to get user input if we get it, we get access to floranext
        '''
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#username"))
        )
        return {"Driver": driver}
    except Exception as e:
        return {"Exception": e}


def authorization(driver):
    try:
        load_dotenv(".env")
        email = os.getenv("ADMIN_EMAIL")
        pswd = os.getenv("ADMIN_PASSWORD")

        # email, pswd = get_cretendtials() if we have credentials.txt inside email:passwd
        email_input = driver.find_element(By.CSS_SELECTOR, "#username")
        email_input.send_keys(email)
        # we sleep program to avoid any issues/errors during automation process
        time.sleep(2)
        pswd_input = driver.find_element(By.CSS_SELECTOR, "#login")
        time.sleep(2)
        # pswd_input.send_keys(pswd)
        driver.execute_script(
            f"document.querySelector('#login').value = '{pswd}'")
        time.sleep(2)
        login_btn = driver.find_element(
            By.CSS_SELECTOR, "#loginForm > div > div:nth-child(3) > footer > div > button")
        login_btn.click()

        # Check if admin webpage loaded and authorization finished successfully
        # In teh code down, Selenium will find Orders link from top nav bar and redirect to the orders page
        time.sleep(4)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#html-body > div.wrapper > div.header > div > div.nav--main.flex.flex--rows.row > ul > li.nav__item.parent.dashboard.level0 > a > span"))
        ).click()

        # Check if order webpage loaded to do looping for each record
        time.sleep(4)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'Order Number')]"))
        )
        return {"Sucessfully": "Sucessfully"}
    except Exception as e:
        return {"Exception": e}


def find_order(driver, order_number):
    try:
        time.sleep(4)
        search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#grid_tab_orders_content > div.grid.np > div.search_container > input[type=text]"))
        )
        search.clear()
        # search.send_keys(order_number)
        driver.execute_script(
            f"document.querySelector('#grid_tab_orders_content > div.grid.np > div.search_container > input[type=text]').value = '{order_number}'")
        time.sleep(2)
        # click to the search button
        driver.find_element(
            By.CSS_SELECTOR, "#grid_tab_orders_content > div.grid.np > div.search_container > button").click()
        # wait for search results
        # if order found if not raise exception and we will catch it
        time.sleep(4)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.form-button.green"))
        )
        return {"Sucessfully": "Sucessfully"}
    except Exception as e:
        return {"Exception": e}


def check_deliverydate(driver):
    try:
        # for ex. dd = 'Aug 1, 2022'
        time.sleep(4)
        dd = driver.find_element(
            By.CSS_SELECTOR, "#lastOrdersGrid_table > tbody > tr > td:nth-child(3)").text
        # string to datetime object with format  for this example 'Aug 1, 2022'
        dd_obj = datetime.strptime(dd, "%b %d, %Y")
        today_date = datetime.today()
        # checking if Delivery Date is in the past
        if today_date > dd_obj:
            return {"Error": "Error"}
        # Clicking vew green button
        time.sleep(4)
        view_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.form-button.green"))
        )
        actions = ActionChains(driver)
        actions.move_to_element(view_btn)
        actions.click(view_btn)
        actions.perform()
        return {"Sucessfully": "Sucessfully"}
    except Exception as e:
        return {"Exception": e}


def check_product_photo(driver):
    try:
        time.sleep(4)
        image_rmv_btn = driver.find_elements(
            By.CSS_SELECTOR, "#sales_order_view_tabs_order_info_content > div > div.box-right > div > fieldset > div > section > section > section > section > section > img")
        if image_rmv_btn:
            btn = image_rmv_btn[0]
            # need to hover section to driver see red X and then need to click it
            section = driver.find_element(
                By.CSS_SELECTOR, "#sales_order_view_tabs_order_info_content > div > div.box-right > div > fieldset > div > section > section > section > section")
            actions = ActionChains(driver)
            actions.move_to_element(section).perform()
            actions.move_to_element(btn)
            actions.click(btn)
            actions.perform()
            time.sleep(2)
            alert = driver.switch_to.alert
            alert.accept()
            time.sleep(4)
            return "Deleted"
        return "Noexist"
    except Exception as e:
        return {"Exception": e}


def upload_image(driver, img_name):
    try:
        img_path = os.getcwd() + "/" + img_name
        input_img = driver.find_element(By.CSS_SELECTOR,
                                        "#sales_order_view_tabs_order_info_content > div > div.box-right > div > fieldset > div > section > section > input")
        input_img.send_keys(img_path)
        time.sleep(4)
        uploaded_img = driver.find_elements(
            By.CSS_SELECTOR, "#sales_order_view_tabs_order_info_content > div > div.box-right > div > fieldset > div > section > section > section > section > img")
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
    time.sleep(4)
    # Scrolling up to top of the page to click back button without issues
    driver.execute_script("window.scrollTo(0, 0)")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#html-body > div.wrapper > div.content-header > div > div > p.form-buttons.default-buttons > button"))
    ).click()
    '''
    Wait before orders page not loaded
    we are checking for search orders input if it loaded webpage loaded.
    if not it will raise an exception
    '''
    time.sleep(4)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#grid_tab_orders_content > div.grid.np > div.search_container > input[type=text]"))
    )


def select_designer(driver, designer):
    try:
        time.sleep(4)
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
        time.sleep(4)
        options = driver.find_elements(
            By.CSS_SELECTOR, "#delivery_status > option")
        # Getting select element to easily get which status is selected
        select = Select(driver.find_element(
            By.CSS_SELECTOR, "#delivery_status"))
        current = select.first_selected_option.text
        if current == "Order Received" or current == "In Progress" or current == "Design Complete":
            must_select = [
                option for option in options if option.text == "Ready for Delivery"
            ]
            if not must_select:
                return "Error"
            must_select[0].click()
            time.sleep(3)
            changed = select.first_selected_option.text
            # double Checking if order status changed
            # if not changed try again to change order status
            if changed == "Ready for Delivery":
                return current, changed
            must_select[0].click()
            time.sleep(3)
            changed = select.first_selected_option.text
            if changed == "Ready for Delivery":
                return current, changed
            return "Error"
        else:
            return {"Current": current}
    except Exception as e:
        return {"Exception": e}
