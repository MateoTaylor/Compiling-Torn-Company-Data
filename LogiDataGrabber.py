#Goal = Pull and sort all 8-10* Logistics companies into a spreadsheet.
# from there, pull all 9-10* company setups and compare.

from TornKey import API_KEY
import requests
import json
import pandas as pd
import pygsheets
from datetime import datetime

def pull_company_info(company_type:int ): # pull all companies of a certain type
    response = requests.get("https://api.torn.com/company/"+ str(company_type) + "?selections=companies&key=" + API_KEY)
    all_companies = json.loads(response.text)
    x8_to_10_companies = []
    for company_info in all_companies['company']:
        if company_info['rating'] == 9: # if this is a 8-10* company, pull its info
            company_setup = find_company_setups(company_info["ID"])
            company_info.update(company_setup) # adding our employee setup to the data
            x8_to_10_companies.append(company_info) # appending it to our larger list

    pandafied = pd.DataFrame(x8_to_10_companies)
    return pandafied


def find_company_setups(company_id:int):
    response = requests.get("https://api.torn.com/company/" + str(company_id) + "?selections=employees&key=" + API_KEY)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    this_company = json.loads(response.text)
    company_positions = {
        "Driller": 0,
        "Roughneck": 0,
        "Derrick Hand": 0,
        "Sales Executive": 0,
        "Motor Hand": 0,
        "Inspector": 0,
        "Secretary": 0,
        "Unassigned": 0,
    }
    for employee_id, employee_info in this_company['company_employees'].items():
        company_positions[employee_info["position"]] += 1
    return company_positions

def access_sheets(): # pull our google sheet
    google_sheets = pygsheets.authorize(service_file='SheetSettingsAPI.json')
    spreadsheet = google_sheets.open('Compiled Logistics Data')
    try:
        worksheet = spreadsheet.worksheet_by_title(datetime.now().strftime("%m/%d/%y"))
    except pygsheets.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(datetime.now().strftime("%m/%d/%y")) # putting today's data into a new sheet
    return worksheet

def upload_to_sheet(sheet:pygsheets.Worksheet, x8_to_10_companies: pd.DataFrame):
    assert type(x8_to_10_companies) == pd.DataFrame
    sheet.set_dataframe(x8_to_10_companies, 'A1')


if __name__ == "__main__":  
    upload_to_sheet(access_sheets(),pull_company_info(28))
    print('done grabbing data')

# Goal: Pull all 8-10* Logistics companies into a spreadsheet.