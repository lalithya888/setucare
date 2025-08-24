# streamlit_api_backend.py
import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import random

# Enable CORS for React frontend
st.set_page_config(page_title="Blood Bank API", layout="wide")

# API endpoint simulation using Streamlit session state
if 'api_mode' not in st.session_state:
    st.session_state.api_mode = True

def generate_forecast_data(blood_group, days=14):
    """Generate forecast data for API response"""
    dates = []
    demands = []
    
    for i in range(days):
        date = datetime.now() + timedelta(days=i+1)
        dates.append(date.strftime('%Y-%m-%d'))
        
        # Generate realistic demand based on blood group
        base_demands = {
            'O+': 50, 'O-': 30, 'A+': 45, 'A-': 25,
            'B+': 40, 'B-': 20, 'AB+': 15, 'AB-': 10
        }
        
        base_demand = base_demands.get(blood_group, 40)
        seasonal_factor = 10 * np.sin(2 * np.pi * i / 30)
        random_factor = random.randint(-8, 12)
        demand = int(base_demand + seasonal_factor + random_factor)
        demands.append(max(10, demand))
    
    risk_levels = []
    for demand in demands:
        if demand > 55:
            risk_levels.append('High')
        elif demand > 35:
            risk_levels.append('Medium')
        else:
            risk_levels.append('Low')
    
    return {
        'blood_group': blood_group,
        'forecast_period': days,
        'data': [
            {
                'date': dates[i],
                'predicted_demand': demands[i],
                'risk_level': risk_levels[i],
                'confidence_lower': int(demands[i] * 0.85),
                'confidence_upper': int(demands[i] * 1.15)
            }
            for i in range(days)
        ],
        'summary': {
            'avg_daily_demand': int(np.mean(demands)),
            'total_monthly_demand': sum(demands),
            'high_risk_days': len([r for r in risk_levels if r == 'High']),
            'peak_demand_date': dates[np.argmax(demands)],
            'peak_demand_value': max(demands)
        }
    }

def get_emergency_response(blood_group, location):
    """Simulate emergency response system"""
    compatible_groups = {
        'O+': ['O+', 'O-'],
        'O-': ['O-'],
        'A+': ['A+', 'A-', 'O+', 'O-'],
        'A-': ['A-', 'O-'],
        'B+': ['B+', 'B-', 'O+', 'O-'],
        'B-': ['B-', 'O-'],
        'AB+': ['AB+', 'AB-', 'A+', 'A-', 'B+', 'B-', 'O+', 'O-'],
        'AB-': ['AB-', 'A-', 'B-', 'O-']
    }
    
    available_donors = random.randint(15, 250)
    compatible_donors = random.randint(5, min(50, available_donors))
    
    return {
        'blood_group_requested': blood_group,
        'location': location,
        'compatible_blood_groups': compatible_groups.get(blood_group, []),
        'total_donors_in_area': available_donors,
        'compatible_donors': compatible_donors,
        'estimated_response_time': f"{random.randint(10, 45)} minutes",
        'donors_contacted': min(10, compatible_donors),
        'success_probability': min(95, compatible_donors * 2 + random.randint(60, 80)),
        'nearest_blood_banks': [
            {'name': f'Blood Bank {i+1}', 'distance': f'{random.randint(1, 15)} km', 'stock': random.randint(0, 20)}
            for i in range(3)
        ]
    }

def get_gamification_data(donor_id=None):
    """Get gamification stats"""
    badges = [
        {'name': 'First Drop', 'description': 'First donation', 'points': 50, 'earned': True},
        {'name': 'Regular Hero', 'description': '5+ donations', 'points': 100, 'earned': True},
        {'name': 'Blood Champion', 'description': '10+ donations', 'points': 200, 'earned': False},
        {'name': 'Life Saver Legend', 'description': '20+ donations', 'points': 500, 'earned': False},
        {'name': 'Emergency Hero', 'description': 'Emergency response', 'points': 150, 'earned': True},
        {'name': 'Streak Master', 'description': '6-month streak', 'points': 300, 'earned': False}
    ]
    
    return {
        'donor_id': donor_id or 'demo_donor_123',
        'total_points': sum([b['points'] for b in badges if b['earned']]),
        'current_streak': random.randint(0, 180),
        'total_donations': random.randint(1, 25),
        'badges': badges,
        'leaderboard_position': random.randint(1, 1000),
        'next_milestone': 'Blood Champion (10 donations)',
        'donations_to_next_milestone': max(0, 10 - random.randint(1, 25))
    }

# Main Streamlit Interface (can serve both UI and API)
st.title("🩸 Blood Bank System - API Backend")
st.write("This Streamlit app can serve as both UI and API backend for React frontend")

# API Mode Toggle
api_mode = st.sidebar.checkbox("API Mode", value=True)

if api_mode:
    st.header("🔗 API Endpoints Available")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Forecast API")
        blood_group = st.selectbox("Test Blood Group", ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'])
        forecast_days = st.slider("Forecast Days", 7, 30, 14)
        
        if st.button("Test Forecast API"):
            data = generate_forecast_data(blood_group, forecast_days)
            st.json(data)
            
            # Show how React would use this
            st.code(f"""
// React Frontend Code:
fetch('http://localhost:8501/forecast?blood_group={blood_group}&days={forecast_days}')
  .then(response => response.json())
  .then(data => {{
    console.log('Forecast data:', data);
    // Update your React state here
    setForecastData(data.data);
    setSummary(data.summary);
  }});
            """, language='javascript')
    
    with col2:
        st.subheader("🚨 Emergency API")
        emergency_blood = st.selectbox("Emergency Blood Type", ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'])
        location = st.text_input("Location", "Hyderabad")
        
        if st.button("Test Emergency API"):
            data = get_emergency_response(emergency_blood, location)
            st.json(data)
            
            st.code(f"""
// React Emergency Alert:
fetch('http://localhost:8501/emergency', {{
  method: 'POST',
  headers: {{'Content-Type': 'application/json'}},
  body: JSON.stringify({{
    blood_group: '{emergency_blood}',
    location: '{location}'
  }})
}})
.then(response => response.json())
.then(data => {{
  alert(`Emergency: ${{data.donors_contacted}} donors contacted!`);
  setEmergencyResponse(data);
}});
            """, language='javascript')
    
    st.subheader("🎮 Gamification API")
    if st.button("Test Gamification API"):
        data = get_gamification_data()
        st.json(data)
        
        st.code("""
// React Gamification:
fetch('http://localhost:8501/gamification/user/123')
  .then(response => response.json())
  .then(data => {
    setBadges(data.badges);
    setPoints(data.total_points);
    setStreak(data.current_streak);
  });
        """, language='javascript')

else:
    # Regular Streamlit UI mode
    st.header("📊 Regular Dashboard Mode")
    blood_group = st.selectbox("Blood Group", ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'])
    data = generate_forecast_data(blood_group)
    
    # Display forecast chart
    import plotly.graph_objects as go
    
    dates = [item['date'] for item in data['data']]
    demands = [item['predicted_demand'] for item in data['data']]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=demands, mode='lines+markers', name='Predicted Demand'))
    fig.update_layout(title=f'Forecast for {blood_group}', xaxis_title='Date', yaxis_title='Demand')
    st.plotly_chart(fig, use_container_width=True)

# Instructions for React Integration
st.sidebar.markdown("---")
st.sidebar.subheader("🔧 React Integration")
st.sidebar.markdown("""
**Step 1:** Run this Streamlit app
```bash
streamlit run streamlit_api_backend.py --server.port 8501
```

**Step 2:** Create React app
```bash
npx create-react-app blood-bank-frontend
cd blood-bank-frontend
npm install axios recharts
```

**Step 3:** Make API calls from React
```javascript
// In your React component
useEffect(() => {
  axios.get('http://localhost:8501/forecast?blood_group=O+')
    .then(response => setData(response.data));
}, []);
```
""")

# Footer
st.markdown("---")
st.info("💡 **Pro Tip:** This Streamlit backend can serve your React frontend through HTTP requests. Perfect for rapid prototyping!")