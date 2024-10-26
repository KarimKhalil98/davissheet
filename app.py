from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from datetime import datetime, timedelta
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'

work_logs = []
admin_password = None  # Initially set as None, so first-time setup

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/employee', methods=['GET', 'POST'])
def employee():
    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        ticket_number = data.get('ticket_number')
        location = data.get('location')
        wo_number = data.get('wo_number')
        week_start = data.get('week_start')
        week_end = data.get('week_end')

        dates = get_dates(week_start, week_end)
        hours = data.getlist('hours')
        not_applicable = data.getlist('not_applicable')

        for i, date in enumerate(dates):
            work_logs.append({
                'name': name,
                'ticket_number': ticket_number,
                'location': location,
                'wo_number': wo_number,
                'date': date,
                'hours': hours[i],
                'not_applicable': bool(not_applicable[i]) if i < len(not_applicable) else False
            })

        return jsonify({'message': 'Work log submitted successfully!'})
    return render_template('employee.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    global admin_password
    if request.method == 'POST':
        if not admin_password:  # Set password for the first time
            admin_password = request.form.get('password')
            return redirect(url_for('admin_dashboard'))
        elif request.form.get('password') == admin_password:  # Subsequent logins
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return 'Incorrect Password', 401
    return render_template('admin_login.html')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        employee_name = request.form.get('employee_name')
        logs = [log for log in work_logs if log['name'].lower() == employee_name.lower()]
        return render_template('admin_dashboard.html', logs=logs)

    return render_template('admin_dashboard.html', logs=[])

def get_dates(start_date, end_date):
    dates = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    return dates

if __name__ == '__main__':
    app.run(debug=True)
