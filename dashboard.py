import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta
import random
import os

# Twilio integration
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    st.sidebar.warning("⚠️ Install twilio package for SMS alerts: `pip install twilio`")

# Page configuration
st.set_page_config(
    page_title="Bounce Fleet Management Dashboard",
    page_icon="🛴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #2ed573 0%, #1e90ff 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .warning-card {
        background: linear-gradient(135deg, #ffa502 0%, #ff6348 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Generate sample data
@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    
    # Fleet data
    fleet_size = 500
    scooter_ids = [f"BNC{str(i).zfill(4)}" for i in range(1, fleet_size + 1)]
    
    # Hub locations (sample locations in major Indian cities)
    hubs = [
        {"name": "Koramangala Hub", "lat": 12.9279, "lon": 77.6271, "capacity": 50},
        {"name": "Whitefield Hub", "lat": 12.9698, "lon": 77.7500, "capacity": 40},
        {"name": "HSR Layout Hub", "lat": 12.9116, "lon": 77.6370, "capacity": 45},
        {"name": "Electronic City Hub", "lat": 12.8456, "lon": 77.6603, "capacity": 35},
        {"name": "Indiranagar Hub", "lat": 12.9784, "lon": 77.6408, "capacity": 30},
        {"name": "Jayanagar Hub", "lat": 12.9299, "lon": 77.5826, "capacity": 40},
        {"name": "Marathahalli Hub", "lat": 12.9592, "lon": 77.6974, "capacity": 25},
        {"name": "MG Road Hub", "lat": 12.9758, "lon": 77.6063, "capacity": 35},
        {"name": "Sarjapur Hub", "lat": 12.9010, "lon": 77.6934, "capacity": 30},
        {"name": "Bellandur Hub", "lat": 12.9256, "lon": 77.6733, "capacity": 40},
    ]
    
    # Generate scooter data
    scooters = []
    for i, scooter_id in enumerate(scooter_ids):
        hub = random.choice(hubs)
        status_weights = [0.6, 0.25, 0.10, 0.05]  # Available, On Trip, Maintenance, Alert
        status = np.random.choice(['Available', 'On Trip', 'Maintenance', 'Alert'], p=status_weights)
        
        # Add some location variance around hub
        lat_offset = np.random.normal(0, 0.01)
        lon_offset = np.random.normal(0, 0.01)
        
        scooter = {
            'scooter_id': scooter_id,
            'hub': hub['name'],
            'status': status,
            'battery_level': max(10, min(100, np.random.normal(75, 20))),
            'lat': hub['lat'] + lat_offset,
            'lon': hub['lon'] + lon_offset,
            'last_service': datetime.datetime.now() - timedelta(days=np.random.randint(1, 90)),
            'total_trips': np.random.randint(50, 500),
            'revenue_today': np.random.uniform(0, 150),
            'fault_reports': np.random.randint(0, 5),
            'uptime_percentage': np.random.uniform(85, 99)
        }
        scooters.append(scooter)
    
    df_scooters = pd.DataFrame(scooters)
    df_hubs = pd.DataFrame(hubs)
    
    # Generate trip data for time series
    dates = pd.date_range(start=datetime.datetime.now() - timedelta(days=30), 
                         end=datetime.datetime.now(), freq='D')
    trip_data = []
    for date in dates:
        daily_trips = np.random.randint(800, 1200)
        completed_trips = int(daily_trips * np.random.uniform(0.85, 0.98))
        revenue = daily_trips * np.random.uniform(25, 45)
        
        trip_data.append({
            'date': date,
            'total_trips': daily_trips,
            'completed_trips': completed_trips,
            'completion_rate': completed_trips / daily_trips * 100,
            'revenue': revenue,
            'avg_trip_duration': np.random.uniform(12, 25),
            'fleet_utilization': np.random.uniform(70, 90)
        })
    
    df_trips = pd.DataFrame(trip_data)
    
    return df_scooters, df_hubs, df_trips

# Load data
df_scooters, df_hubs, df_trips = generate_sample_data()

# Sidebar
st.sidebar.header("🛴 Fleet Control Center")
st.sidebar.markdown("---")

# Twilio Configuration Section
if TWILIO_AVAILABLE:
    st.sidebar.markdown("### 📱 SMS Alert Configuration")
    
    # Twilio credentials input
    with st.sidebar.expander("🔧 Twilio Settings", expanded=False):
        account_sid = st.text_input("Account SID", type="password", help="Your Twilio Account SID")
        auth_token = st.text_input("Auth Token", type="password", help="Your Twilio Auth Token")
        twilio_phone = st.text_input("Twilio Phone Number", help="Your Twilio phone number (e.g., +1234567890)")
        
        # Manager phone numbers
        st.markdown("**Fleet Manager Contacts:**")
        manager_phones = []
        for i in range(3):
            phone = st.text_input(f"Manager {i+1} Phone", key=f"manager_{i}", 
                                help="Include country code (e.g., +919876543210)")
            if phone:
                manager_phones.append(phone)
        
        # Store in session state
        if account_sid and auth_token:
            st.session_state.twilio_configured = True
            st.session_state.twilio_creds = {
                'account_sid': account_sid,
                'auth_token': auth_token,
                'phone_number': twilio_phone,
                'manager_phones': manager_phones
            }
        else:
            st.session_state.twilio_configured = False
    
    st.sidebar.markdown("---")

# Filters
selected_hubs = st.sidebar.multiselect(
    "Select Hubs",
    options=df_scooters['hub'].unique(),
    default=df_scooters['hub'].unique()[:3]
)

battery_threshold = st.sidebar.slider(
    "Low Battery Alert Threshold (%)",
    min_value=10,
    max_value=50,
    value=20
)

service_days = st.sidebar.slider(
    "Service Due Alert (days)",
    min_value=30,
    max_value=90,
    value=60
)

# Filter data
filtered_scooters = df_scooters[df_scooters['hub'].isin(selected_hubs)]

# Main Dashboard
st.title("🛴 Bounce Fleet Management Dashboard")
st.markdown("---")

# Key Metrics Row
col1, col2, col3, col4, col5 = st.columns(5)

total_fleet = len(filtered_scooters)
active_scooters = len(filtered_scooters[filtered_scooters['status'] == 'On Trip'])
available_scooters = len(filtered_scooters[filtered_scooters['status'] == 'Available'])
maintenance_scooters = len(filtered_scooters[filtered_scooters['status'] == 'Maintenance'])
utilization_rate = (active_scooters / total_fleet) * 100 if total_fleet > 0 else 0

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>Total Fleet</h3>
        <h1>{}</h1>
    </div>
    """.format(total_fleet), unsafe_allow_html=True)

with col2:
    color_class = "success-card" if utilization_rate >= 25 else "warning-card"
    st.markdown("""
    <div class="{}">
        <h3>Utilization Rate</h3>
        <h1>{:.1f}%</h1>
    </div>
    """.format(color_class, utilization_rate), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="success-card">
        <h3>Active Rides</h3>
        <h1>{}</h1>
    </div>
    """.format(active_scooters), unsafe_allow_html=True)

with col4:
    avg_revenue = filtered_scooters['revenue_today'].mean()
    st.markdown("""
    <div class="metric-card">
        <h3>Avg RPVPD</h3>
        <h1>₹{:.0f}</h1>
    </div>
    """.format(avg_revenue), unsafe_allow_html=True)

with col5:
    alerts_count = len(filtered_scooters[
        (filtered_scooters['battery_level'] < battery_threshold) | 
        (filtered_scooters['status'] == 'Alert')
    ])
    color_class = "alert-card" if alerts_count > 0 else "success-card"
    st.markdown("""
    <div class="{}">
        <h3>Active Alerts</h3>
        <h1>{}</h1>
    </div>
    """.format(color_class, alerts_count), unsafe_allow_html=True)

# Second row - Map and Fleet Status
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Fleet Map")
    
    # Create color mapping for status
    color_map = {
        'Available': 'green',
        'On Trip': 'blue',
        'Maintenance': 'orange',
        'Alert': 'red'
    }
    
    filtered_scooters['color'] = filtered_scooters['status'].map(color_map)
    
    fig_map = px.scatter_mapbox(
        filtered_scooters,
        lat='lat',
        lon='lon',
        color='status',
        color_discrete_map=color_map,
        hover_data=['scooter_id', 'battery_level', 'hub'],
        zoom=11,
        height=500,
        title="Real-time Scooter Locations"
    )
    
    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    st.subheader("📊 Fleet Status")
    
    status_counts = filtered_scooters['status'].value_counts()
    
    fig_donut = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        hole=0.6,
        marker_colors=['#2ed573', '#3742fa', '#ff9f43', '#ff3838']
    )])
    
    fig_donut.update_layout(
        title="Fleet Distribution",
        height=300,
        showlegend=True,
        annotations=[dict(text=f'{total_fleet}<br>Total', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    st.plotly_chart(fig_donut, use_container_width=True)
    
    # Hub Performance
    st.subheader("🏢 Hub Performance")
    hub_stats = filtered_scooters.groupby('hub').agg({
        'scooter_id': 'count',
        'uptime_percentage': 'mean',
        'revenue_today': 'sum'
    }).round(1)
    
    hub_stats.columns = ['Scooters', 'Uptime %', 'Revenue ₹']
    
    # Color code based on uptime
    def color_uptime(val):
        if val >= 95:
            return 'background-color: #2ed573; color: white'
        elif val >= 90:
            return 'background-color: #ff9f43; color: white'
        else:
            return 'background-color: #ff3838; color: white'
    
    styled_hub_stats = hub_stats.style.applymap(color_uptime, subset=['Uptime %'])
    st.dataframe(styled_hub_stats, use_container_width=True)

# Third row - Analytics and Alerts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Performance Trends")
    
    # Trip completion rate trend
    fig_trends = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Trip Completion Rate', 'Fleet Utilization'),
        vertical_spacing=0.1
    )
    
    fig_trends.add_trace(
        go.Scatter(
            x=df_trips['date'],
            y=df_trips['completion_rate'],
            mode='lines+markers',
            name='Completion Rate %',
            line=dict(color='#2ed573', width=3)
        ),
        row=1, col=1
    )
    
    fig_trends.add_trace(
        go.Scatter(
            x=df_trips['date'],
            y=df_trips['fleet_utilization'],
            mode='lines+markers',
            name='Utilization %',
            line=dict(color='#3742fa', width=3)
        ),
        row=2, col=1
    )
    
    fig_trends.update_layout(height=400, showlegend=False)
    fig_trends.update_xaxes(title_text="Date", row=2, col=1)
    fig_trends.update_yaxes(title_text="Completion %", row=1, col=1)
    fig_trends.update_yaxes(title_text="Utilization %", row=2, col=1)
    
    st.plotly_chart(fig_trends, use_container_width=True)

with col2:
    st.subheader("🚨 High-Risk Scooters")
    
    # Identify high-risk scooters
    high_risk = filtered_scooters[
        (filtered_scooters['battery_level'] < battery_threshold) |
        (filtered_scooters['fault_reports'] >= 3) |
        (filtered_scooters['uptime_percentage'] < 85) |
        ((datetime.datetime.now() - filtered_scooters['last_service']).dt.days > service_days)
    ].copy()
    
    if len(high_risk) > 0:
        # Add risk reasons
        high_risk['risk_reason'] = ''
        high_risk.loc[high_risk['battery_level'] < battery_threshold, 'risk_reason'] += 'Low Battery; '
        high_risk.loc[high_risk['fault_reports'] >= 3, 'risk_reason'] += 'Multiple Faults; '
        high_risk.loc[high_risk['uptime_percentage'] < 85, 'risk_reason'] += 'Low Uptime; '
        high_risk.loc[(datetime.datetime.now() - high_risk['last_service']).dt.days > service_days, 'risk_reason'] += 'Service Due; '
        
        high_risk_display = high_risk[['scooter_id', 'hub', 'battery_level', 'risk_reason']].head(10)
        high_risk_display.columns = ['Scooter ID', 'Hub', 'Battery %', 'Risk Factors']
        
        st.dataframe(high_risk_display, use_container_width=True, height=300)
        
        # Action buttons
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔧 Schedule Maintenance"):
                st.success("Maintenance scheduled for high-risk scooters!")
        with col_b:
            if st.button("🔋 Dispatch Swap Crew"):
                st.success("Swap crew dispatched for low battery scooters!")
    else:
        st.success("✅ No high-risk scooters detected!")

# Fourth row - Additional KPIs
st.markdown("---")
st.subheader("📊 Additional KPIs")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_trip_completion = df_trips['completion_rate'].mean()
    st.metric(
        label="Avg Trip Completion Rate",
        value=f"{avg_trip_completion:.1f}%",
        delta=f"{avg_trip_completion - 90:.1f}%" if avg_trip_completion >= 90 else f"{avg_trip_completion - 90:.1f}%"
    )

with col2:
    total_revenue = df_trips['revenue'].sum()
    st.metric(
        label="30-Day Revenue",
        value=f"₹{total_revenue:,.0f}",
        delta="12.5%"
    )

with col3:
    avg_uptime = filtered_scooters['uptime_percentage'].mean()
    st.metric(
        label="Fleet Avg Uptime",
        value=f"{avg_uptime:.1f}%",
        delta=f"{avg_uptime - 95:.1f}%" if avg_uptime >= 95 else f"{avg_uptime - 95:.1f}%"
    )

with col4:
    negative_balance_users = np.random.randint(15, 45)  # Sample data
    st.metric(
        label="Negative Balance Users",
        value=negative_balance_users,
        delta="-8" if negative_balance_users < 30 else "+5"
    )

# Auto-refresh functionality
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Bounce Fleet Management Dashboard | Last Updated: {} | 
    <span style='color: green;'>●</span> System Operational</p>
</div>
""".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

# Sidebar additional info
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Quick Actions")

# Export Report functionality
if st.sidebar.button("📊 Export Report"):
    # Create a comprehensive report
    report_data = {
        'Fleet Summary': {
            'Total Fleet Size': total_fleet,
            'Active Rides': active_scooters,
            'Utilization Rate (%)': round(utilization_rate, 2),
            'Average RPVPD (₹)': round(filtered_scooters['revenue_today'].mean(), 2),
            'Active Alerts': alerts_count
        },
        'Hub Performance': hub_stats.to_dict(),
        'High Risk Scooters': len(high_risk) if 'high_risk' in locals() else 0,
        'Generated At': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Convert to CSV format for download
    fleet_summary_df = pd.DataFrame([report_data['Fleet Summary']])
    csv_data = fleet_summary_df.to_csv(index=False)
    
    st.sidebar.download_button(
        label="💾 Download CSV Report",
        data=csv_data,
        file_name=f"bounce_fleet_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
    st.sidebar.success("✅ Report ready for download!")

# Send Alerts functionality with Twilio
if st.sidebar.button("📧 Send Alerts"):
    if 'high_risk' in locals() and len(high_risk) > 0:
        alert_summary = f"""
🚨 BOUNCE FLEET ALERT 🚨

High-Risk Scooters: {len(high_risk)}

Breakdown:
• Low Battery: {len(high_risk[high_risk['battery_level'] < battery_threshold])}
• High Fault Reports: {len(high_risk[high_risk['fault_reports'] >= 3])}
• Low Uptime: {len(high_risk[high_risk['uptime_percentage'] < 85])}
• Service Overdue: {len(high_risk[(datetime.datetime.now() - high_risk['last_service']).dt.days > service_days])}

Actions Required:
1. Dispatch battery swap crews
2. Schedule maintenance
3. Review hub distribution

Time: {datetime.datetime.now().strftime("%H:%M %d/%m/%Y")}
        """
        
        st.sidebar.text_area("Alert Message Preview:", alert_summary, height=200)
        
        # Twilio SMS Integration
        if TWILIO_AVAILABLE and hasattr(st.session_state, 'twilio_configured') and st.session_state.twilio_configured:
            creds = st.session_state.twilio_creds
            
            if st.sidebar.button("📱 Send SMS Alerts"):
                try:
                    # Initialize Twilio client
                    client = Client(creds['account_sid'], creds['auth_token'])
                    
                    sent_count = 0
                    failed_count = 0
                    
                    # Send SMS to each manager
                    for phone in creds['manager_phones']:
                        if phone:
                            try:
                                message = client.messages.create(
                                    body=alert_summary,
                                    from_=creds['phone_number'],
                                    to=phone
                                )
                                sent_count += 1
                                st.sidebar.success(f"✅ SMS sent to {phone[-4:]}")
                            except Exception as e:
                                failed_count += 1
                                st.sidebar.error(f"❌ Failed to send to {phone[-4:]}: {str(e)}")
                    
                    # Summary
                    if sent_count > 0:
                        st.sidebar.success(f"🚨 Alert sent to {sent_count} manager(s)!")
                    if failed_count > 0:
                        st.sidebar.warning(f"⚠️ {failed_count} message(s) failed to send")
                        
                except Exception as e:
                    st.sidebar.error(f"❌ Twilio Error: {str(e)}")
                    st.sidebar.info("💡 Check your Twilio credentials and phone numbers")
        
        elif TWILIO_AVAILABLE:
            st.sidebar.warning("⚠️ Configure Twilio credentials above to send SMS alerts")
        
        else:
            st.sidebar.info("📧 Alert summary generated! Install Twilio package for SMS functionality.")
    
    else:
        st.sidebar.info("✅ No alerts to send - all systems operational!")
        
        # Send "All Clear" message if configured
        if (TWILIO_AVAILABLE and hasattr(st.session_state, 'twilio_configured') 
            and st.session_state.twilio_configured):
            
            if st.sidebar.button("📱 Send All-Clear SMS"):
                creds = st.session_state.twilio_creds
                all_clear_msg = f"""
✅ BOUNCE FLEET STATUS: ALL CLEAR

Fleet Performance:
• Total Scooters: {total_fleet}
• Utilization: {utilization_rate:.1f}%
• Active Rides: {active_scooters}
• No high-risk alerts

System Status: OPERATIONAL
Time: {datetime.datetime.now().strftime("%H:%M %d/%m/%Y")}
                """
                
                try:
                    client = Client(creds['account_sid'], creds['auth_token'])
                    for phone in creds['manager_phones']:
                        if phone:
                            client.messages.create(
                                body=all_clear_msg,
                                from_=creds['phone_number'],
                                to=phone
                            )
                    st.sidebar.success("✅ All-clear notification sent!")
                except Exception as e:
                    st.sidebar.error(f"❌ Error: {str(e)}")

# Sync Fleet Data functionality
if st.sidebar.button("🔄 Sync Fleet Data"):
    with st.sidebar:
        # Show a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate data sync process
        import time
        for i in range(100):
            progress_bar.progress(i + 1)
            if i < 30:
                status_text.text('Connecting to fleet API...')
            elif i < 60:
                status_text.text('Fetching scooter locations...')
            elif i < 80:
                status_text.text('Updating battery status...')
            else:
                status_text.text('Finalizing sync...')
            time.sleep(0.02)  # Small delay for demonstration
        
        status_text.text('✅ Sync completed!')
        st.success("🔄 Fleet data synchronized successfully!")
        
        # Show sync summary
        st.info(f"""
        **Sync Summary:**
        • {total_fleet} scooters updated
        • {len(selected_hubs)} hubs synchronized  
        • Last sync: {datetime.datetime.now().strftime("%H:%M:%S")}
        """)
        
        # Auto-refresh the page after sync (in a real app, this would reload fresh data)
        if st.button("🔄 Refresh Dashboard"):
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ Dashboard Info")
st.sidebar.info("""
**Key Features:**
- Real-time fleet monitoring
- Interactive hub mapping  
- Performance analytics
- Risk identification
- Maintenance scheduling
- Revenue tracking
- SMS alert integration

**Refresh Rate:** Every 5 minutes
**Coverage:** All active hubs

**SMS Setup:**
1. Get Twilio credentials from console.twilio.com
2. Configure settings above
3. Add manager phone numbers
4. Test alerts with sample data
""")