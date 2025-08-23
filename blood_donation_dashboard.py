
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Configure page
st.set_page_config(
    page_title="🩸 Blood Bridge - Management Dashboard",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #e74c3c;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .emergency-alert {
        background-color: #ff6b6b;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .success-alert {
        background-color: #51cf66;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all the datasets and models"""
    try:
        # Load donor data
        df_donors = pd.read_csv('/Users/lilyland/Downloads/setucare/hackathon_data.csv')

        # Load gamification data
        df_gamification = pd.read_csv('/Users/lilyland/Downloads/setucare/donor_gamification_data.csv')

        # Load feature importance
        feature_importance = pd.read_csv('/Users/lilyland/Downloads/setucare/feature_importance.csv')

        # Load model info
        with open('/Users/lilyland/Downloads/setucare/model_info.json', 'r') as f:
            model_info = json.load(f)

        return df_donors, df_gamification, feature_importance, model_info
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None

def main():
    # Header
    st.markdown('<h1 class="main-header">🩸 Blood Bridge Management Dashboard</h1>', unsafe_allow_html=True)

    # Load data
    df_donors, df_gamification, feature_importance, model_info = load_data()

    if df_donors is None:
        st.error("❌ Failed to load data. Please check file paths.")
        return

    # Sidebar navigation
    st.sidebar.title("🔧 Navigation")
    page = st.sidebar.selectbox("Choose a section:", [
        "📊 Overview Dashboard",
        "👥 Donor Analytics", 
        "🚨 Emergency Management",
        "🏆 Gamification & Leaderboards",
        "🤖 ML Model Performance",
        "📈 Blood Demand Forecast",
        "⚙️ System Settings"
    ])

    if page == "📊 Overview Dashboard":
        show_overview_dashboard(df_donors, df_gamification, model_info)
    elif page == "👥 Donor Analytics":
        show_donor_analytics(df_donors, df_gamification)
    elif page == "🚨 Emergency Management":
        show_emergency_management(df_donors)
    elif page == "🏆 Gamification & Leaderboards":
        show_gamification_dashboard(df_gamification)
    elif page == "🤖 ML Model Performance":
        show_ml_dashboard(feature_importance, model_info)
    elif page == "📈 Blood Demand Forecast":
        show_forecast_dashboard(df_donors)
    elif page == "⚙️ System Settings":
        show_system_settings()

def show_overview_dashboard(df_donors, df_gamification, model_info):
    st.header("📊 System Overview")

    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_donors = len(df_donors)
        st.metric("👥 Total Donors", f"{total_donors:,}")

    with col2:
        active_donors = len(df_donors[df_donors['user_donation_active_status'] == 'Active'])
        st.metric("✅ Active Donors", f"{active_donors:,}")

    with col3:
        total_donations = df_donors['donations_till_date'].sum()
        st.metric("🩸 Total Donations", f"{total_donations:,.0f}")

    with col4:
        avg_score = df_gamification['score'].mean()
        st.metric("⭐ Avg Donor Score", f"{avg_score:.0f}")

    st.divider()

    # Charts in two columns
    col1, col2 = st.columns(2)

    with col1:
        # Blood group distribution
        st.subheader("🩸 Blood Group Distribution")
        blood_counts = df_donors['blood_group'].value_counts().head(8)
        fig_blood = px.pie(
            values=blood_counts.values,
            names=blood_counts.index,
            title="Distribution of Blood Groups",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_blood, use_container_width=True)

    with col2:
        # Donor roles
        st.subheader("👤 Donor Roles")
        role_counts = df_donors['role'].value_counts()
        fig_roles = px.bar(
            x=role_counts.index,
            y=role_counts.values,
            title="Number of Donors by Role",
            color=role_counts.values,
            color_continuous_scale="Viridis"
        )
        fig_roles.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_roles, use_container_width=True)

    # Recent activity timeline
    st.subheader("📅 Registration Timeline")
    df_donors['registration_date'] = pd.to_datetime(df_donors['registration_date'])
    monthly_reg = df_donors.groupby(df_donors['registration_date'].dt.to_period('M')).size()

    fig_timeline = px.line(
        x=monthly_reg.index.astype(str),
        y=monthly_reg.values,
        title="Monthly Donor Registrations",
        labels={'x': 'Month', 'y': 'New Registrations'}
    )
    fig_timeline.update_traces(line_color='#e74c3c', line_width=3)
    st.plotly_chart(fig_timeline, use_container_width=True)

def show_donor_analytics(df_donors, df_gamification):
    st.header("👥 Donor Analytics")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        blood_groups = ['All'] + list(df_donors['blood_group'].unique())
        selected_blood = st.selectbox("🩸 Filter by Blood Group:", blood_groups)

    with col2:
        roles = ['All'] + list(df_donors['role'].unique())
        selected_role = st.selectbox("👤 Filter by Role:", roles)

    with col3:
        status_options = ['All', 'Active', 'Inactive']
        selected_status = st.selectbox("📊 Filter by Status:", status_options)

    # Apply filters
    filtered_df = df_donors.copy()
    if selected_blood != 'All':
        filtered_df = filtered_df[filtered_df['blood_group'] == selected_blood]
    if selected_role != 'All':
        filtered_df = filtered_df[filtered_df['role'] == selected_role]
    if selected_status != 'All':
        status_map = {'Active': 'Active', 'Inactive': 'Inactive'}
        filtered_df = filtered_df[filtered_df['user_donation_active_status'] == status_map[selected_status]]

    st.info(f"📊 Showing {len(filtered_df)} donors (filtered from {len(df_donors)} total)")

    # Analytics charts
    col1, col2 = st.columns(2)

    with col1:
        # Donation distribution
        st.subheader("🎯 Donation Distribution")
        donations = filtered_df['donations_till_date'].fillna(0)
        fig_donations = px.histogram(
            x=donations,
            nbins=20,
            title="Number of Donations per Donor",
            labels={'x': 'Number of Donations', 'y': 'Number of Donors'}
        )
        st.plotly_chart(fig_donations, use_container_width=True)

    with col2:
        # Geographic distribution
        st.subheader("📍 Geographic Distribution")
        fig_geo = px.scatter_mapbox(
            filtered_df.dropna(subset=['latitude', 'longitude']).head(500),
            lat='latitude',
            lon='longitude',
            color='blood_group',
            hover_data=['role', 'donations_till_date'],
            mapbox_style='open-street-map',
            title="Donor Locations",
            zoom=10
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    # Top donors table
    st.subheader("🏆 Top Donors")
    top_donors = filtered_df.nlargest(10, 'donations_till_date')[
        ['user_id', 'blood_group', 'role', 'donations_till_date', 'user_donation_active_status']
    ].rename(columns={
        'user_id': 'Donor ID',
        'blood_group': 'Blood Group',
        'role': 'Role',
        'donations_till_date': 'Total Donations',
        'user_donation_active_status': 'Status'
    })
    st.dataframe(top_donors, use_container_width=True)

def show_emergency_management(df_donors):
    st.header("🚨 Emergency Management System")

    # Emergency request simulator
    st.subheader("📱 Emergency Request Simulator")

    col1, col2 = st.columns(2)

    with col1:
        emergency_blood = st.selectbox(
            "🩸 Required Blood Group:", 
            ['O Positive', 'O Negative', 'A Positive', 'A Negative', 
             'B Positive', 'B Negative', 'AB Positive', 'AB Negative']
        )

        emergency_city = st.selectbox("🏙️ City:", ['Hyderabad', 'Bangalore', 'Mumbai', 'Delhi'])

        urgency_level = st.select_slider("⚡ Urgency Level:", ['Low', 'Medium', 'High', 'Critical'])

    with col2:
        quantity_needed = st.number_input("📊 Units Needed:", min_value=1, max_value=10, value=2)

        st.write("📍 **Emergency Location:**")
        lat = st.number_input("Latitude:", value=17.3850, format="%.4f")
        lon = st.number_input("Longitude:", value=78.4867, format="%.4f")

    if st.button("🚨 SEND EMERGENCY ALERT", type="primary"):
        # Simulate emergency processing
        compatible_donors = get_compatible_donors(df_donors, emergency_blood)

        st.success(f"✅ Emergency alert sent!")
        st.info(f"📊 Found {len(compatible_donors)} compatible donors for {emergency_blood}")

        # Show emergency metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("⚡ Response Time", "2.3 sec")

        with col2:
            st.metric("📱 Alerts Sent", min(10, len(compatible_donors)))

        with col3:
            estimated_response = min(8, len(compatible_donors) // 3)
            st.metric("📞 Expected Responses", estimated_response)

        # Show top matching donors
        if len(compatible_donors) > 0:
            st.subheader("🏆 Top 5 Matching Donors")
            top_matches = compatible_donors.head(5)[
                ['blood_group', 'role', 'donations_till_date', 'user_donation_active_status']
            ].rename(columns={
                'blood_group': 'Blood Group',
                'role': 'Role', 
                'donations_till_date': 'Donations',
                'user_donation_active_status': 'Status'
            })
            st.dataframe(top_matches, use_container_width=True)

def get_compatible_donors(df_donors, blood_group):
    """Get compatible donors for a blood group"""
    compatibility = {
        'O Negative': ['O Negative'],
        'O Positive': ['O Negative', 'O Positive'],
        'A Negative': ['O Negative', 'A Negative'],
        'A Positive': ['O Negative', 'O Positive', 'A Negative', 'A Positive'],
        'B Negative': ['O Negative', 'B Negative'],
        'B Positive': ['O Negative', 'O Positive', 'B Negative', 'B Positive'],
        'AB Negative': ['O Negative', 'A Negative', 'B Negative', 'AB Negative'],
        'AB Positive': ['O Negative', 'O Positive', 'A Negative', 'A Positive', 
                      'B Negative', 'B Positive', 'AB Negative', 'AB Positive']
    }

    compatible_groups = compatibility.get(blood_group, [blood_group])
    return df_donors[df_donors['blood_group'].isin(compatible_groups)]

def show_gamification_dashboard(df_gamification):
    st.header("🏆 Gamification & Leaderboards")

    # Top performers
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥇 Top 10 Donors by Score")
        top_scores = df_gamification.nlargest(10, 'score')[
            ['score', 'donations', 'badge_count', 'blood_group']
        ].reset_index(drop=True)
        top_scores.index += 1  # Start from 1
        st.dataframe(top_scores, use_container_width=True)

    with col2:
        st.subheader("🎖️ Badge Distribution")
        badge_dist = df_gamification['badge_count'].value_counts().sort_index()
        fig_badges = px.bar(
            x=badge_dist.index,
            y=badge_dist.values,
            title="Number of Donors by Badge Count",
            labels={'x': 'Number of Badges', 'y': 'Number of Donors'}
        )
        st.plotly_chart(fig_badges, use_container_width=True)

    # Gamification analytics
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Score Distribution")
        fig_score_dist = px.histogram(
            df_gamification, 
            x='score', 
            nbins=30,
            title="Donor Score Distribution"
        )
        st.plotly_chart(fig_score_dist, use_container_width=True)

    with col2:
        st.subheader("🩸 Donations vs Score")
        fig_correlation = px.scatter(
            df_gamification,
            x='donations',
            y='score',
            color='blood_group',
            title="Relationship between Donations and Score"
        )
        st.plotly_chart(fig_correlation, use_container_width=True)

    # Sample motivational messages
    st.subheader("💬 Sample Motivational Messages")

    sample_messages = [
        "🎉 Congratulations! You've earned the 'Blood Champion' badge!",
        "🔥 Amazing! You're on a 6-month donation streak!",
        "⭐ You're in the top 10% of donors in your area!",
        "💪 Your donations have helped save 15 lives this year!"
    ]

    for msg in sample_messages:
        st.info(msg)

def show_ml_dashboard(feature_importance, model_info):
    st.header("🤖 ML Model Performance")

    # Model metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        rf_accuracy = model_info.get('random_forest_accuracy', 0) * 100
        st.metric("🌲 Random Forest Accuracy", f"{rf_accuracy:.1f}%")

    with col2:
        lr_accuracy = model_info.get('logistic_regression_accuracy', 0) * 100
        st.metric("📈 Logistic Regression Accuracy", f"{lr_accuracy:.1f}%")

    with col3:
        training_samples = model_info.get('training_samples', 0)
        st.metric("📊 Training Samples", f"{training_samples:,}")

    # Feature importance chart
    st.subheader("🔍 Feature Importance Analysis")
    fig_importance = px.bar(
        feature_importance,
        x='importance',
        y='feature',
        orientation='h',
        title="Feature Importance in Donor Prediction Model",
        color='importance',
        color_continuous_scale='Viridis'
    )
    fig_importance.update_layout(height=600)
    st.plotly_chart(fig_importance, use_container_width=True)

    # Model info
    st.subheader("ℹ️ Model Information")
    st.json(model_info)

def show_forecast_dashboard(df_donors):
    st.header("📈 Blood Demand Forecast")

    st.info("🔧 Forecast model is under development. Showing simulated data for demonstration.")

    # Simulate forecast data
    dates = pd.date_range(start=datetime.now(), periods=30, freq='D')
    blood_groups = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']

    # Create simulated forecast
    forecast_data = []
    for date in dates:
        for bg in blood_groups:
            base_demand = np.random.normal(50, 15)  # Base demand
            weekend_effect = 1.2 if date.weekday() >= 5 else 1.0
            demand = max(0, int(base_demand * weekend_effect))

            forecast_data.append({
                'date': date,
                'blood_group': bg,
                'predicted_demand': demand,
                'confidence_interval': np.random.uniform(0.8, 0.95)
            })

    df_forecast = pd.DataFrame(forecast_data)

    # Forecast visualization
    col1, col2 = st.columns(2)

    with col1:
        # Total daily demand
        st.subheader("📊 Daily Demand Forecast")
        daily_demand = df_forecast.groupby('date')['predicted_demand'].sum().reset_index()

        fig_daily = px.line(
            daily_demand,
            x='date',
            y='predicted_demand',
            title="Predicted Daily Blood Demand (Next 30 Days)"
        )
        st.plotly_chart(fig_daily, use_container_width=True)

    with col2:
        # Blood group breakdown
        st.subheader("🩸 Demand by Blood Group")
        bg_demand = df_forecast.groupby('blood_group')['predicted_demand'].sum().reset_index()

        fig_bg = px.bar(
            bg_demand,
            x='blood_group',
            y='predicted_demand',
            title="Total Predicted Demand by Blood Group (30 Days)"
        )
        st.plotly_chart(fig_bg, use_container_width=True)

    # Supply vs Demand analysis
    st.subheader("⚖️ Supply vs Demand Analysis")

    supply_data = []
    for bg in blood_groups:
        compatible_donors = get_compatible_donors(df_donors, bg.replace('+', ' Positive').replace('-', ' Negative'))
        active_donors = len(compatible_donors[compatible_donors['user_donation_active_status'] == 'Active'])
        total_demand = df_forecast[df_forecast['blood_group'] == bg]['predicted_demand'].sum()

        supply_data.append({
            'blood_group': bg,
            'active_donors': active_donors,
            'predicted_demand': total_demand,
            'supply_ratio': active_donors / max(1, total_demand) * 100
        })

    df_supply = pd.DataFrame(supply_data)

    fig_supply = px.bar(
        df_supply,
        x='blood_group',
        y=['active_donors', 'predicted_demand'],
        title="Supply (Active Donors) vs Demand Comparison",
        barmode='group'
    )
    st.plotly_chart(fig_supply, use_container_width=True)

def show_system_settings():
    st.header("⚙️ System Settings")

    st.subheader("🔧 Configuration")

    # Alert settings
    with st.expander("📱 Alert Settings"):
        st.checkbox("Enable SMS alerts", value=True)
        st.checkbox("Enable WhatsApp alerts", value=True)
        st.checkbox("Enable email notifications", value=False)

        st.slider("Maximum alerts per emergency:", 1, 20, 10)
        st.slider("Alert timeout (minutes):", 5, 60, 30)

    # Gamification settings
    with st.expander("🎮 Gamification Settings"):
        st.checkbox("Enable badge system", value=True)
        st.checkbox("Enable leaderboards", value=True)
        st.checkbox("Enable personalized messages", value=True)

        st.number_input("Points per donation:", 50, 200, 100)
        st.number_input("Streak bonus multiplier:", 1.0, 3.0, 1.5)

    # Model settings
    with st.expander("🤖 ML Model Settings"):
        st.selectbox("Primary prediction model:", ["Random Forest", "Logistic Regression"])
        st.slider("Prediction confidence threshold:", 0.5, 0.9, 0.7)
        st.checkbox("Auto-retrain models", value=True)

    # System status
    st.subheader("📊 System Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("✅ Database: Online")
        st.success("✅ ML Models: Loaded")

    with col2:
        st.success("✅ SMS Gateway: Active")
        st.warning("⚠️ WhatsApp API: Limited")

    with col3:
        st.success("✅ Gamification: Active")
        st.success("✅ Emergency System: Ready")

if __name__ == "__main__":
    main()
