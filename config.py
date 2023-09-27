import json


def config_browser(headless: bool):
    config_filename = "config"
    if headless == True:
        config_filename = "headless_config"
    with open(f'Resources/{config_filename}.json') as f:
        data = json.load(f)
        f.close()
    if 'browser' not in data:
        raise Exception('The config file does not contain "browser"')
    elif data['browser'] not in ['chrome', 'firefox']:
        raise Exception(f'"{data["browser"]}" is not a supported browser')
    return data


def get_data():
    with open('Resources/data.json') as f:
        data = json.load(f)
        f.close()
    return data
