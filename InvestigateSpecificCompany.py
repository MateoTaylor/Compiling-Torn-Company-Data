from TornKey import API_KEY
import requests
import json

def pull_company_employees(company_id:int ): # pull all companies of a certain type
    response = requests.get("https://api.torn.com/company/" + str(company_id) + "?selections=employees&key=" + API_KEY)
    this_company = json.loads(response.text)
    results = []
    averagestats = 0
    for employee_id, employee_info in this_company['company_employees'].items():
        pull_employee = requests.get("https://api.torn.com/v2/user/" + str(employee_id) + "/hof?key=" + API_KEY)
        this_employee = json.loads(pull_employee.text)
        results.append([employee_info["name"],employee_info["position"],this_employee["hof"]["working_stats"]["value"]])
        averagestats += this_employee["hof"]["working_stats"]["value"]
    for emp in results:
        print(emp)
    print(str(averagestats/len(results)) + "\n")
    # can also return if these if that's more convenient
        
def parse_company_info(): # use TORN API to pull company info
    response = requests.get("https://api.torn.com/company/?selections=detailed,profile,stock&key=" + API_KEY)
    this_company = json.loads(response.text) # pull our company data
    print(this_company)


if __name__ == "__main__":
    #pull_company_employees(93310)
    # pull_company_employees(98543)
    # parse_company_info()
    pull_company_employees(97966)

    # pull_company_employees(97966)
    # pull_company_employees(90452)

    #top 10* 15 man
    '''
    pull_company_employees(90590) # 421233.73333333334
    pull_company_employees(83046) #451520.4666666667
    pull_company_employees(96283) #360026.6666666667
    pull_company_employees(82142) #308348.93333333335
    pull_company_employees(99658) #200933.4
    pull_company_employees(90797) #461415.5333333333
    pull_company_employees(98543) #214109.16666666666 pusheen
    pull_company_employees(103610) #203855.0 pusheen2.0
    
    pull_company_employees(94698) #295690.06666666665
    pull_company_employees(83665) #385747.6666666667
    '''
    print('done grabbing data')