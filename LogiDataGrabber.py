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
    for company_id, company_info in all_companies['company'].items():
        if company_info['rating'] >= 8:
            company_setup = find_company_setups(company_info["ID"])
            company_info.update(company_setup) # adding our employee setup to the data
            x8_to_10_companies.append(company_info) # appending it to our larger list

    pandafied = pd.DataFrame(x8_to_10_companies)
    return pandafied


def find_company_setups(company_id:int):
    response = requests.get("https://api.torn.com/company/" + str(company_id) + "?selections=employees&key=" + API_KEY)
    this_company = json.loads(response.text)
    company_positions = {
        "Lumper": 0,
        "Driver": 0,
        "Forklift Operator": 0,
        "Transport Coordinator": 0,
        "Warehouse Manager": 0,
        "Shift Manager": 0,
        "Supply Chain Manager": 0,
        "Procurement Manager": 0
    }
    for employee_id, employee_info in this_company['company_employees'].items():
        company_positions[employee_info["position"]] += 1
    return company_positions

def access_sheets(): # pull our google sheet
    google_sheets = pygsheets.authorize(service_file='SheetSettingsAPI.json')
    spreadsheet = google_sheets.open('Compiled Logistics Data')
    spreadsheet.add_worksheet(datetime.now().strftime("%m/%d/%y")) # putting today's data into a new sheet
    return spreadsheet.worksheet_by_title(datetime.now().strftime("%m/%d/%y"))

def upload_to_sheet(sheet:pygsheets.Worksheet, x8_to_10_companies: pd.DataFrame):
    assert type(x8_to_10_companies) == pd.DataFrame
    sheet.set_dataframe(x8_to_10_companies, 'A1')


if __name__ == "__main__":  
    upload_to_sheet(access_sheets(),pull_company_info(40))

# Goal: Pull all 8-10* Logistics companies into a spreadsheet.
