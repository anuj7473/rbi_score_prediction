import json
import pandas as pd

class ScoreCalculator:
    def __init__(self, row_):
        self.score = 0
        self.row_ = row_
        self.cols = []
    def digital_access_score(self):
        """Caculating score based on 'internetUsage' and monthlyDataExpense"""
        rst = 0
        if self.row_['internetUsage'] == 'yes':
            rst += 4
        monthlyDataExpense_map = {
            '101-200':3,
            '1-100':2,
            "0":-3
        }
        rst = rst + monthlyDataExpense_map[self.row_['monthlyDataExpense'].strip()]
        self.score += rst
        self.cols.append('internetUsage','')
        return rst
    def family_spending_score(self):
        """score based on dependentMembers"""
        maps = {
            '0-2':5,
            '3-5':8,
            '6-8':11
        }
        rst = maps[self.row_['dependentMembers']]
        self.score += rst
        return rst

    def family_dynamics_score(self):
        """Score based on foodFuelExpensePercentage and outStandingLoanEmi"""
        map_ = {
            '<25%':4,
            "25-50%": 2,
            "51-75%": -1,
            ">75%": -2
        }
        self.score += map_[self.row_['foodCookingFuelPercentage']]
        
        outstanding_map = {
            '0': 3,
            '1-500': 2,
            '501-1000': -1
        }
        self.score += outstanding_map[self.row_['outstandingLoansEMI']]
        return map_[self.row_['foodCookingFuelPercentage']] + outstanding_map[self.row_['outstandingLoansEMI']]
    
    def income_dependency_score(self):
        """score based on  dependentMember, earningMember, jobStability"""
        # Map for earningDependentRation
        ratio_map = {
            '1:2': 5,
            '1:4': -3,
        }
        ratio = self.row_.get('earningDependentRation', '').strip()
        rst = ratio_map.get(ratio, 2)
        self.score += rst

        job_type_map = {
            'small business': 5,
            'factory worker': 3,
            'daily wager': -2
        }
        job_score=0
        job_type = self.row_.get('jobType', '').strip()
        for job in job_type:
            job_score = job_type_map.get(job.lower(), 0)
        self.score += job_score
        rst += job_score

        job_stability_map = {
            'permanent': 5,
            'seasonal': 1,
            'irregular': -2
        }
        job_stability = self.row_.get('jobStability', '').strip().lower()
        job_stability_score = job_stability_map.get(job_stability, 0)
        self.score += job_stability_score
        
        return rst
    
    def emergency_fund_access_score(self):
        """Score based on emergencyFundManagement, emergencyInterestRate, and pastEmergencyExperience"""
        # emergencyFundManagement mapping
        fund_management_map = {
            'Savings': 5,
            'Family-friends': 3,
            'moneyLender': -3
        }
        fund_management = self.row_.get('emergencyFundManagement', '').strip()
        fund_management_score = fund_management_map.get(fund_management, 0)
        self.score += fund_management_score

        # emergencyInterestRate mapping
        interest_rate_map = {
            '0%': 3,
            '1-10': 1,
            '20%': -2
        }
        interest_rate = self.row_.get('emergencyInterestRate', '').strip()
        interest_rate_score = interest_rate_map.get(interest_rate, 0)
        self.score += interest_rate_score

        # pastEmergencyExperience mapping
        past_experience_map = {
            'no': 3,
            'yes': -1
        }
        past_experience = self.row_.get('pastEmergencyExperience', '').strip().lower()
        past_experience_score = past_experience_map.get(past_experience, 0)
        self.score += past_experience_score

        return fund_management_score + interest_rate_score + past_experience_score

    def asset_ownership_score(self):
        """
        Calculates asset ownership score (max 13 pts):
        +5 for Land, +5 for Vehicles, +3 for Livestock, +1 for Mobile Phones,
        +3 if motorizedVehicles == 'yes'
        """
        score = 0
        asset_map = {
            'Land': 5,
            'Vehicles': 5,
            'Livestock': 3,
            'Mobile Phones': 1
        }
        # Check each asset
        for asset in self.row_['familyAssets']:
            score += asset_map.get(asset, 0)

        # Check motorizedVehicles
        motorized = self.row_.get('motorizedVehicles', '').strip().lower()
        if motorized == 'yes':
            score += 3

        self.score += score
        return score
    
    def income_frequency_score(self):
        """
        Calculates income frequency score (max 13 pts):
        +13 for monthly, +9 for weekly, +5 for daily
        """
        frequency_map = {
            'monthly': 13,
            'weekly': 9,
            'daily': 5
        }
        income_frequency = self.row_.get('incomeFrequency', '').strip().lower()
        score = frequency_map.get(income_frequency, 0)
        self.score += score
        return score
    
    def financial_behavior_score(self):
        """
        Calculates Financial Behavior score (max 15 pts):
        +4 if secondaryIncome == 'yes'
        monthlySavings (categorical):
            '0' -> -1
            '1-500' -> +2
            '1000+' -> +5
        +3 if governmentSchemeAwareness == 'yes'
        loanDefaultHistory:
            'no' -> +3
            else -> -4
        """
        score = 0

        # secondaryIncome
        secondary_income = self.row_.get('secondaryIncome', '').strip().lower()
        if secondary_income == 'yes':
            score += 4

        # monthlySavings (categorical)
        monthly_savings = self.row_.get('monthlySavings', '').strip()
        savings_map = {
            '0': -1,
            '1-500': 2,
            '1000+': 5
        }
        score += savings_map.get(monthly_savings, 0)

        # governmentSchemeAwareness
        scheme_awareness = self.row_.get('governmentSchemeAwareness', '').strip().lower()
        if scheme_awareness == 'yes':
            score += 3

        # loanDefaultHistory
        loan_default = self.row_.get('loanDefaultHistory', '').strip().lower()
        if loan_default == 'no':
            score += 3
        else:
            score += -4

        self.score += score
        return score

    def lpg_adoption_score(self):
        """
        Calculates LPG Adoption score (max 7 pts):
        +3 if LPG Preference == 'yes'
        LPG Challenges:
            'none' -> +2
            'cost' -> +1
        +2 if Cylinder Preference == '5kg'
        """
        score = 0

        # LPG Preference
        lpg_preference = self.row_.get('lpgPreference', '').strip().lower()
        if lpg_preference == 'yes':
            score += 3

        # LPG Challenges
        lpg_challenges = self.row_.get('lpgChallenges', '').strip().lower()
        if lpg_challenges == 'none':
            score += 2
        elif lpg_challenges == 'cost':
            score += 1

        # Cylinder Preference
        cylinder_preference = self.row_.get('cylinderPreference', '').strip().lower()
        if cylinder_preference == '5kg':
            score += 2

        self.score += score
        return score


    def total_score(self):
        self.score = 0
        self.digital_access_score()
        self.family_spending_score()
        self.family_dynamics_score()
        self.income_dependency_score()
        self.emergency_fund_access_score()
        self.asset_ownership_score()
        self.income_frequency_score()
        self.financial_behavior_score()
        self.lpg_adoption_score()
        return self.score