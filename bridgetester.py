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
            bridgeid = bridge.get('id')
            bridgeid = bridgeid.split('-')[1] # this extracts a readable bridge name from the bridge metadata
            if bridgeid in IGNORED:
                continue
            formid = 1
            formidstring = 'form' + formid
            RESULTS[bridgeid] = {}
            RESULTS[bridgeid][formidstring]['timestamp'] = TIMEOFRUN
            errormessages = []
            bridgestring = '/?action=display&bridge=' + bridgeid + '&format=Json'
            forms = bridge.find_all("form")
            for form in forms:
                formstring = ''
                parameters = form.find_all("input")
                lists = form.find_all("select")
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
                for list in lists:
                    selectionvalue = ''
                    for selectionentry in list.contents:
                        if 'selected' in selectionentry.attrs:
                            selectionvalue = selectionentry.get('value')
                            break
                    if selectionvalue == '':
                        selectionvalue = list.contents[0].get('value')
                    formstring = formstring + '&' + list.get('name') + '=' + selectionvalue
                if not errormessages:
                    getBridge(URL + bridgestring + formstring,bridgeid,formidstring)
                else:
                    RESULTS[bridgeid][formidstring]['missing'] = errormessages
                formid += 1

def getBridge(bridgestring,bridgeid,formidstring):
    start = time.perf_counter()
    page = requests.get(bridgestring)
    page.encoding='utf-8-sig'
    runtime = time.perf_counter() - start
    # some time calculations needed to get the seconds correctly into powerbi
    RESULTS[bridgeid][formidstring]['runtime'] = int(runtime * 1000)
    if page.text != '':
        jsoncontent = page.json()
        RESULTS[bridgeid][formidstring]['items'] = len(jsoncontent['items'])
        if len(jsoncontent['items']) == 0:
            RESULTS[bridgeid][formidstring]['status'] = 'broken'
        elif len(jsoncontent['items']) == 1:
            if jsoncontent['items'][0].get('title'):
                if 'Bridge returned error' in jsoncontent['items'][0]['title']:
                    RESULTS[bridgeid][formidstring]['status'] = 'broken'
                    RESULTS[bridgeid][formidstring]['code'] = jsoncontent['items'][0]['title']
                else:
                    RESULTS[bridgeid][formidstring]['status'] = 'working'
            else:
                RESULTS[bridgeid][formidstring]['status'] = 'working'
        elif len(jsoncontent['items']) > 1 and len(jsoncontent['items']) < 50:
            RESULTS[bridgeid][formidstring]['status'] = 'working'
        elif len(jsoncontent['items']) > 50:
            RESULTS[bridgeid][formidstring]['status'] = 'sizewarning'
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