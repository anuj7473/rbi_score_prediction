import json
import pandas as pd

class ScoreCalculator:
    def __init__(self, row_):
        self.score = 0
        self.row_ = row_
        self.cols = []
    
    def _get_scalar_value(self, key, default=None):
        """Helper method to safely get scalar values from row data. Only 'assetsOwned' can be a list; all other fields are always scalar."""
        try:
            value = self.row_[key]
            # Only assetsOwned should ever be a list
            if key == 'assetsOwned':
                if isinstance(value, list):
                    return value
                elif value is None or value == '':
                    return []
                else:
                    return [value]
            # For all other fields, always return a scalar
            if isinstance(value, list):
                if len(value) == 0:
                    return default
                else:
                    return value[0]
            # Handle pandas Series
            if hasattr(value, 'iloc'):
                if len(value) == 0:
                    return default
                elif len(value) == 1:
                    return value.iloc[0]
                else:
                    return value.iloc[0]
            # Handle numpy arrays
            if hasattr(value, 'size'):
                if value.size == 0:
                    return default
                elif value.size == 1:
                    return value.item()
                else:
                    return value.item() if value.size > 0 else default
            return value
        except (KeyError, IndexError, AttributeError):
            return default
    
    def _is_na(self, value):
        """Helper method to safely check if a value is NA"""
        try:
            # Handle regular Python lists
            if isinstance(value, list):
                if len(value) == 0:
                    return True
                # Check if all elements in the list are NA
                return all(pd.isna(item) for item in value)
            
            # Handle pandas Series and numpy arrays
            if hasattr(value, 'iloc'):
                if len(value) == 0:
                    return True
                value = value.iloc[0]
            elif hasattr(value, 'size'):
                if value.size == 0:
                    return True
                value = value.item()
            
            return pd.isna(value)
        except:
            return True
    
    def digital_access_score(self):
        """Caculating score based on 'internetUsage' and monthlyDataExpense"""
        rst = 0
        
        # Handle null values for internetUsed
        internet_used = self._get_scalar_value('internetUsed')
        if self._is_na(internet_used):
            internet_used = 'no'  # Default to no
        else:
            internet_used = str(internet_used).strip().lower()
        
        if internet_used == 'yes':
            rst += 4
        
        monthlyDataExpense_map = {
            '₹101-₹200':2,
            'More than ₹200':3,
            "₹0-₹100":-3
        }
        
        # Handle null values and ensure string type
        data_expense = self._get_scalar_value('dataPackExpense')
        if self._is_na(data_expense):
            # Default to lowest category for null values
            data_expense = "₹0-₹100"
        else:
            data_expense = str(data_expense).strip()
        
        rst = rst + monthlyDataExpense_map.get(data_expense, -3)  # Default to -3 if not found
        self.score += rst
        self.cols.append('internetUsed')
        return rst
    
    def family_spending_score(self):
        """score based on dependentMembers"""
        maps = {
            '0-2':5,
            '3-5':8,
            '6-8':11
        }
        
        # Handle null values and ensure string type
        dependent_members = self._get_scalar_value('dependentMembers')
        if self._is_na(dependent_members):
            # Default to lowest category for null values
            dependent_members = '0-2'
        else:
            dependent_members = str(dependent_members).strip()
        
        rst = maps.get(dependent_members, 5)  # Default to 5 if not found
        self.score += rst
        return rst

    def family_dynamics_score(self):
        """Score based on foodFuelExpensePercentage and outStandingLoanEmi"""
        map_ = {
            'Less than 25%':4,
            "25-50%": 2,
            "51-75%": -1,
            "More than 75%": -2
        }
        
        # Handle null values for foodCookingFuelPercentage
        food_percentage = self._get_scalar_value('foodFuelExpensePercent')
        if self._is_na(food_percentage):
            food_percentage = 'Less than 25%'  # Default to best category
        else:
            food_percentage = str(food_percentage).strip()
        
        food_score = map_.get(food_percentage, 4)  # Default to 4 if not found
        self.score += food_score
        
        outstanding_map = {
            '0': 3,
            '1-500': 2,
            '501-1000': -1
        }
        
        # Handle null values for outstandingLoansEMI
        try:
            outstanding_emi = self._get_scalar_value('outstandingLoansEMI')
        except:
            outstanding_emi = 0
        if self._is_na(outstanding_emi):
            outstanding_emi = '0'  # Default to best category
        else:
            outstanding_emi = str(outstanding_emi).strip()
        
        emi_score = outstanding_map.get(outstanding_emi, 3)  # Default to 3 if not found
        self.score += emi_score
        
        return food_score + emi_score
    
    def income_dependency_score(self):
        """score based on  dependentMember, earningMember, jobStability"""
        # Map for earningDependentRation
        ratio_map = {
            '1:2': 5,
            '1:4': -3,
        }
        
        # Handle null values for earningDependentRation
        ratio = self._get_scalar_value('earningDependentRation', '')
        if self._is_na(ratio):
            ratio = '1:2'  # Default to best category
        else:
            ratio = str(ratio).strip()
        
        rst = ratio_map.get(ratio, 2)
        self.score += rst

        job_type_map = {
            'small business': 5,
            'factory worker': 3,
            'daily wager': -2
        }
        job_score = 0
        
        # Handle null values for jobType
        job_type = self._get_scalar_value('jobType', '')
        if self._is_na(job_type):
            job_type = 'factory worker'  # Default to middle category
        else:
            job_type = str(job_type).strip()
        
        # Check if job_type is a list or string
        if isinstance(job_type, list):
            for job in job_type:
                job_score = job_type_map.get(job.lower(), 0)
        else:
            job_score = job_type_map.get(job_type.lower(), 0)
        
        self.score += job_score
        rst += job_score

        job_stability_map = {
            'permanent': 5,
            'seasonal': 1,
            'irregular': -2
        }
        
        # Handle null values for jobStability
        job_stability = self._get_scalar_value('jobStability', '')
        if self._is_na(job_stability):
            job_stability = 'seasonal'  # Default to middle category
        else:
            job_stability = str(job_stability).strip().lower()
        
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
        
        # Handle null values for emergencyFundManagement
        fund_management = self._get_scalar_value('emergencyFundManagement', '')
        if self._is_na(fund_management):
            fund_management = 'Family-friends'  # Default to middle category
        else:
            fund_management = str(fund_management).strip()
        
        fund_management_score = fund_management_map.get(fund_management, 0)
        self.score += fund_management_score

        # emergencyInterestRate mapping
        interest_rate_map = {
            '0%': 3,
            '1-10': 1,
            '20%': -2
        }
        
        # Handle null values for emergencyInterestRate
        interest_rate = self._get_scalar_value('emergencyInterestRate', '')
        if self._is_na(interest_rate):
            interest_rate = '1-10'  # Default to middle category
        else:
            interest_rate = str(interest_rate).strip()
        
        interest_rate_score = interest_rate_map.get(interest_rate, 0)
        self.score += interest_rate_score

        # pastEmergencyExperience mapping
        past_experience_map = {
            'no': 3,
            'yes': -1
        }
        
        # Handle null values for pastEmergencyExperience
        past_experience = self._get_scalar_value('pastEmergencyExperience', '')
        if self._is_na(past_experience):
            past_experience = 'no'  # Default to better category
        else:
            past_experience = str(past_experience).strip().lower()
        
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
            'Mobile Phones Only': 1,
            'None': 0
        }
        
        # Handle null values for familyAssets
        family_assets = self._get_scalar_value('assetsOwned')
        if self._is_na(family_assets):
            family_assets = []  # Default to empty list
        elif isinstance(family_assets, str):
            # If it's a string, try to convert to list or treat as single item
            if family_assets.strip() == '':
                family_assets = []
            else:
                family_assets = [family_assets.strip()]
        
        # Check each asset
        for asset in family_assets:
            score += asset_map.get(asset, 0)

        # Check motorizedVehicles
        motorized = self._get_scalar_value('motorizedVehicles', '')
        if self._is_na(motorized):
            motorized = 'no'  # Default to no
        else:
            motorized = str(motorized).strip().lower()
        
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
        
        # Handle null values for incomeFrequency
        income_frequency = self._get_scalar_value('incomeFrequency', '')
        if self._is_na(income_frequency):
            income_frequency = 'monthly'  # Default to best category
        else:
            income_frequency = str(income_frequency).strip().lower()
        
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
        secondary_income = self._get_scalar_value('secondaryIncome', '')
        if self._is_na(secondary_income):
            secondary_income = 'no'  # Default to no
        else:
            secondary_income = str(secondary_income).strip().lower()
        
        if secondary_income == 'yes':
            score += 4

        # monthlySavings (categorical)
        monthly_savings = self._get_scalar_value('monthlySavings', '')
        if self._is_na(monthly_savings):
            monthly_savings = '0'  # Default to lowest category
        else:
            monthly_savings = str(monthly_savings).strip()
        
        savings_map = {
            '0': -1,
            '1-500': 2,
            '1000+': 5
        }
        score += savings_map.get(monthly_savings, 0)

        # governmentSchemeAwareness
        scheme_awareness = self._get_scalar_value('governmentSchemeAwareness', '')
        if self._is_na(scheme_awareness):
            scheme_awareness = 'no'  # Default to no
        else:
            scheme_awareness = str(scheme_awareness).strip().lower()
        
        if scheme_awareness == 'yes':
            score += 3

        # loanDefaultHistory
        loan_default = self._get_scalar_value('loanDefaultHistory', '')
        if self._is_na(loan_default):
            loan_default = 'no'  # Default to better category
        else:
            loan_default = str(loan_default).strip().lower()
        
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
        lpg_preference = self._get_scalar_value('lpgPreference', '')
        if self._is_na(lpg_preference):
            lpg_preference = 'no'  # Default to no
        else:
            lpg_preference = str(lpg_preference).strip().lower()
        
        if lpg_preference == 'yes':
            score += 3

        # LPG Challenges
        lpg_challenges = self._get_scalar_value('lpgChallenges', '')
        if self._is_na(lpg_challenges):
            lpg_challenges = 'cost'  # Default to middle category
        else:
            lpg_challenges = str(lpg_challenges).strip().lower()
        
        if lpg_challenges == 'none':
            score += 2
        elif lpg_challenges == 'cost':
            score += 1

        # Cylinder Preference
        cylinder_preference = self._get_scalar_value('cylinderPreference', '')
        if self._is_na(cylinder_preference):
            cylinder_preference = 'other'  # Default to other
        else:
            cylinder_preference = str(cylinder_preference).strip().lower()
        
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
    