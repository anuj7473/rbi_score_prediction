from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import pandas as pd
import requests
import csv
from datetime import datetime
import os

FASTAPI_BASE_URL = "http://127.0.0.1:8000"

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route('/')
def home():
    """Home page with credit score form"""
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate_score():
    """Send form data to FastAPI, store the full API response in history, and render the result."""
    try:
        # Get all form data
        form_data = {}
        for key in request.form.keys():
            if key == 'assetsOwned':
                form_data[key] = request.form.getlist(key)
            else:
                form_data[key] = request.form.get(key)

        # Prepare only the fields needed for FastAPI
        fastapi_fields = [
            'internetUsed', 'dataPackExpense', 'dependentMembers', 'foodFuelExpensePercent',
            'outstandingLoansEMI', 'earningDependentRation', 'jobType', 'jobStability',
            'emergencyFundManagement', 'emergencyInterestRate', 'pastEmergencyExperience',
            'assetsOwned', 'motorizedVehicles', 'incomeFrequency', 'secondaryIncome',
            'monthlySavings', 'governmentSchemeAwareness', 'loanDefaultHistory',
            'lpgPreference', 'lpgChallenges', 'cylinderPreference'
        ]
        fastapi_data = {}
        for k in fastapi_fields:
            if k == 'assetsOwned':
                v = form_data.get(k)
                if v is None:
                    fastapi_data[k] = []
                elif isinstance(v, list):
                    fastapi_data[k] = v
                elif v == '':
                    fastapi_data[k] = []
                else:
                    fastapi_data[k] = [v]
            else:
                v = form_data.get(k)
                if isinstance(v, list):
                    fastapi_data[k] = v[0] if v else ''
                else:
                    fastapi_data[k] = v

        # Set defaults for missing FastAPI fields
        defaults = {
            'internetUsed': 'no',
            'dataPackExpense': '\u20b90-\u20b9100',
            'dependentMembers': '0-2',
            'foodFuelExpensePercent': 'Less than 25%',
            'outstandingLoansEMI': '0',
            'earningDependentRation': '1:2',
            'jobType': 'factory worker',
            'jobStability': 'seasonal',
            'emergencyFundManagement': 'Family-friends',
            'emergencyInterestRate': '1-10',
            'pastEmergencyExperience': 'no',
            'assetsOwned': [],
            'motorizedVehicles': 'no',
            'incomeFrequency': 'monthly',
            'secondaryIncome': 'no',
            'monthlySavings': '0',
            'governmentSchemeAwareness': 'no',
            'loanDefaultHistory': 'no',
            'lpgPreference': 'no',
            'lpgChallenges': 'cost',
            'cylinderPreference': 'other'
        }
        for key, default_value in defaults.items():
            if key not in fastapi_data or fastapi_data[key] == '' or fastapi_data[key] is None:
                fastapi_data[key] = default_value

        # Debug: Print assetsOwned value and type in form_data
        print(f"[DEBUG] form_data['assetsOwned']: {form_data.get('assetsOwned')} (type: {type(form_data.get('assetsOwned'))})")
        # Debug: Print assetsOwned value and type in fastapi_data
        print(f"[DEBUG] fastapi_data['assetsOwned']: {fastapi_data.get('assetsOwned')} (type: {type(fastapi_data.get('assetsOwned'))})")
        # Debug: Print outgoing FastAPI payload
        print("Sending to FastAPI:", fastapi_data)

        # Make request to FastAPI service
        try:
            response = requests.post(
                f"{FASTAPI_BASE_URL}/calculate-credit-score",
                json=fastapi_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            if response.status_code != 200:
                flash(f"Error from scoring service: {response.status_code} - {response.text}", "error")
                return redirect(url_for('home'))
            response.raise_for_status()
            api_response = response.json()
            
            # Debug: Print complete FastAPI response
            print(f"[DEBUG] Complete FastAPI Response:")
            for key, value in api_response.items():
                print(f"  {key}: {value} (type: {type(value)})")
            
            # Store the full API response in history, along with form data and timestamp
            history_row = dict(form_data)
            history_row.update(api_response)
            history_row['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Debug: Print what's being saved to CSV
            print(f"[DEBUG] History row app_score: {history_row.get('app_score')}")
            print(f"[DEBUG] History row risk_level: {history_row.get('risk_level')}")
            print(f"[DEBUG] Full history row keys: {list(history_row.keys())}")
            
            csv_file = 'history.csv'
            write_header = not os.path.exists(csv_file)
            with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list(history_row.keys()))
                if write_header:
                    writer.writeheader()
                writer.writerow(history_row)
            
            # Debug: Print what's being passed to template
            print(f"[DEBUG] API Response: {api_response}")
            print(f"[DEBUG] API Response keys: {list(api_response.keys())}")
            
            return render_template('result.html', scores=api_response, form_data=form_data)
        except requests.exceptions.ConnectionError:
            flash("Error: Cannot connect to the scoring service. Please ensure the FastAPI service is running on localhost:8000", "error")
            return redirect(url_for('home'))
        except requests.exceptions.Timeout:
            flash("Error: Request to scoring service timed out. Please try again.", "error")
            return redirect(url_for('home'))
        except requests.exceptions.RequestException as e:
            flash(f"Error communicating with scoring service: {str(e)}", "error")
            return redirect(url_for('home'))
    except Exception as e:
        flash(f"Error calculating score: {str(e)}", "error")
        return redirect(url_for('home'))

@app.route('/history')
def history():
    """Display history of all credit score calculations"""
    import csv
    import os
    history_data = []
    csv_file = 'history.csv'
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Debug: Print what's being read from CSV
                print(f"[DEBUG] CSV row app_score: {row.get('app_score')}")
                print(f"[DEBUG] CSV row risk_level: {row.get('risk_level')}")
                history_data.append(row)
    return render_template('history.html', history=history_data)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Flask app is running"})

@app.route('/api/score-info')
def score_info():
    """Get score range information"""
    return jsonify({
        "raw_score_range": {"min": -150, "max": 150},
        "app_score_range": {"min": 300, "max": 850},
        "risk_levels": {
            "Low Risk": "700-850",
            "Medium Risk": "500-699", 
            "High Risk": "300-499"
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)