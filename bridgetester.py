import requests
from bs4 import BeautifulSoup
import random
import json
import time
import pandas as pd
import os.path


def getParameters(bridges):
    for bridge in bridges:
        if bridge.get('data-ref'):
            if bridge.get('data-ref') in IGNORED:
                continue
            RESULTS[bridge.get('data-ref')] = {}
            RESULTS[bridge.get('data-ref')]['timestamp'] = TIMEOFRUN
            errormessages = []
            bridgestring = '/?action=display&bridge=' + bridge.get('data-ref') + '&format=Json'
            forms = bridge.find_all("form")
            formstrings = []
            for form in forms:
                formstring = ''
                parameters = form.find_all("input")
                for parameter in parameters:
                    if parameter.get('type') == 'number' or parameter.get('type') == 'text':
                        if parameter.has_attr('required'):
                            if parameter.get('placeholder') == '':
                                if parameter.get('value') == '':
                                    errormessages.append(parameter.get('name'))
                                else:
                                    formstring = formstring + '&' + parameter.get('name') + '=' + parameter.get('value')
                            else:
                                formstring = formstring + '&' + parameter.get('name') + '=' + parameter.get('placeholder')
                    if parameter.get('type') == 'checkbox':
                        if parameter.has_attr('checked'):
                            formstring = formstring + '&' + parameter.get('name') + '=on'
                formstrings.append(formstring)
            if not errormessages:
                getBridge(URL + bridgestring + random.choice(formstrings),bridge.get('data-ref'))
            else:
                RESULTS[bridge.get('data-ref')]['missing'] = errormessages

def getBridge(bridgestring,bridgeref):
    start = time.perf_counter()
    page = requests.get(bridgestring)
    page.encoding='utf-8-sig'
    runtime = time.perf_counter() - start
    # some time calculations needed to get the seconds correctly into powerbi
    RESULTS[bridgeref]['runtime'] = int(runtime * 100)
    if page.text != '':
        jsoncontent = page.json()
        RESULTS[bridgeref]['items'] = len(jsoncontent['items'])
        if len(jsoncontent['items']) == 0:
            RESULTS[bridgeref]['status'] = 'broken'
        elif len(jsoncontent['items']) == 1:
            if jsoncontent['items'][0].get('title'):
                if 'Bridge returned error' in jsoncontent['items'][0]['title']:
                    RESULTS[bridgeref]['status'] = 'broken'
                    RESULTS[bridgeref]['code'] = jsoncontent['items'][0]['title']
                else:
                    RESULTS[bridgeref]['status'] = 'working'
            else:
                RESULTS[bridgeref]['status'] = 'working'
        elif len(jsoncontent['items']) > 1 and len(jsoncontent['items']) < 50:
            RESULTS[bridgeref]['status'] = 'working'
        elif len(jsoncontent['items']) > 50:
            RESULTS[bridgeref]['status'] = 'sizewarning'
    #else:
    #    ERRORMESSAGES.append(bridgestring + ' returns no page')


URL = "http://localhost:3000"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

bridges = soup.find_all("section")
RESULTS = {}
TIMEOFRUN = int(time.time())
IGNORED = ['Tester', 'AnimeUltime', 'Demo', 'WeLiveSecurity', 'PresidenciaPT', 'Shanaproject', 'Flickr', 'Wired', 'Facebook', 'FB2', 'Portuguesa', 'Q Play', 'Filter']
getParameters(bridges)
if not os.path.isfile('stats.csv'):
    pd.DataFrame(RESULTS).T.to_csv('stats.csv')
else:
    pd.DataFrame(RESULTS).T.to_csv('stats.csv', mode='a', header=False)