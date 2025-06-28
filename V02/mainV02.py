import pandas as pd
import numpy as np
import score

df = pd.read_excel(r'E:\ML\01Projects\rbi_score_prediction\V02\Modified_Underwriting_Form.xlsx')

# Test all scoring methods
print("Testing all scoring methods...")

# Create score columns for each method
df['digital_access_score'] = df.apply(
    lambda row: score.ScoreCalculator(row).digital_access_score(), axis=1
)

df['family_spending_score'] = df.apply(
    lambda row: score.ScoreCalculator(row).family_spending_score(), axis=1
)

df['family_dynamics_score'] = df.apply(
    lambda row: score.ScoreCalculator(row).family_dynamics_score(), axis=1
)

df['income_dependency_score'] = df.apply(
    lambda row: score.ScoreCalculator(row).income_dependency_score(), axis=1
)

df['emergency_fund_access_score'] = df.apply(
    lambda row: score.ScoreCalculator(row).emergency_fund_access_score(), axis=1
)

df['asset_ownership_score'] = df.apply(
    lambda row: score.ScoreCalculator(row).asset_ownership_score(), axis=1
)

df['income_frequency_score'] = df.apply(
    lambda row: score.ScoreCalculator(row).income_frequency_score(), axis=1
)

df['financial_behavior_score'] = df.apply(
    lambda row: score.ScoreCalculator(row).financial_behavior_score(), axis=1
)

df['lpg_adoption_score'] = df.apply(
    lambda row: score.ScoreCalculator(row).lpg_adoption_score(), axis=1
)

# Calculate total score
df['total_score'] = df.apply(
    lambda row: score.ScoreCalculator(row).total_score(), axis=1
)

# print("All scoring methods completed successfully!")
# print(f"Total rows processed: {len(df)}")
# print("\nScore ranges:")
# score_columns = ['digital_access_score', 'family_spending_score', 'family_dynamics_score', 
#                 'income_dependency_score', 'emergency_fund_access_score', 'asset_ownership_score',
#                 'income_frequency_score', 'financial_behavior_score', 'lpg_adoption_score', 'total_score']

# for col in score_columns:
#     if col in df.columns:
#         print(f"{col}: {df[col].min()} to {df[col].max()}")

# print(f"\nTotal score range: {df['total_score'].min()} to {df['total_score'].max()}")
# print(f"Average total score: {df['total_score'].mean():.2f}")
