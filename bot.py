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
from webdriver import Browser


def access_floranext():
    try:
        config_browser_data = config_browser()
        Browser(config_browser_data)

        '''
        In the code down, Selenium will wait for a maximum of
        10 seconds for an element matching the given criteria to be found.
        If no element is found in that time, a TimeoutException is thrown
        we are trying to get user input if we get it, we get access to floranext
        '''
        WebDriverWait(Browser.getDriver(), 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        return {"Sucessfully": "Sucessfully"}
    except Exception as e:
        Browser.quit()
        return {"Exception": e}


def authorization():
    try:
        load_dotenv(".env")
        # email = os.getenv("ADMIN_EMAIL")
        email = "Dev@BloomNWA.com"
        # pswd = os.getenv("ADMIN_PASSWORD")
        pswd = "Dev&1234"
        # email, pswd = get_cretendtials() if we have credentials.txt inside email:passwd
        time.sleep(5)
        orders_title = Browser.getDriver().find_elements(
            By.XPATH, '//div[@class="page-main-actions"]//h1[text()="Orders"]')
        if (len(orders_title) == 0):
            email_input = Browser.getDriver().find_element(
                By.CSS_SELECTOR, "#username")
            email_input.send_keys("for")
            time.sleep(3)
            email_input.clear()
            time.sleep(3)
            email_input.send_keys(email)
            time.sleep(3)
            # print(email_input.get_attribute('value'))
            # we sleep program to avoid any issues/errors during automation process
            pswd_input = Browser.getDriver().find_element(By.CSS_SELECTOR, "#login")
            pswd_input.send_keys("for")
            time.sleep(2)
            pswd_input.clear()
            time.sleep(2)
            pswd_input.send_keys(pswd)
            # print(pswd_input.get_attribute('value'))
            # Browser.getDriver().execute_script(
            # f"document.querySelector('#login').value = '{pswd}'")
            time.sleep(3)
            login_btn = Browser.getDriver().find_element(
                By.XPATH, "//div[@class='actions']//button[contains(class, action-login)]")
            login_btn.click()
        # Check if admin webpage loaded and authorization finished successfully
        # In teh code down, Selenium will find Orders link from top nav bar and redirect to the orders page
        WebDriverWait(Browser.getDriver(), 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#menu-magento-sales-sales"))
        )
        time.sleep(3)
        WebDriverWait(Browser.getDriver(), 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#menu-magento-sales-sales > a"))
        ).click()
        time.sleep(3)
        WebDriverWait(Browser.getDriver(), 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@class='submenu']//li[@data-ui-id='menu-magento-sales-sales-order']"))
        ).click()
        time.sleep(3)
        return {"Sucessfully": "Sucessfully"}
    except Exception as e:
        Browser.quit()
        print(e)
        return {"Exception": e}


def find_order(order_number):
    try:
        time.sleep(3)
        search = WebDriverWait(Browser.getDriver(), 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#partialText"))
        )
        search.clear()
        search.send_keys(order_number)
        time.sleep(2)
        Browser.getDriver().execute_script(
            f"document.querySelector('#partialText').value = '{order_number}'")
        time.sleep(2)
        search.send_keys(Keys.ENTER)
        time.sleep(2)
        # enter ito search
        # wait for search results
        # if order not found raise exception
        time.sleep(10)
        WebDriverWait(Browser.getDriver(), 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//td//div[contains(text(), '{order_number}')]"))
        )
        return {"Sucessfully": "Sucessfully"}
    except Exception as e:
        return {"Exception": e}


def check_deliverydate(order_number):
    try:
        # for ex. dd = 'Aug 1, 2022'
        time.sleep(2)
        dd = Browser.getDriver().find_element(
            By.XPATH, f"//div[contains(text(), '{order_number}')]//..//../td[3]/div").text
        # string to datetime object with format  for this example 'Aug 1, 2022'
        dd_obj = datetime.strptime(dd, "%b %d, %Y").date()
        today_date = datetime.today().date()
        # checking if Delivery Date is in the past
        if today_date > dd_obj:
            return {"Error": "Error"}
        # Clicking veiw blue button
        time.sleep(2)
        view_btn = WebDriverWait(Browser.getDriver(), 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[contains(text(), '{order_number}')]//..//..//a[@class='action-menu-item']"))
        )
        actions = ActionChains(Browser.getDriver())
        actions.move_to_element(view_btn)
        actions.click(view_btn)
        actions.perform()
        time.sleep(10)
        return {"Sucessfully": "Sucessfully"}
    except Exception as e:
        return {"Exception": e}


def check_product_photo():
    try:
        time.sleep(5)
        image_rmv_btn = Browser.getDriver().find_elements(
            By.XPATH, "//div[contains(@class, 'image-uploader-preview')]//div[@class='actions']//button")
        if image_rmv_btn:
            btn = image_rmv_btn[0]
            # clicking to the trash button
            actions = ActionChains(Browser.getDriver())
            actions.move_to_element(btn)
            actions.click(btn)
            actions.perform()
            time.sleep(10)
            return "Deleted"
        return "Noexist"
    except Exception as e:
        return {"Exception": e}


def upload_image(img_name):
    try:
        img_path = os.getcwd() + "/" + img_name
        input_img = WebDriverWait(Browser.getDriver(), 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 "//div[@class='file-uploader-summary product-image-wrapper']"))
        )

        drag_and_drop_file(input_img, img_path)
        # @TODO need to cchange to iframe click done and thats it
        time.sleep(20)
        WebDriverWait(Browser.getDriver(), 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH, "//button[@class='doka--button doka--button-app doka--button-action-confirm doka--button-icon-fallback']"))
        ).click()

        time.sleep(20)
        uploaded_img = Browser.getDriver().find_elements(
            By.XPATH, "//div[contains(@class, 'image-uploader-preview')]//div[@class='actions']//button")
        # Double Check that image was successfully uploaded.
        if not uploaded_img:
            time.sleep(5)
            uploaded_img = Browser.getDriver().find_elements(
                By.CSS_SELECTOR, "#sales_order_view_tabs_order_info_content > div > div.box-right > div > fieldset > div > section > section > section > section > img")
            if uploaded_img:
                return "Successfully"
            else:
                return "Error"
        else:
            return "Successfully"
    except Exception as e:
        return {"Exception": e}


def back_to_orders():
    time.sleep(2)
    # Scrolling up to top of the page to click back button without issues
    Browser.getDriver().execute_script("window.scrollTo(0, 0)")
    time.sleep(2)
    WebDriverWait(Browser.getDriver(), 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//button[@id='back']"))
    ).click()
    '''
    Wait before orders page not loaded
    we are checking for search orders input if it loaded webpage loaded.
    if not it will raise an exception
    '''
    time.sleep(10)
    WebDriverWait(Browser.getDriver(), 10).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@id='partialText']"))
    )


def select_designer(designer):
    try:
        time.sleep(2)
        '''
        we are trying to find our designer in options
        if we dont find it we will return error and script will continue
        '''
        options = Browser.getDriver().find_elements(
            By.CSS_SELECTOR, "#designer-order > option")
        our_option = [option for option in options if option.text == designer]
        if not our_option:
            return "Error"
        our_option[0].click()
        time.sleep(3)
        return "Successfully"
    except Exception as e:
        return {"Exception": e}


def change_status():
    try:
        time.sleep(2)
        order_type = Browser.getDriver().find_element(
            By.CSS_SELECTOR, ".order-store-details-information-table tr:nth-child(3) td").text.split(" / ")[1]
        change_status = f"Ready for {order_type}"
        options = Browser.getDriver().find_elements(
            By.CSS_SELECTOR, "#order_status > option")
        # Getting select element to easily get which status is selected
        select = Select(Browser.getDriver().find_element(
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
            send_text_message_popup = Browser.getDriver().find_elements(
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
