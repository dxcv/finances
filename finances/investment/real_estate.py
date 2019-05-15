import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



class HouseInvestment():
    n_years = 0
    value_rate = 0
    house_price = 0
    interest_rate = 0.02
    initial_investment = 10000
    initial_costs = [0]
    yearly_costs = [0]

    def __init__(self,
        n_years = 0,
        value_rate = 0,
        house_price = 0,
        interest_rate = 0.02,
        initial_investment = 10000,
        initial_costs = [0],
        yearly_costs = [0]
    ):
        self.n_years = n_years
        self.value_rate = value_rate
        self.house_price = house_price
        self.interest_rate = interest_rate
        self.initial_investment = initial_investment
        self.initial_costs = initial_costs
        self.yearly_costs = yearly_costs
        self.loan = self.house_price-self.initial_investment+np.sum(self.initial_costs)


    def value_house(self):
        return self.house_price*(1+self.value_rate)**self.n_years


    def total_pay_to_bank(self):
        pay_to_bank = self.loan*(1+self.interest_rate)**self.n_years
        return pay_to_bank


    def monthly_payment(self):
        monthly_to_bank = self.total_pay_to_bank()/self.n_years/12.0

        return np.sum(self.yearly_costs)/12.0 + monthly_to_bank


    def house_investment_gain(self):
        pay_to_bank = self.total_pay_to_bank()
        total_yearly_costs = np.sum(self.yearly_costs)*self.n_years
        total_paid = pay_to_bank+total_yearly_costs+self.initial_investment
        
        house_value = self.house_price*(1+self.value_rate)**self.n_years
        total_investment_return = house_value-total_paid
        
        return total_investment_return


class RentHouse():

    def __init__(self,
        n_years,
        initial_investment,
        invest_return,
        rent,
        monthly_io,
        yearly_rent_increase
        ):
        self.n_years = n_years
        self.initial_investment = initial_investment
        self.invest_return = invest_return  # annual
        self.rent = rent
        self.monthly_io = monthly_io
        self.yearly_rent_increase = yearly_rent_increase


    def return_on_investment(self):
        month_input = self.monthly_io
        if month_input<0:
            print('Negative monthly io')
        value_investment = self.initial_investment
        monthly_return = (1+self.invest_return)**(1/12.0)-1.0
        for k in range(self.n_years):
            month_input-=self.yearly_rent_increase
            for month in range(12):
                value_investment*=(1+monthly_return)
                value_investment+=month_input
        return value_investment


if __name__=='__main__':

    n_years = 20
    initial_investment = 10000

    buy_house = HouseInvestment(
        n_years = n_years,
        value_rate = 0.05,
        house_price = 200000,
        interest_rate = 0.015,
        initial_investment = initial_investment,
        initial_costs = [20000, 2000],
        yearly_costs = [1000]
    )

    print(buy_house.monthly_payment())

    rent = RentHouse(
        n_years=n_years,
        initial_investment=initial_investment,
        invest_return=0.05,
        rent=775,
        monthly_io=buy_house.monthly_payment()-775,
        yearly_rent_increase=0.05
        )

    return_house = buy_house.house_investment_gain()
    return_rent = rent.return_on_investment()

    print(return_house)
    print(return_rent)
    print(return_house-return_rent)
