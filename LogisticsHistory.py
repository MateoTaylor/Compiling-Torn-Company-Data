import requests
import json
import pygsheets
from datetime import datetime
from TornKey import API_KEY


def access_sheets(): # pull our google sheet2
    google_sheets = pygsheets.authorize(service_file='SheetSettingsAPI.json')   
    spreadsheet = google_sheets.open('Torn Comp History Tracker')
    return spreadsheet

def parse_company_info(): # use TORN API to pull company info
    response = requests.get("https://api.torn.com/company/?selections=employees,detailed,profile,stock&key=" + API_KEY)
    this_company = json.loads(response.text) # pull our company data
    # Different parts of request dictionary:
    # employees pulls effectivenesss & wages
    # company_detailed pulls advertising
    # company pulls daily income
    # stock gives us our global price

    # pulling apart our employee effectiveness and wages:
    employees = this_company["company_employees"]
    employee_count = this_company["company"]["employees_hired"]

    employee_wages = 0
    employee_effectiveness = 0
    worst_employee = ["",0]
    positions = {}
    position_effectiveness = {}

    for employee_id,employee in employees.items():
        employee_wages += employee["wage"] # adding to total wages
        employee_effectiveness += employee["effectiveness"]["total"] # adding to total effectiveness

        if employee["position"] in positions:
            positions[employee["position"]] += 1
            position_effectiveness[employee["position"]] += employee["effectiveness"]["total"]
        else:
            positions[employee["position"]] = 1
            position_effectiveness[employee["position"]] = employee["effectiveness"]["total"]

        stat_loss = 0
        if "addiction" in employee["effectiveness"]: # checking if this is our worst employee
            stat_loss += int(employee["effectiveness"]["addiction"])
        if "inactivity" in employee["effectiveness"]:
            stat_loss += int(employee["effectiveness"]["inactivity"])
        if stat_loss < worst_employee[1]:
            worst_employee = [employee["name"],stat_loss]
    return {"advertising": this_company['company_detailed']['advertising_budget']//1000,
            "oil_price": this_company['company_stock']['Oil (Barrel)']['price'],
            "current_stock": this_company['company_stock']['Oil (Barrel)']['in_stock'],
            "oil_sold": this_company['company_stock']['Oil (Barrel)']['sold_amount'],
            "income": this_company['company']['daily_income']//1000,
            "wages": employee_wages//1000,
            "employee_count": employee_count,
            "average_effectiveness": round(employee_effectiveness/employee_count,2),
            "worst_employee": worst_employee, # note this is a list of [name,stat_loss]
            "positions": dict(sorted(
                ((position, {"count": count, "average_effectiveness": round(position_effectiveness[position]/count, 2)})
                 for position, count in positions.items()),
                key = lambda x:x[1]["count"],
                reverse=True
            )) # sorted dictionary of positions & occurences
            }

def format_for_sheet(info:dict): # format TORN API data into a list for our google sheet
    # this function will take our dictionary and format it for our google sheet
    list_to_return = [-info['wages'],-info['advertising'],info['income'],info["income"]-info["wages"]-info["advertising"],""] # first 4 columns are basic comp info

    list_to_return.append(info["oil_price"]) # oil price
    list_to_return.append(info["current_stock"]) # current stock
    list_to_return.append(info["oil_sold"]) # oil sold
    list_to_return.append(info['average_effectiveness'])

    list_to_return.extend(["",str(info['employee_count']) + "/30",info['worst_employee'][0],info['worst_employee'][1]]) # worst employee
    for position_info in info["positions"].values():
        list_to_return.append(position_info["count"])
        list_to_return.append(position_info["average_effectiveness"])
    return list_to_return
     # average effectiveness


def column_index_to_letter(column_index:int):
    letters = ""
    while column_index:
        column_index, remainder = divmod(column_index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters

def update_sheets(sheet:pygsheets.Worksheet, update_list:list): # update a row in our google sheet (based on date)
    # find what row we're adding to, based on date
    column = sheet.get_values(start="A2", end="A800", majdim="COLUMNS") # should pull dates
    target_row = column[0].index(datetime.now().strftime("%m/%d/%y").lstrip("0").replace("/0", "/")) + 2 # +2 because we're starting at A2
    
    start_column = 2
    end_column = start_column + len(update_list) - 1
    sheet.update_values(crange=f"{column_index_to_letter(start_column)}{target_row}:{column_index_to_letter(end_column)}{target_row}", values=[update_list])
    

update_sheets(access_sheets()[0],format_for_sheet(parse_company_info()))
print('Cake & Co update done!')