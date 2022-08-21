import requests
from bs4 import BeautifulSoup
import math
import time
import pandas as pd
import os.path
from datetime import datetime
import itertools


def getParameters(bridges):
    for bridge in bridges:
        if bridge.get('data-ref'): # Some div entries are empty, this ignores those
            bridgeid = bridge.get('id')
            bridgeid = bridgeid.split('-')[1] # this extracts a readable bridge name from the bridge metadata
            if bridgeid in IGNORED:
                continue
            bridgestring = '/?action=display&bridge=' + bridgeid + '&format=json'
            forms = bridge.find_all("form")
            formid = 1
            for form in forms:
                # a bridge can have multiple contexts, named 'forms' in html
                # this code will produce a fully working formstring that should create a working feed when called
                # this will create an example feed for every single context, to test them all
                formstring = ''
                errormessages = []
                parameters = form.find_all("input")
                lists = form.find_all("select")
                # this for/if mess cycles through all available input parameters, checks if it required, then pulls
                # the default or examplevalue and then combines it all together into the formstring
                # if an example or default value is missing for a required attribute, it will throw an error
                # any non-required fields are not tested!!!
                for parameter in parameters:
                    if parameter.get('type') == 'hidden' and parameter.get('name') == 'context':
                        cleanvalue = parameter.get('value').replace(" ","+")
                        formstring = formstring + '&' + parameter.get('name') + '=' + cleanvalue
                    if parameter.get('type') == 'number' or parameter.get('type') == 'text':
                        if parameter.has_attr('required'):
                            if parameter.get('placeholder') == '':
                                if parameter.get('value') == '':
                                    errormessages.append(parameter.get('name'))
                                else:
                                    formstring = formstring + '&' + parameter.get('name') + '=' + parameter.get('value')
                            else:
                                formstring = formstring + '&' + parameter.get('name') + '=' + parameter.get('placeholder')
                    # same thing, just for checkboxes. If a checkbox is checked per default, it gets added to the formstring
                    if parameter.get('type') == 'checkbox':
                        if parameter.has_attr('checked'):
                            formstring = formstring + '&' + parameter.get('name') + '=on'
                for listing in lists:
                    selectionvalue = ''
                    listname = listing.get('name')
                    if 'optgroup' in listing.contents[0].name:
                        listing = list(itertools.chain.from_iterable(listing))
                    firstselectionentry = 1
                    for selectionentry in listing:
                        if firstselectionentry:
                            selectionvalue = selectionentry.get('value')
                            firstselectionentry = 0
                        else:
                            if 'selected' in selectionentry.attrs:
                                selectionvalue = selectionentry.get('value')
                                break
                    formstring = formstring + '&' + listname + '=' + selectionvalue
                if not errormessages:
                    getBridge(URL + bridgestring + formstring,bridgeid,formid)
                formid += 1

def getBridge(bridgestring,bridgeid,formid):
    start = time.perf_counter()
    page = requests.get(bridgestring)
    page.encoding='utf-8-sig'
    runtime = math.ceil(time.perf_counter() - start)
    if page.text != '':
        jsoncontent = page.json()
        code = ''
        items = len(jsoncontent['items'])
        if len(jsoncontent['items']) == 0:
            status = 'broken'
        elif len(jsoncontent['items']) == 1:
            if jsoncontent['items'][0].get('title'):
                if 'Bridge returned error' in jsoncontent['items'][0]['title']:
                    status = 'broken'
                    code = jsoncontent['items'][0]['title']
                else:
                    status = 'broken'
            else:
                status = 'working'
        elif len(jsoncontent['items']) > 1 and len(jsoncontent['items']) < 50:
            status = 'working'
        elif len(jsoncontent['items']) > 50:
            status = 'sizewarning'
    logentry = ('time="' + TIMEOFRUN
                + '" bridge="' + bridgeid 
                + '" formid="' + str(formid) 
                + '" duration="' + str(runtime)
                + '" items="' + str(items)
                + '" status="' + status
                + '" code="' + code
                + '"')
    with open(os.getcwd() + '/run.log', 'a+') as file:
        file.write("\n")
        file.write(logentry)
    

URL = "http://localhost:3000"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

bridges = soup.find_all("section")
TIMEOFRUN = time.strftime("%d %b %Y %H:%M:%S")
IGNORED = ['Tester', 'AnimeUltime', 'Demo', 'WeLiveSecurity', 'PresidenciaPT', 'Shanaproject', 'Flickr', 'Wired', 'Facebook', 'FB2', 'Portuguesa', 'Q Play', 'Filter']
getParameters(bridges)