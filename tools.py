from datetime import datetime
from os import walk, remove
import requests
from bs4 import BeautifulSoup
import re
import os
import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail, To
from dotenv import load_dotenv


def delete_logs():
    date_format = "%Y-%m-%d"
    today = datetime.today().date()

    # getting filenames from logs directory
    filenames = next(walk("logs/"), (None, None, []))[2]

    for filename in filenames:

        # cleaning filename getting only date
        file_datestr = filename.replace(".log", "")
        # Delete any log files older than 7 days.
        file_date = datetime.strptime(file_datestr, date_format).date()
        delta = (today - file_date).days
        if delta > 7:
            remove(f'logs/{filename}')


def scrap_images() -> BeautifulSoup:
    try:
        response = requests.get(
            "https://khloris.bloomnwa.com/iut/floranext_queue.php")
        soup = BeautifulSoup(response.text, 'html.parser')  # parsing html
        records = soup.find_all("tr")
        if len(records) == 1 and records[0].td.text == ' No Records Found':
            records = None

    except Exception as e:
        return {"Exception": e}
    # if record founds returning records  if not found returning none to end script
    if records:
        return {"Records": records}
    return None


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def clean_record(r: str) -> dict:
    '''
    r string looks like this and we need to clean this and save date inside dict
    <td>Order Number: 100046565<br/>Designer: Jennifer T<br/>Record ID: 221<br/>
    Image Location: https://khloris.bloomnwa.com/iut/OrderImage/1/100046565/16512492740025586470913094876994.jpg</td>
    '''
    # removing td tags from start and form end, also removing br tags
    items = r[4:][:-5].split("<br/>")
    record = {}
    for item in items:
        k, v = item.split(": ")
        record[k] = v
    return record


def get_cretendtials():
    with open("./credentials.txt") as f:
        text = f.read()
        email, pswd = text.split(":")
        f.close()
    return email, pswd


def save_image(url):
    img_data = requests.get(url).content
    # ex: https://khloris.bloomnwa.com/iut/OrderImage/1/100049552/16529657061607462732434894867644.jpg
    # getting only name from the img url = 16529657061607462732434894867644.jpg
    # and saving
    img_name = url.split("/")[-1]
    with open(img_name, "wb") as handler:
        handler.write(img_data)
        handler.close()


def delete_image(img_name):
    if os.path.exists(img_name):
        os.remove(img_name)
    else:
        print("The file does not exist")


def delete_from_queue(record_id, order_number, img_name):
    api_url = f'https://khloris.bloomnwa.com/iut/floranext_delete_order.php?RecordID={record_id}&OrderNumber={order_number}&Image={img_name}'
    requests.get(api_url)


def send_error_message(record_id, error):
    api_url = f'https://khloris.bloomnwa.com/iut/floranext_update_order.php?OrderID={record_id}&Error={error}'
    requests.get(api_url)


def send_mail(subject, message):
    '''
    By default load_dotenv will look for the .env file
    in the current working directory or any parent directories
    however you can also specify the path if your particular use case requires
    it be stored elsewhere.
    '''
    load_dotenv(".env")
    temail = os.getenv("TO_EMAIL")
    apikey = os.getenv("SENDGRID_API_KEY")
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    smtpserver = os.getenv("SMTP_SERVER")
    port = os.getenv("PORT")
    sg = sendgrid.SendGridAPIClient(api_key=apikey)
    from_email = Email(email)
    to_email = To(temail)
    content = Content("text/plain", message)
    mail = Mail(from_email, to_email, subject, content)
    # Send an HTTP POST request to /mail/send
    sg.send(mail)


def drag_and_drop_file(drop_target, path):
    JS_DROP_FILE = """
        var target = arguments[0],
            offsetX = arguments[1],
            offsetY = arguments[2],
            document = target.ownerDocument || document,
            window = document.defaultView || window;

        var input = document.createElement('INPUT');
        input.type = 'file';
        input.onchange = function () {
        var rect = target.getBoundingClientRect(),
            x = rect.left + (offsetX || (rect.width >> 1)),
            y = rect.top + (offsetY || (rect.height >> 1)),
            dataTransfer = { files: this.files };

        ['dragenter', 'dragover', 'drop'].forEach(function (name) {
            var evt = document.createEvent('MouseEvent');
            evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
            evt.dataTransfer = dataTransfer;
            target.dispatchEvent(evt);
        });

        setTimeout(function () { document.body.removeChild(input); }, 25);
        };
        document.body.appendChild(input);
        return input;
    """
    driver = drop_target.parent
    file_input = driver.execute_script(JS_DROP_FILE, drop_target, 0, 0)
    file_input.send_keys(path)
