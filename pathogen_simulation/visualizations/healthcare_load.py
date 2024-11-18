# Healthcare system visualization
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

def initialize_healthcare_params():
    """Initialize healthcare parameters in session state if they don't exist"""
    if 'healthcare_params' not in st.session_state:
        st.session_state.healthcare_params = {
            'hospital_beds': 28.0,  # per 10k population
            'icu_beds': 3.5,     # per 10k population
            'ventilators': 2.0,     # per 10k population
            'transmission_rate': 5.0,  # base transmission rate percentage
        }

def load_country_data():
    """Load and process country data from CSV"""
    df = pd.read_csv('data/country_data.csv')
    
    # Calculate world totals and averages
    world_data = {
        'country': 'World',
        'continent': 'Global',
        'population': df['population'].sum(),
        'population_density': df['population_density'].mean(),
        'air_quality_index': df['air_quality_index'].mean(),
        'water_quality_index': df['water_quality_index'].mean(),
        'age_distribution_young': df['age_distribution_young'].mean(),
        'age_distribution_adult': df['age_distribution_adult'].mean(),
        'age_distribution_elderly': df['age_distribution_elderly'].mean(),
        'gender_ratio': df['gender_ratio'].mean(),
        'health_conditions_percentage': df['health_conditions_percentage'].mean()
    }
    
    # Add world data to the dataframe
    df = pd.concat([df, pd.DataFrame([world_data])], ignore_index=True)
    return df

def display_vaccination_params():
    """Display vaccination program parameters"""
    with st.sidebar.expander("Vaccination Parameters", expanded=False):
        # Show current vaccines
        if st.session_state.vaccination_params['vaccines']:
            st.write("Current Vaccines:")
            vaccines_to_remove = []
            for idx, vaccine in enumerate(st.session_state.vaccination_params['vaccines']):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{vaccine['name']}**")
                with col2:
                    if st.button("Remove", key=f"remove_vaccine_{idx}"):
                        vaccines_to_remove.append(idx)
            
            # Remove vaccines (if any) after the loop
            for idx in reversed(vaccines_to_remove):
                st.session_state.vaccination_params['vaccines'].pop(idx)
                st.rerun()

        # Add new vaccine interface
        if st.checkbox("Add New Vaccine"):
            new_vaccine = {
                'name': st.text_input(
                    "Vaccine Name", 
                    value=f"Vaccine {len(st.session_state.vaccination_params['vaccines']) + 1}"
                ),
                'population_vaccinated': st.number_input(
                    "Population Vaccinated (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=0.0,
                    step=0.1
                ),
                'effectiveness': st.number_input(
                    "Effectiveness Against Infection (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=95.0,
                    step=0.1
                ),
                'waning_immunity_rate': st.number_input(
                    "Monthly Waning Rate (%)", 
                    min_value=0.0, 
                    max_value=100.0, 
                    value=5.0,
                    step=0.1
                )
            }
            
            # Store the new vaccine in session state
            if not any(v['name'] == new_vaccine['name'] 
                      for v in st.session_state.vaccination_params['vaccines']):
                st.session_state.vaccination_params['vaccines'].append(new_vaccine)

        # Display total number of vaccines
        st.metric(
            "Total Vaccines",
            len(st.session_state.vaccination_params['vaccines'])
        )

def calculate_healthcare_metrics(params: dict, vaccination_params: dict, country_info: pd.Series, days: int = 30):
    """
    Calculate healthcare system load metrics over time with vaccination impact
    
    Mathematical Model:
    
    1. Base Parameters:
       - R₀: Basic reproduction number = transmission_rate / 100
       - D: Population density factor = min(1.5, max(0.5, population_density / 500))
       - H: Health conditions factor = min(1.5, max(0.5, health_conditions_percentage / 25))
    
    2. Vaccination Impact:
       For each vaccine i:
       - V_effi: Vaccine effectiveness (%)
       - V_popi: Vaccinated population (%)
       - V_wanei: Waning immunity rate (% per month)
       
       Total Vaccination Effect = Σ(V_effi × V_popi × (1 - V_wanei)) / 100
       Vaccination Protection = min(0.95, Total Vaccination Effect / 100)
    
    3. Adjusted Transmission Rate:
       R_eff = R₀ × D × H × (1 - Vaccination Protection)
    
    4. Disease Progression:
       - Daily Recovery Rate (γ) = 0.1 (10%)
       - Base Severity Rate (σ) = 0.15 × H
       - Adjusted Severity Rate = σ × (1 - Vaccination Protection × 0.7)
       
       New Cases(t) = Current Cases × (1 + R_eff - γ)
    
    5. Healthcare Resource Requirements:
       - ICU Rate = 0.30 × (1 - Vaccination Protection × 0.8)
       - Ventilator Rate = 0.15 × (1 - Vaccination Protection × 0.8)
       
       For each time t:
       - Required Beds = Severe Cases(t) = New Cases(t) × Adjusted Severity Rate
       - Required ICU = Severe Cases(t) × ICU Rate
       - Required Ventilators = Severe Cases(t) × Ventilator Rate
    """
    population = country_info['population'] / 100000  # Convert to per 100k units
    
    # Initialize time series data
    dates = [datetime.now() + timedelta(days=x) for x in range(days)]
    metrics = {
        'date': dates,
        'available_beds': [params['hospital_beds'] * (population/100)] * days,
        'available_icu': [params['icu_beds'] * (population/100)] * days,
        'available_ventilators': [params['ventilators'] * (population/100)] * days
    }
    
    # Calculate vaccination impact
    total_vaccination_effect = 0.0
    if vaccination_params['vaccines']:
        for vaccine in vaccination_params['vaccines']:
            # Calculate reduction in transmission based on vaccine effectiveness and coverage
            protection_factor = (
                vaccine['effectiveness'] * 
                vaccine['population_vaccinated'] / 100 * 
                (1 - vaccine['waning_immunity_rate'] / 100)
            )
            total_vaccination_effect += protection_factor
    
    # Adjust transmission rate based on vaccination and other factors
    base_transmission = params['transmission_rate'] / 100
    density_factor = min(1.5, max(0.5, country_info['population_density'] / 500))
    health_factor = min(1.5, max(0.5, country_info['health_conditions_percentage'] / 25))
    
    # Reduce transmission based on vaccination effect (capped at 95% reduction)
    vaccination_reduction = min(0.95, total_vaccination_effect / 100)
    adjusted_transmission = base_transmission * density_factor * health_factor * (1 - vaccination_reduction)
    
    # Calculate resource requirements over time
    recovery_rate = 0.1  # 10% daily recovery rate
    severity_rate = 0.15 * health_factor * (1 - vaccination_reduction * 0.7)  # Vaccines reduce severity
    icu_rate = 0.30 * (1 - vaccination_reduction * 0.8)  # Vaccines reduce ICU needs
    ventilator_rate = 0.15 * (1 - vaccination_reduction * 0.8)  # Vaccines reduce ventilator needs
    
    active_cases = []
    current_cases = population * adjusted_transmission
    
    for _ in range(days):
        current_cases = current_cases * (1 + adjusted_transmission - recovery_rate)
        active_cases.append(current_cases)
    
    # Calculate required resources
    severe_cases = [case * severity_rate for case in active_cases]
    metrics['required_beds'] = severe_cases
    metrics['required_icu'] = [case * icu_rate for case in severe_cases]
    metrics['required_ventilators'] = [case * ventilator_rate for case in severe_cases]
    
    return pd.DataFrame(metrics)

def display_healthcare_load():
    """Display healthcare system load visualization with vaccination impact"""
    st.header("Healthcare System Load")
    
    # Initialize healthcare parameters
    initialize_healthcare_params()
    
    # Create sidebar for parameter controls
    st.sidebar.header("Healthcare System Parameters")
    
    # Add parameter controls in sidebar
    st.session_state.healthcare_params.update({
        'hospital_beds': st.sidebar.slider(
            "Hospital Beds (per 10k population)",
            min_value=0.0,
            max_value=50.0,
            value=float(st.session_state.healthcare_params.get('hospital_beds', 28.0)),
            step=0.1
        ),
        'icu_beds': st.sidebar.slider(
            "ICU Beds (per 10k population)",
            min_value=0.0,
            max_value=10.0,
            value=float(st.session_state.healthcare_params.get('icu_beds', 3.5)),
            step=0.1
        ),
        'ventilators': st.sidebar.slider(
            "Ventilators (per 10k population)",
            min_value=0.0,
            max_value=5.0,
            value=float(st.session_state.healthcare_params.get('ventilators', 2.0)),
            step=0.1
        ),
        'transmission_rate': st.sidebar.slider(
            "Base Transmission Rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=float(st.session_state.healthcare_params.get('transmission_rate', 5.0)),
            step=0.1
        )
    })
    
    # Load country data
    country_df = load_country_data()
    
    # Add continent/country selection
    continents = ['All'] + sorted(country_df['continent'].unique().tolist())
    selected_continent = st.selectbox("Select Continent", continents)
    
    # Filter countries by continent
    filtered_df = country_df if selected_continent == 'All' else country_df[
        (country_df['continent'] == selected_continent) | (country_df['country'] == 'World')
    ]
    
    selected_country = st.selectbox(
        "Select Country",
        filtered_df['country'].tolist(),
        index=filtered_df['country'].tolist().index('World')
    )
    
    # Time range selection
    projection_days = st.slider("Projection Days", 7, 90, 30)
    
    # Get country information
    country_info = country_df[country_df['country'] == selected_country].iloc[0]
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Healthcare Load", "Vaccination Impact"])
    
    # Calculate metrics with vaccination impact
    metrics_df = calculate_healthcare_metrics(
        st.session_state.healthcare_params,
        st.session_state.vaccination_params,
        country_info,
        projection_days
    )
    
    with tab1:
        # Create line graph for healthcare load
        fig_load = go.Figure()
        
        # Add hospital bed lines
        fig_load.add_trace(go.Scatter(
            x=metrics_df['date'], y=metrics_df['available_beds'],
            name='Hospital Bed Capacity',
            line=dict(color='blue', dash='dash')
        ))
        fig_load.add_trace(go.Scatter(
            x=metrics_df['date'], y=metrics_df['required_beds'],
            name='Hospital Bed Usage',
            line=dict(color='blue')
        ))
        
        # Add ICU bed lines
        fig_load.add_trace(go.Scatter(
            x=metrics_df['date'], y=metrics_df['available_icu'],
            name='ICU Bed Capacity',
            line=dict(color='red', dash='dash')
        ))
        fig_load.add_trace(go.Scatter(
            x=metrics_df['date'], y=metrics_df['required_icu'],
            name='ICU Bed Usage',
            line=dict(color='red')
        ))
        
        # Add ventilator lines
        fig_load.add_trace(go.Scatter(
            x=metrics_df['date'], y=metrics_df['available_ventilators'],
            name='Ventilator Capacity',
            line=dict(color='green', dash='dash')
        ))
        fig_load.add_trace(go.Scatter(
            x=metrics_df['date'], y=metrics_df['required_ventilators'],
            name='Ventilator Usage',
            line=dict(color='green')
        ))
        
        fig_load.update_layout(
            title=f"Healthcare System Load Over Time - {selected_country}",
            xaxis_title="Date",
            yaxis_title="Number of Units",
            hovermode='x unified',
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig_load, use_container_width=True)
    
    with tab2:
        # Debug information at the top of the tab
        st.write("Debug: Checking vaccination data...")
        st.write(f"Vaccines in session state: {len(st.session_state.vaccination_params.get('vaccines', []))}")
        
        # Ensure we're getting the latest data
        current_vaccines = st.session_state.vaccination_params.get('vaccines', [])
        
        if current_vaccines:
            st.write(f"Found {len(current_vaccines)} vaccines")
            # Create DataFrame from current vaccine data
            vaccines_df = pd.DataFrame(current_vaccines)
            
            # Main vaccination metrics chart
            fig_vac = go.Figure()
            
            # Add bars for population coverage and effectiveness
            fig_vac.add_trace(go.Bar(
                x=vaccines_df['name'],
                y=vaccines_df['population_vaccinated'],
                name='Population Coverage',
                marker_color='rgb(49, 130, 189)'
            ))
            
            fig_vac.add_trace(go.Bar(
                x=vaccines_df['name'],
                y=vaccines_df['effectiveness'],
                name='Vaccine Effectiveness',
                marker_color='rgb(204, 204, 204)'
            ))
            
            # Add waning immunity rate as a line
            fig_vac.add_trace(go.Scatter(
                x=vaccines_df['name'],
                y=vaccines_df['waning_immunity_rate'],
                name='Monthly Waning Rate',
                mode='lines+markers',
                line=dict(color='rgb(255, 127, 14)'),
                yaxis='y2'
            ))
            
            # Update layout with dual y-axes
            fig_vac.update_layout(
                title="Vaccination Program Metrics",
                xaxis_title="Vaccine",
                yaxis_title="Percentage (%)",
                yaxis2=dict(
                    title="Monthly Waning Rate (%)",
                    overlaying='y',
                    side='right'
                ),
                barmode='group',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_vac, use_container_width=True)
            
            # Calculate and display impact metrics
            col1, col2, col3 = st.columns(3)
            
            # Calculate total coverage considering effectiveness and waning
            effective_coverage = sum(
                row['population_vaccinated'] * 
                row['effectiveness'] * 
                (1 - row['waning_immunity_rate']/100) 
                for _, row in vaccines_df.iterrows()
            ) / 100  # Convert to percentage
            
            with col1:
                st.metric(
                    "Average Population Coverage",
                    f"{vaccines_df['population_vaccinated'].mean():.1f}%",
                    help="Average percentage of population covered by vaccines"
                )
            
            with col2:
                st.metric(
                    "Average Vaccine Effectiveness",
                    f"{vaccines_df['effectiveness'].mean():.1f}%",
                    help="Average effectiveness of all vaccines"
                )
            
            with col3:
                st.metric(
                    "Effective Protection Level",
                    f"{effective_coverage:.1f}%",
                    help="Total population protection considering coverage, effectiveness, and waning immunity"
                )
            
            # Display resource reduction metrics
            st.subheader("Projected Impact on Healthcare Resources")
            impact_cols = st.columns(3)
            
            # Calculate average reduction in resource needs
            bed_reduction = (1 - metrics_df['required_beds'].mean() / 
                           (metrics_df['available_beds'].mean() * 2)) * 100
            icu_reduction = (1 - metrics_df['required_icu'].mean() / 
                           (metrics_df['available_icu'].mean() * 2)) * 100
            vent_reduction = (1 - metrics_df['required_ventilators'].mean() / 
                            (metrics_df['available_ventilators'].mean() * 2)) * 100
            
            with impact_cols[0]:
                st.metric(
                    "Hospital Bed Need Reduction",
                    f"{max(0, bed_reduction):.1f}%",
                    help="Estimated reduction in hospital bed requirements due to vaccination"
                )
            
            with impact_cols[1]:
                st.metric(
                    "ICU Need Reduction",
                    f"{max(0, icu_reduction):.1f}%",
                    help="Estimated reduction in ICU bed requirements due to vaccination"
                )
            
            with impact_cols[2]:
                st.metric(
                    "Ventilator Need Reduction",
                    f"{max(0, vent_reduction):.1f}%",
                    help="Estimated reduction in ventilator requirements due to vaccination"
                )
            
        else:
            st.info("No vaccination data available. Add vaccines in the sidebar parameters to see their impact.")
            st.write("To add a vaccine:")
            st.write("1. Expand the 'Vaccination Parameters' section in the sidebar")
            st.write("2. Check the 'Add New Vaccine' box")
            st.write("3. Enter the vaccine details")
            st.write("4. Click 'Update Visualization' to see the impact")
    
    # Display country statistics
    st.subheader("Country Statistics")
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("Population", f"{country_info['population']:,.0f}")
    with cols[1]:
        st.metric("Population Density", f"{country_info['population_density']:.1f}")
    with cols[2]:
        st.metric("Health Conditions %", f"{country_info['health_conditions_percentage']:.1f}%")
    with cols[3]:
        st.metric("Elderly Population %", f"{country_info['age_distribution_elderly']:.1f}%")


# HEALTHCARE LOAD MATHEMATICAL EXPLANATIONS

"""
1. Resource Requirements Calculation

Base Resource Need per Infected Person:
--------------------------------------
For each infected person (I), base resource requirements are:

Hospital Bed Need = I * h
where:
- I = number of infected cases
- h = hospitalization rate (typically 15-20% of active cases)

ICU Bed Need = I * i
where:
- i = ICU rate (typically 3-5% of active cases)

Ventilator Need = I * v
where:
- v = ventilation rate (typically 1-2% of active cases)

2. Resource Utilization Rate

For each resource type:
Utilization Rate = (Current Usage / Total Capacity) * 100

where:
- Current Usage = Resources currently in use
- Total Capacity = Total available resources per 10,000 population, scaled to total population

Example for hospital beds:
Total Bed Capacity = (beds_per_10k / 10000) * total_population
Utilization % = (beds_in_use / Total Bed Capacity) * 100

3. Healthcare Worker Load

Healthcare Worker Strain = (Patients / HCW_Ratio)
where:
- Patients = Current hospitalized cases
- HCW_Ratio = Standard healthcare worker to patient ratio (varies by department)

4. Medical Supply Consumption

Daily Supply Usage = Base_Rate * Severity_Multiplier * Active_Cases
where:
- Base_Rate = Standard daily supply use per patient
- Severity_Multiplier = Adjustment based on disease severity (1-3x)

PPE Consumption Rate = HCW * PPE_Sets * Shifts
where:
- HCW = Number of active healthcare workers
- PPE_Sets = Sets of PPE needed per worker per shift (typically 2-4)
- Shifts = Number of shifts per day

5. Resource Strain Indicators

Critical Threshold Calculation:
Strain Level = (Current_Load / Maximum_Capacity) * 100

Categorization:
- Normal: < 75% capacity
- Warning: 75-90% capacity
- Critical: > 90% capacity

6. Testing Capacity Utilization

Daily Testing Capacity = Tests_per_10k * (Population / 10000)
Testing Backlog = Daily_Test_Demand - Daily_Testing_Capacity

Effective Testing Rate = (Completed_Tests / Test_Demand) * 100

7. Medication and Vaccine Stock Calculations

Medication Stock Adequacy = Current_Stock / (Daily_Usage * Planning_Horizon)
where:
- Current_Stock = Available medication units
- Daily_Usage = Units used per patient per day
- Planning_Horizon = Number of days to plan for (typically 30-90)

Vaccination Capacity:
Daily Vaccination Rate = min(Available_Doses, Administration_Capacity)
where:
- Available_Doses = Vaccine stock available
- Administration_Capacity = Healthcare system's daily vaccination capability

8. System Overload Probability

Risk of Overload = f(Current_Load, Growth_Rate, Capacity)
where f is typically a logistic function:
P(overload) = 1 / (1 + e^(-k(x - x0)))
where:
- k = steepness parameter
- x = current load ratio
- x0 = critical threshold

9. Healthcare Budget Impact

Daily Cost = Σ(Resource_Usage_i * Cost_per_Unit_i)
where:
- Resource_Usage_i = Usage of resource type i
- Cost_per_Unit_i = Cost per unit of resource type i

Budget Depletion Rate = Daily_Cost / Available_Budget

10. Healthcare Quality Metrics

Quality of Care Index = Base_Quality * (1 - System_Strain)
where:
- Base_Quality = Standard quality score (typically 1.0)
- System_Strain = Current load / Maximum capacity

"""