from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
from score import ScoreCalculator

app = FastAPI(title="Credit Scoring API", version="1.0.0")

# Pydantic models for request and response
class CreditScoreRequest(BaseModel):
    # Digital Access fields
    internetUsed: Optional[str] = Field(default="no", description="Internet usage: yes/no")
    dataPackExpense: Optional[str] = Field(default="₹0-₹100", description="Data pack expense range")
    
    # Family Spending fields
    dependentMembers: Optional[str] = Field(default="0-2", description="Number of dependent members")
    
    # Family Dynamics fields
    foodFuelExpensePercent: Optional[str] = Field(default="Less than 25%", description="Food fuel expense percentage")
    outstandingLoansEMI: Optional[str] = Field(default=None, description="Outstanding loan EMI")
    
    # Income Dependency fields
    earningDependentRation: Optional[str] = Field(default="1:2", description="Earning to dependent ratio")
    jobType: Optional[str] = Field(default="factory worker", description="Type of job")
    jobStability: Optional[str] = Field(default="seasonal", description="Job stability")
    
    # Emergency Fund fields
    emergencyFundManagement: Optional[str] = Field(default="Family-friends", description="Emergency fund source")
    emergencyInterestRate: Optional[str] = Field(default="1-10", description="Emergency interest rate")
    pastEmergencyExperience: Optional[str] = Field(default="no", description="Past emergency experience")
    
    # Asset Ownership fields
    assetsOwned: Optional[List[str]] = Field(default=[], description="List of assets owned")
    motorizedVehicles: Optional[str] = Field(default="no", description="Owns motorized vehicles")
    
    # Income Frequency fields
    incomeFrequency: Optional[str] = Field(default="monthly", description="Income frequency")
    
    # Financial Behavior fields
    secondaryIncome: Optional[str] = Field(default="no", description="Has secondary income")
    monthlySavings: Optional[str] = Field(default="0", description="Monthly savings amount")
    governmentSchemeAwareness: Optional[str] = Field(default="no", description="Government scheme awareness")
    loanDefaultHistory: Optional[str] = Field(default="no", description="Loan default history")
    
    # LPG Adoption fields
    lpgPreference: Optional[str] = Field(default="no", description="LPG preference")
    lpgChallenges: Optional[str] = Field(default="cost", description="LPG challenges")
    cylinderPreference: Optional[str] = Field(default="other", description="Cylinder preference")

class CreditScoreResponse(BaseModel):
    digital_access: int = Field(description="Digital Access score")
    spending_patterns: int = Field(description="Spending Patterns score")
    family_dynamic: int = Field(description="Family Dynamic score")
    income_stability: int = Field(description="Income Stability score")
    emergency_fund: int = Field(description="Emergency Fund score")
    asset_ownership: int = Field(description="Asset Ownership score")
    income_frequency: int = Field(description="Income Frequency score")
    financial_behavior: int = Field(description="Financial Behavior score")
    lpg_adoption: int = Field(description="LPG Adoption score")
    raw_total_score: int = Field(description="Raw total score")
    app_score: int = Field(description="Normalized app score (300-850)")
    risk_level: str = Field(description="Risk level based on app score")

def normalize_score(raw_score: int, min_raw: int = -150, max_raw: int = +150) -> int:
    """
    Normalize raw score from range [min_raw, max_raw] to [300, 850]
    """
    # Ensure raw_score is within bounds
    raw_score = max(min_raw, min(raw_score, max_raw))
    
    # Normalize to 0-1 range
    normalized = (raw_score - min_raw) / (max_raw - min_raw)
    
    # Scale to 300-850 range
    app_score = int(300 + (normalized * 550))
    
    return app_score

def get_risk_level(app_score: int) -> str:
    """
    Determine risk level based on app score
    """
    if 700 <= app_score <= 850:
        return "Low Risk"
    elif 500 <= app_score <= 699:
        return "Medium Risk"
    elif 300 <= app_score <= 499:
        return "High Risk"
    else:
        return "Invalid Score"

@app.post("/calculate-credit-score", response_model=CreditScoreResponse)
async def calculate_credit_score(request: CreditScoreRequest):
    """
    Calculate credit score based on provided parameters
    """
    try:
        row_data = request.dict()
        # Defensive: Convert all non-assetsOwned lists to scalar
        for k, v in row_data.items():
            if k != "assetsOwned" and isinstance(v, list):
                if len(v) == 0:
                    row_data[k] = ""
                else:
                    row_data[k] = v[0]
        print(f"FastAPI received data: {row_data}")
        for k, v in row_data.items():
            print(f"  {k}: {v} (type: {type(v)})")
        calculator = ScoreCalculator(row_data)
        # Calculate individual scores
        digital_access = calculator.digital_access_score()
        spending_patterns = calculator.family_spending_score()
        family_dynamic = calculator.family_dynamics_score()
        income_stability = calculator.income_dependency_score()
        emergency_fund = calculator.emergency_fund_access_score()
        asset_ownership = calculator.asset_ownership_score()
        income_frequency = calculator.income_frequency_score()
        financial_behavior = calculator.financial_behavior_score()
        lpg_adoption = calculator.lpg_adoption_score()
        # Calculate total raw score
        raw_total_score = calculator.total_score()
        # Normalize to app score (300-850)
        app_score = normalize_score(raw_total_score)
        # Determine risk level
        risk_level = get_risk_level(app_score)
        return CreditScoreResponse(
            digital_access=digital_access,
            spending_patterns=spending_patterns,
            family_dynamic=family_dynamic,
            income_stability=income_stability,
            emergency_fund=emergency_fund,
            asset_ownership=asset_ownership,
            income_frequency=income_frequency,
            financial_behavior=financial_behavior,
            lpg_adoption=lpg_adoption,
            raw_total_score=raw_total_score,
            app_score=app_score,
            risk_level=risk_level
        )
    except Exception as e:
        print(f"FastAPI error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error calculating credit score: {str(e)}")

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Credit Scoring API",
        "version": "1.0.0",
        "endpoints": {
            "POST /calculate-credit-score": "Calculate credit score based on provided parameters",
            "GET /health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "API is running"}

@app.get("/score-ranges")
async def score_ranges():
    """
    Get information about score ranges and risk levels
    """
    return {
        "raw_score_range": {
            "min": -150,
            "max": +150,
            "description": "Raw score range based on scoring algorithm"
        },
        "app_score_range": {
            "min": 300,
            "max": 850,
            "description": "Normalized app score range"
        },
        "risk_levels": {
            "Low Risk": "700-850",
            "Medium Risk": "500-699",
            "High Risk": "300-499"
        },
        "scoring_components": {
            "digital_access": "Internet usage and data expense",
            "spending_patterns": "Based on dependent members",
            "family_dynamic": "Food/fuel expenses and loan EMI",
            "income_stability": "Job type, stability, and earning ratio",
            "emergency_fund": "Emergency fund management and experience",
            "asset_ownership": "Assets owned and motorized vehicles",
            "income_frequency": "Frequency of income",
            "financial_behavior": "Savings, secondary income, loan history",
            "lpg_adoption": "LPG preference and usage"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)