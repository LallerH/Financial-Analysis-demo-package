import pandas as pd

class FinancialYear:

    def __init__(self, data):
        '''
        Arguments:
            data: dictionary from pandas.core.series.Series (row of financial year from pandas object)
        '''
        self.year = data['date'][0:4]
        self.dom_sales = round(int(data['domestic_sales']))
        self.ext_sales = round(int(data['external_sales']))
        self.chg_semi_finished = round(int(data['chg_in_semi_finished_goods']))
        self.own_work_cap = round(int(data['own_work_capitalized']))
        self.other_inc = round(int(data['other_income']))
        self.raw_material_cost = round(int(data['cost_raw_materials']))
        self.services = round(int(data['cost_services']))
        self.other_services = round(int(data['other_services']))
        self.cogs = round(int(data['cogs']))
        self.coss = round(int(data['coss']))
        self.wages = round(int(data['wages']))
        self.benefits = round(int(data['other_benefits']))
        self.contributions = round(int(data['contributions']))
        self.depreciation = round(int(data['depreciation']))
        self.other_exp = round(int(data['other_expenses']))
        self.raw_materials = round(int(data['raw_materials']))
        self.semi_fin_goods = round(int(data['semi_finished_goods']))
        self.animals = round(int(data['animals']))
        self.fin_goods = round(int(data['finished_goods']))
        self.goods = round(int(data['goods']))
        #self.advances_piad = round(int(data['advances_inv']))

        self.net_sales = self.dom_sales + self.ext_sales
        self.own_performance_cap = self.own_work_cap + self.chg_semi_finished
        self.production_value = self.net_sales + self.own_performance_cap
        self.material_costs = self.raw_material_cost + self.services + self.other_services + self.cogs + self.coss
        self.staff_costs = self.wages + self.benefits + self.contributions
        self.ebitda = self.net_sales + self.own_performance_cap - self.material_costs - self.staff_costs + self.other_inc - self.other_exp
        self.op_profit = self.ebitda - self.depreciation

    def cost_ratios(self, ratio = None):
        '''
        Argument:
        ratio =
            - raw_material_cost (str)
            - 
        
        Returns:
        -> cost ratio 
        -> False if not in possible_ratios list
        '''
        possible_ratios = ('raw_material_cost',)
        
        if not ratio:
            print('No arguments for "ratios" method!')
        else:
            if ratio not in possible_ratios:
                print(f'Not defined cost ratio: {ratio}. Defined ratios: {possible_ratios}')
                return False
        if ratio == 'raw_material_cost':
            return self.raw_material_cost / self.production_value
           
    def dscr(self):
        pass

def get_findata_from_csv(year: str, status: str):
    '''
    Gets financial year data from csv from DIR-> .data\financials.csv
    Arguments:
        year: financial year (YYYY)
        status: draft/closed (HUN: főkönyv / lezárt)
    Returns:
        financial_data (class) of financial year
        False if no Data
    '''
    import os
    database = pd.read_csv((fr'{str(os.getcwd())}\data\financials.csv'), sep=";", encoding='latin-1')
    found = False
    for idx_actyear in range (0, len(database)):
        if database.date[idx_actyear][0:4] == year and str(database.status[idx_actyear]) == status:
            found = True
            row = database.iloc[idx_actyear]
            required_year = FinancialYear(row.to_dict())
            return required_year
    if not found:
        print(f'Error: Financial data ({year} / {status}) not found!')
        return False
    

if __name__ == '__main__':
    actual_year = get_findata_from_csv('2021','closed')
    if actual_year:
        print(f'Financial year: {actual_year.year}')
        print(f'Production value: {actual_year.production_value}')
        print(f'EBITDA: {actual_year.ebitda}')
        print(f'Operating profit: {actual_year.op_profit}\n\n*****************\n')
        print(f'Material cost ratio: {actual_year.cost_ratios(ratio = "raw_material_cost")}')
    else:
        print(actual_year)