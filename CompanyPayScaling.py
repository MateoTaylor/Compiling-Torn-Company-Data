import requests
import json
import pygsheets
from datetime import datetime
from TornKey import API_KEY
import pandas as pd

def access_sheets(): # pull our google sheet2
    google_sheets = pygsheets.authorize(service_file='SheetSettingsAPI.json')   
    spreadsheet = google_sheets.open('Torn Comp History Tracker')
    return spreadsheet

def overall_pay_per_effectiveness():
    response = requests.get("https://api.torn.com/company/?selections=employees,detailed,profile,stock&key=" + API_KEY)
    this_company = json.loads(response.text) # pull our company data
    # Different parts of request dictionary:
    # employees pulls effectivenesss & wages
    # company_detailed pulls advertising
    # company pulls daily income

    primary_stats = {
        'Secretary': 112500,
        'Sales Executive': 131500,
        'Roughneck': 75000,
        'Driller': 150000,
        'Motor Hand': 112500,
        'Derrick Hand': 94000,
        'Unassigned': 1000,
    }

    # stock gives us our global price
    output = pd.DataFrame(columns=["Name","Position","Wage","Effectiveness","Pay per Effectiveness"])

    # pulling apart our employee effectiveness and wages:
    employees = this_company["company_employees"]
    employee_count = this_company["company"]["employees_hired"]
    for employee_id,employee in employees.items():
        wage = employee["wage"]
        effectiveness = employee["effectiveness"]["working_stats"]
        merits = employee["effectiveness"]["merits"] if "merits" in employee["effectiveness"] else 0

        std_wage = 20 * primary_stats[employee["position"]]
        std_pay_per_effectiveness = std_wage / 100
        pay_per_effectiveness = wage/effectiveness if effectiveness > 0 else 0
        overpayment_ratio = pay_per_effectiveness / std_pay_per_effectiveness

        
        output = pd.concat([output,pd.DataFrame({"Name":[employee["name"]],
                                                "Position":[employee["position"]],
                                                "Wage":[wage],
                                                "Effectiveness":[effectiveness + merits],
                                                "Merits":[merits],
                                                "Overpayment Ratio":[overpayment_ratio],
                                                "Pay per Effectiveness":[pay_per_effectiveness],
                                                "Std Pay per Effectiveness":[std_pay_per_effectiveness],
                                                "Primary State Req":[primary_stats[employee["position"]]],
                                                "Standard Wage":[std_wage]

        })],ignore_index=True)

        
    output = output.sort_values(by="Position",ascending=False)
    return output

def update_sheets(sheet:pygsheets.Worksheet, output:pd.DataFrame): # add datafram toe our google sheet
    # just add pd
    sheet.set_dataframe(output, 'A1')

if __name__ == "__main__":
    spreadsheet = access_sheets()
    update_sheets(spreadsheet[1], overall_pay_per_effectiveness())