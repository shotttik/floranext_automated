from tools import delete_from_queue, delete_image, delete_logs, save_image, scrap_images, clean_record, send_error_message, send_mail
from bot import access_floranext, authorization, back_to_orders, change_status, check_product_photo, find_order, check_deliverydate, select_designer, upload_image, get_recaptcha_score
from datetime import datetime
import logging
import sys
today = datetime.today().date().isoformat()

FLAGGED_ERRORS = []
# Creating logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='{levelname} {asctime} - {message}',
    datefmt='%Y-%m-%d %H:%M:%S',
    style='{',
    filename=f'logs/{today}.log',
    filemode='a',
)

# Comment next line if you want to see debug info in log files.
logging.disable(logging.DEBUG)

# changed file mode in line 17 'w' to 'a' if w it will clear a log 'a' will open and continue writing

logging.info('Script Started.')

delete_logs()
logging.info('Old Log Files Deleted.')

logging.info('Accessing Image Upload Queue on KHLORIS.')
records = scrap_images()

# if 0 records found
if records is None:
    logging.info("0 Records Found, Exiting Script.")
    sys.exit(1)
elif records.get("Exception", None):
    logging.error(
        'Unable to Access Image Upload Queue on KHLORIS.')
    send_mail(
        subject="Image Upload Queue Error",
        message="Unable to Access Image Upload Queue on KHLORIS",
    )
    sys.exit(1)
else:
    records = records.get("Records")

data = []

# Scrape data for each record including fields and creating json
# inside records we have beautiful soups
for record in records:
    # beautiful soup to string to get clean json
    r = str(record.findAll("td")[1])
    r_data = clean_record(r)
    # if couldn't got order number will get null
    order_number = r_data.get("Order Number", "NULL")
    logging.info(
        f'Captured Data for Order {order_number}.')
    data.append(r_data)

# Access Floranext Admin Site at: https://pos.floranext.com/bloomnwa_com/admin/
response = access_floranext()
config_browser_data = {}
if response.get("Exception", None):
    exception_msg = str(response.get("Exception"))
    logging.error(
        'Unable to Access Floranext.'
    )
    send_mail(
        subject='Unable to Access Floranext.',
        message=exception_msg)
    sys.exit(1)
else:
    driver = response.get("Driver")
    config_browser_data = response.get("Config_Browser", None)

# Login to Floranext Admin
max_attempts = 3
score = get_recaptcha_score(driver, config_browser_data)
for i in range(max_attempts):
    logging.info(f"Getting Browser's reCAPTCHA-v3 Score.")
    logging.info(f"Your Browser's reCAPTCHA-v3 Score is: {score}.")
    logging.info(
        f"Attempting to Login to Floranext,  Attempt: {i+1} of {max_attempts}.")
    response = authorization(driver)
    if response.get("Sucessfully", None):
        logging.info(f"Login to Floranext Successful.")
        break
    elif response.get("Exception", None) and i == 4:
        exception_msg = str(response.get("Exception"))
        logging.error(
            "Unable to Login to Floranext."
        )
        send_mail(
            subject='Unable to Login to Floranext.',
            message=exception_msg)
        driver.quit()
        sys.exit(1)

for record in data:
    order_number = record.get('Order Number', None)
    designer = record.get('Designer', None)
    record_id = record.get('Record ID', None)
    image_location = record.get('Image Location', None)

    logging.info(
        f'Processing Order Number {order_number}.')

    if order_number is None:
        logging.error(
            "Record Has No Order Number. Skipping Processing."
        )
        continue
    if designer is None:
        logging.error(
            "Record Has No Designer. Skipping Processing."
        )
        continue
    if record_id is None:
        logging.error(
            "Record Has No Record ID. Skipping Processing."
        )
        continue
    if image_location is None:
        logging.error(
            "Record Has No Image Location. Skipping Processing."
        )
        continue

    # STEP: In Search Orders field Type Order Number for current record and press Enter.
    logging.info(f"Searching for Order.")
    find_status = find_order(driver, order_number)
    # If no record found, sending email, and sending api error message
    if find_status.get("Exception", None):
        exception_msg = str(find_status.get("Exception"))

        send_mail(
            subject=f'Image Upload Error / Order: {order_number}',
            message=f'''Image upload tool could not process order {order_number} because the order number is not valid in Floranext.
            '''
        )
        send_error_message(
            record_id, "Error: Order number not valid in Floranext!")

        logging.error(
            "Order Not Found. Skipping Order."
        )
        continue
    else:
        find_status = find_status.get("Sucessfully")

    # Once the Order loads check the delivery date
    check_del_status = check_deliverydate(driver, order_number)
    # If Delivery Date is in the past or some error occurs
    if check_del_status.get("Error", None):
        send_mail(
            subject=f'Image Upload Error / Order: {order_number}',
            message=f'''Image for Order {order_number} not uploaded because the delivery date in floranext is in the past. Please check that the order number is correct.
            '''
        )
        send_error_message(
            record_id, "Error: Delivery date not current in Floranext!")
        logging.error(
            "Delivery Date Not Current, Skipping Order."
        )
        continue
    elif check_del_status.get("Exception", None):
        exception_msg = str(check_del_status.get("Exception"))
        send_mail(
            subject=f'Image Upload Error / Order: {order_number}',
            message=f'''Error: Image for order {order_number} not uploaded because the delivery date in floranext is in the past. Please check that the order number is correct.
            '''
        )
        send_error_message(
            record_id, "Image Upload Tool returned the following Error: Delivery date not current.")
        logging.error(
            "Delivery Date Not Current, Skipping Order."
        )
        continue
    else:
        check_del_status = check_del_status.get("Sucessfully")
    '''In the Product Photo Section, Delete any existing image which may be attached to the
    image by clicking the red X (if applicable).
    '''
    checked = check_product_photo(driver)
    if checked == "Deleted":
        logging.info("Deleting Existing Image, Uploading New Order Image.")
    elif checked == "Noexist":
        logging.info("Uploading Order Image.")
    else:
        exception_msg = str(checked.get("Exception"))
        logging.error(f"We got an error {exception_msg}")
        send_error_message(record_id, "Deleting Existing image failed.")
        FLAGGED_ERRORS.append(
            f"{str(datetime.now())} Record ID: {record_id}, {exception_msg}")
        back_to_orders(driver)
        continue

    '''
    for example this is image location
    https://khloris.bloomnwa.com/iut/OrderImage/1/100049552/16529657061607462732434894867644.jpg
    we are downloading image to upload in website
    downloading in existing folder where this python file is located and
    after that we are deleteing image
    '''
    img_name = image_location.split("/")[-1]
    save_image(image_location)
    uploaded = upload_image(driver, img_name)
    delete_image(img_name)

    if uploaded == "Successfully":
        logging.info("Order Image Successfully Uploaded.")
    elif uploaded == "Error":
        logging.error("Unable to Upload Order Image, Skipping Order.")
        FLAGGED_ERRORS.append(
            f"{str(datetime.now())} Record ID: {record_id}, Unable to upload image. Skipping order.")
        back_to_orders(driver)
        continue
    else:
        exception_msg = str(uploaded.get("Exception"))
        send_error_message(record_id, "Unable to upload image")
        logging.error("unable to upload image")
        FLAGGED_ERRORS.append(
            f"{str(datetime.now())} Record ID: {record_id}, {exception_msg}")
        back_to_orders(driver)
        continue

    # Select desginer
    selected = select_designer(driver, designer)
    if selected == "Successfully":
        logging.info(f"Designer set to {designer}.")
    elif selected == "Error":
        logging.error(f"Unable to set Designer to {designer}.")
        FLAGGED_ERRORS.append(
            f"{str(datetime.now())} Record ID: {record_id}, Unable to set Designer to {designer}.")
    else:
        logging.error(f"Unable to set Designer to {designer}.")
        exception_msg = str(selected.get("Exception"))
        FLAGGED_ERRORS.append(
            f"{str(datetime.now())} Record ID: {record_id}, {exception_msg}")

    # change order status
    status = change_status(driver)
    if type(status) == tuple:
        current, changed = status
        logging.info(
            f"Current Order Status is {current}, Status Changed to {changed}.")
    elif status == "Error":
        logging.error(
            f"Unable to Change Order Status to Ready for Delivery.")
        FLAGGED_ERRORS.append(
            f"{str(datetime.now())} Record ID: {record_id}, Unable to change order status to Ready for Delivery")
    elif status.get("Current", None):
        status = status.get("Current")
        logging.info(
            f"Current Order Status is {status}, No Change Made to Order Status.")
    else:
        exception_msg = str(status.get("Exception"))
        FLAGGED_ERRORS.append(
            f"{str(datetime.now())} Record ID: {record_id}, {exception_msg}")
        logging.info(
            f"Current Order Status is {status}, No Change Made to Order Status.")

    '''
    after changes our driver location is current order page and
    we are going to back and continue looping
    '''
    back_to_orders(driver)

    # Delete image from upload queue
    delete_from_queue(record_id, order_number, img_name)
    logging.info("Deleting Order Image from Upload Queue.")

    # Finished with Order
    logging.info(f"Finished Processing Order Number {order_number}.")

logging.info("Script Complete!")
if FLAGGED_ERRORS:
    logging.info("Errors Found, Sending log file...")

    msg = 'List of Error logs:'
    errors = ""
    for i, e in enumerate(FLAGGED_ERRORS):
        errors += f"\n{i}) {e}"
    msg = msg + errors
    send_mail(
        subject='Errors found',
        message=msg
    )
driver.quit()
