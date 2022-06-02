from tools import delete_from_queue, delete_image, delete_logs, save_image, scrap_images, clean_record, send_error_message, send_mail
from bot import access_floranext, authorization, back_to_orders, change_status, check_product_photo, find_order, check_deliverydate, select_designer, upload_image
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
# changed file mode in line 17 'w' to 'a' if w it will clear a log 'a' will open and continue writing

logging.info('Script Started')

delete_logs()
logging.info('Old Log Files Deleted')

logging.info('Accessing Image Upload Queue on KHLORIS.')
records = scrap_images()

# if 0 records found
if records is None:
    logging.error("0 records found")
    sys.exit(1)
elif records.get("Exception", None):
    logging.error(
        'Unable to Access Image Upload Queue on KHLORIS')
    send_mail(
        subject="Image Queque Error",
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
driver = access_floranext()
if driver.get("Exception", None):
    exception_msg = str(driver.get("Exception"))
    logging.error(
        'Unable to Access Floranext.'
    )
    send_mail(
        subject='Unable to Access Floranext.',
        message=exception_msg)
    sys.exit(1)
else:
    driver = driver.get("Driver")


# Login to Floranext Admin
authrz_status = authorization(driver)

if authrz_status.get("Exception", None):
    exception_msg = str(authrz_status.get("Exception"))
    logging.error(
        "Unable to Login to Floranext."
    )
    send_mail(
        subject='Unable to Login to Floranext.',
        message=exception_msg)
    sys.exit(1)
else:
    authrz_status = authrz_status.get("Sucessfully")


for record in data:
    order_number = record.get('Order Number', None)
    designer = record.get('Designer', None)
    record_id = record.get('Record ID', None)
    image_location = record.get('Image Location', None)

    if order_number is None:
        logging.error(
            "Record have not Order Number. Skipping processing."
        )
        continue
    if designer is None:
        logging.error(
            "Record have not Designer. Skipping processing."
        )
        continue
    if record_id is None:
        logging.error(
            "Record have not Record ID. Skipping processing."
        )
        continue
    if image_location is None:
        logging.error(
            "Record have not Image Location. Skipping."
        )
        continue
    logging.info(
        f'Processing Order Number {order_number}.')

    # STEP: In Search Orders field Type Order Number for current record and press Enter.
    find_status = find_order(driver, order_number)
    # If no record found, sending email, and sending api error message
    if find_status.get("Exception", None):
        exception_msg = str(find_status.get("Exception"))

        send_mail(
            subject=f'Image Upload Error / Order: {order_number}',
            message=f'''Image upload tool could not process order {order_number} because the
            order number is not valid in Floranext.
            '''
        )
        send_error_message(record_id, "Invalid Order Number")

        logging.error(
            "Order not found. Skipping order."
        )
        continue
    else:
        find_status = find_status.get("Sucessfully")

    # Once the Order loads check the delivery date
    check_del_status = check_deliverydate(driver)
    # If Delivery Date is in the past or some error occurs
    if check_del_status.get("Error", None):
        send_mail(
            subject=f'Image Upload Error / Order: {order_number}',
            message=f'''Image upload tool could not process order {order_number}
            because thedelivery date in floranext is in the past. Check that the order number is correct.
            '''
        )
        send_error_message(
            record_id, "Delivery date not current. Skipping order.")
        logging.error(
            "Delivery date not current. Skipping order."
        )
        continue
    elif check_del_status.get("Exception", None):
        exception_msg = str(check_del_status.get("Exception"))
        send_mail(
            subject=f'Image Upload Error / Order: {order_number}',
            message=f'''Image upload tool could not process order {order_number}
            because thedelivery date in floranext is in the past. Check that the order number is correct.
            '''
        )
        send_error_message(
            record_id, "Delivery date not current. Skipping order.")
        logging.error(
            "Delivery date not current. Skipping order."
        )
        continue
    else:
        check_del_status = check_del_status.get("Sucessfully")

    '''In the Product Photo Section, Delete any existing image which may be attached to the
    image by clicking the red X (if applicable).
    '''
    checked = check_product_photo(driver)
    if checked == "Deleted":
        logging.info("Deleted existing image.")
    elif checked == "Noexist":
        logging.info("No existing image")
    else:
        exception_msg = str(checked.get("Exception"))
        logging.error(f"We got an error {exception_msg}")
        send_error_message(record_id, "Deleting Existing image failed")
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
        logging.info("Image successfully uploaded")
    elif uploaded == "Error":
        logging.error("Unable to upload image. Skipping order.")
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
            f"Current order status is {current}, status changed to {changed}.")
    elif status == "Error":
        logging.error(f"Unable to change order status to Ready for Delivery.")
        FLAGGED_ERRORS.append(
            f"{str(datetime.now())} Record ID: {record_id}, Unable to change order status to Ready for Delivery")
    elif status.get("Current", None):
        status = status.get("Current")
        logging.info(
            f"Currend order status is {status}, no change made to order status.")
    else:
        exception_msg = str(status.get("Exception"))
        FLAGGED_ERRORS.append(
            f"{str(datetime.now())} Record ID: {record_id}, {exception_msg}")
        logging.info(
            f"Currend order status is {status}, no change made to order status.")

    '''
    after changes our driver location is current order page and
    we are going to back and continue looping
    '''
    back_to_orders(driver)

    # Delete image from upload queue
    delete_from_queue(record_id, order_number, img_name)
    logging.info("Deleting image from Upload Queue.")

    # Finished with Order
    logging.info(f"Finished processing Order Number {order_number}")

logging.info("Script Complete")
if FLAGGED_ERRORS:
    logging.info("Errors Found, Sending log file..")

    msg = 'List of Error logs:'
    errors = ""
    for i, e in enumerate(FLAGGED_ERRORS):
        errors += f"\n{i}) {e}"
    msg = msg + errors
    send_mail(
        subject='Errors found',
        message=msg
    )

driver.close()
