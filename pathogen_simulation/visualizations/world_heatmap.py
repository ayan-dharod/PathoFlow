import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def load_country_coordinates():
    """Load country coordinates mapping"""
    return {
        'China': (35.8617, 104.1954),
        'India': (20.5937, 78.9629),
        'United States': (37.0902, -95.7129),
        'Indonesia': (-0.7893, 113.9213),
        'Pakistan': (30.3753, 69.3451),
        'Brazil': (-14.2350, -51.9253),
        'Nigeria': (9.0820, 8.6753),
        'Bangladesh': (23.6850, 90.3563),
        'Russia': (61.5240, 105.3188),
        'Mexico': (23.6345, -102.5528),
        'Japan': (36.2048, 138.2529),
        'Ethiopia': (9.1450, 40.4897),
        'Philippines': (12.8797, 121.7740),
        'Egypt': (26.8206, 30.8025),
        'Vietnam': (14.0583, 108.2772),
        'DR Congo': (-4.0383, 21.7587),
        'Turkey': (38.9637, 35.2433),
        'Iran': (32.4279, 53.6880),
        'Germany': (51.1657, 10.4515),
        'Thailand': (15.8700, 100.9925),
        'United Kingdom': (55.3781, -3.4360),
        'France': (46.2276, 2.2137),
        'Italy': (41.8719, 12.5674),
        'South Africa': (-30.5595, 22.9375),
        'Tanzania': (-6.3690, 34.8888),
        'Myanmar': (21.9162, 95.9560),
        'South Korea': (35.9078, 127.7669),
        'Colombia': (4.5709, -74.2973),
        'Kenya': (-0.0236, 37.9062),
        'Spain': (40.4637, -3.7492),
        'Argentina': (-38.4161, -63.6167),
        'Algeria': (28.0339, 1.6596),
        'Sudan': (12.8628, 30.2176),
        'Uganda': (1.3733, 32.2903),
        'Iraq': (33.2232, 43.6793),
        'Poland': (51.9194, 19.1451),
        'Canada': (56.1304, -106.3468),
        'Morocco': (31.7917, -7.0926),
        'Saudi Arabia': (23.8859, 45.0792),
        'Uzbekistan': (41.3775, 64.5853),
        'Malaysia': (4.2105, 101.9758),
        'Peru': (-9.1900, -75.0152),
        'Afghanistan': (33.9391, 67.7100),
        'Venezuela': (6.4238, -66.5897),
        'Ghana': (7.9465, -1.0232),
        'Angola': (-11.2027, 17.8739),
        'Nepal': (28.3949, 84.1240),
        'Yemen': (15.5527, 48.5164),
        'North Korea': (40.3399, 127.5101),
        'Australia': (-25.2744, 133.7751)
    }

def display_country_rankings(data: pd.DataFrame, metric_option: str, variants: list):
    """
    Display ranked country data based on selected metric
    
    Parameters:
    -----------
    data: DataFrame with country data
    metric_option: Metric to sort by (Total Cases, Severity Index, or Variant Distribution)
    variants: List of variant dictionaries
    """
    if metric_option == 'Total Cases':
        # Sort by total active cases
        sorted_data = data.sort_values('active_cases', ascending=False)
        
        # Display top 10 countries
        for idx, row in sorted_data.head(10).iterrows():
            st.metric(
                row['country'],
                f"{row['active_cases']:,} cases",
                delta=f"Rate: {row['infection_rate']:.2%}"
            )
    
    elif metric_option == 'Severity Index':
        # Sort by severity index
        sorted_data = data.sort_values('severity_index', ascending=False)
        
        # Display top 10 countries
        for idx, row in sorted_data.head(10).iterrows():
            st.metric(
                row['country'],
                f"Severity: {row['severity_index']:.2f}",
                delta=f"Cases: {row['active_cases']:,}"
            )
    
    elif metric_option == 'Variant Distribution':
        if not variants:
            st.warning("No variants have been added to analyze distribution.")
            return
            
        # Create tabs for each variant
        tabs = st.tabs([v['name'] for v in variants])
        
        for tab, variant in zip(tabs, variants):
            with tab:
                # Sort by variant-specific cases
                variant_col = f"{variant['name']}_cases"
                sorted_data = data.sort_values(variant_col, ascending=False)
                
                # Display top 10 countries for this variant
                for idx, row in sorted_data.head(10).iterrows():
                    variant_percentage = (row[variant_col] / row['active_cases'] * 100 
                                       if row['active_cases'] > 0 else 0)
                    st.metric(
                        row['country'],
                        f"{row[variant_col]:,} cases",
                        delta=f"{variant_percentage:.1f}% of total"
                    )
                
                # Add variant details
                st.write("Variant Details:")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Severity: {variant['severity']}/10")
                    st.write(f"Mortality: {variant['mortality_rate']}%")
                with col2:
                    st.write(f"Recovery: {variant['recovery_rate']}%")
                    if 'vaccine_effectiveness' in variant:
                        st.write(f"Vaccine Effectiveness: {variant['vaccine_effectiveness']}%")

    # Add download button for full data
    csv = convert_to_downloadable_csv(data, metric_option, variants)
    st.download_button(
        label="Download Full Rankings",
        data=csv,
        file_name=f"country_rankings_{metric_option.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )

def convert_to_downloadable_csv(data: pd.DataFrame, metric_option: str, variants: list) -> str:
    """
    Convert the ranking data to a downloadable CSV format
    
    Parameters:
    -----------
    data: DataFrame with country data
    metric_option: Selected metric for sorting
    variants: List of variant dictionaries
    
    Returns:
    --------
    str: CSV string of the data
    """
    # Select relevant columns based on metric
    if metric_option == 'Total Cases':
        cols = ['country', 'active_cases', 'infection_rate', 'severity_index']
    elif metric_option == 'Severity Index':
        cols = ['country', 'severity_index', 'active_cases', 'infection_rate']
    elif metric_option == 'Variant Distribution':
        variant_cols = [f"{v['name']}_cases" for v in variants]
        cols = ['country', 'active_cases', 'infection_rate', 'severity_index'] + variant_cols
    
    # Create export dataframe
    export_df = data[cols].copy()
    
    # Sort based on metric
    if metric_option == 'Total Cases':
        export_df = export_df.sort_values('active_cases', ascending=False)
    elif metric_option == 'Severity Index':
        export_df = export_df.sort_values('severity_index', ascending=False)
    elif metric_option == 'Variant Distribution' and variants:
        export_df = export_df.sort_values(f"{variants[0]['name']}_cases", ascending=False)
    
    return export_df.to_csv(index=False)

def calculate_variant_impact(variants: list, base_transmission: float) -> float:
    """
    Calculate the combined impact of all variants on transmission
    
    Mathematical Model:
    ------------------
    For each variant i:
    Impact_i = (Cases_i/1000) * (Severity_i/10) * (Mortality_i/100) * (1 - Recovery_i/100)
    
    Combined Impact = Σ(Impact_i * Weight_i)
    where Weight_i is based on variant prevalence
    
    Final Transmission = Base_Rate * (1 + Combined_Impact)
    """
    if not variants:
        return base_transmission
    
    total_impact = 0
    total_cases = sum(v['daily_cases'] for v in variants)
    
    for variant in variants:
        # Calculate relative prevalence of this variant
        prevalence = variant['daily_cases'] / total_cases if total_cases > 0 else 0
        
        # Calculate variant's individual impact
        variant_impact = (
            (variant['daily_cases'] / 1000) *  # Normalized case rate
            (variant['severity'] / 10) *        # Normalized severity
            (variant['mortality_rate'] / 100) * # Mortality contribution
            (1 - variant['recovery_rate'] / 100) # Recovery rate impact
        )
        
        # Add weighted impact to total
        total_impact += variant_impact * prevalence
    
    # Return adjusted transmission rate
    return base_transmission * (1 + total_impact)

def calculate_vaccine_effectiveness(variants: list, vaccination_params: dict) -> float:
    """
    Calculate overall vaccine effectiveness considering variants
    
    Mathematical Model:
    ------------------
    For each variant i:
    Effectiveness_i = Base_Effectiveness * Variant_Specific_Effectiveness_i
    
    Overall_Effectiveness = Σ(Effectiveness_i * Variant_Prevalence_i)
    """
    if not variants or not vaccination_params['vaccines']:
        return 0
    
    total_effectiveness = 0
    total_cases = sum(v['daily_cases'] for v in variants)
    
    for variant in variants:
        # Calculate variant's prevalence
        prevalence = variant['daily_cases'] / total_cases if total_cases > 0 else 0
        
        # Average vaccine effectiveness against this variant
        variant_vaccine_effectiveness = variant['vaccine_effectiveness'] / 100
        
        total_effectiveness += variant_vaccine_effectiveness * prevalence
    
    return total_effectiveness

def calculate_global_spread(params: dict, countries_data: pd.DataFrame, variants: list = None, vaccination_params: dict = None):
    """
    Calculate disease spread across different countries based on parameters
    
    Mathematical Model:
    ------------------
    Risk Score = w1*PD + w2*AQ + w3*WQ + w4*HC
    where:
    - PD = Normalized Population Density
    - AQ = Normalized Air Quality Impact
    - WQ = Normalized Water Quality Impact
    - HC = Normalized Health Conditions
    
    Variant-Adjusted Transmission = Base_Rate * Variant_Impact
    
    Final Infection Rate = Risk_Score * Adjusted_Transmission * (1 - Vaccine_Protection)
    """
    # Calculate base risk factors
    countries_data['risk_score'] = (
        0.3 * (countries_data['population_density'] / countries_data['population_density'].max()) +
        0.2 * (countries_data['air_quality_index'] / countries_data['air_quality_index'].max()) +
        0.2 * (countries_data['water_quality_index'] / countries_data['water_quality_index'].max()) +
        0.3 * (countries_data['health_conditions_percentage'] / countries_data['health_conditions_percentage'].max())
    )
    
    # Calculate variant-adjusted transmission rate
    adjusted_transmission = calculate_variant_impact(variants, params['transmission_rate'])
    
    # Calculate vaccine effectiveness
    vaccine_protection = calculate_vaccine_effectiveness(variants, vaccination_params)
    
    # Calculate infection rate with all factors
    countries_data['infection_rate'] = (
        countries_data['risk_score'] * 
        (adjusted_transmission / 100) *
        (1 - vaccine_protection) *
        (1 + params['mutation_rate'] / 100)
    )
    
    # Add variant-specific calculations
    if variants:
        for variant in variants:
            variant_name = variant['name']
            # Calculate variant-specific spread
            countries_data[f'{variant_name}_cases'] = np.floor(
                countries_data['population'] * 
                countries_data['infection_rate'] * 
                (variant['daily_cases'] / 1000) *
                (variant['severity'] / 10)
            ).astype(int)
    
    # Calculate total active cases
    countries_data['active_cases'] = np.floor(
        countries_data['population'] * 
        countries_data['infection_rate']
    ).astype(int)
    
    # Calculate severity index
    countries_data['severity_index'] = calculate_severity_index(countries_data, variants if variants else [])
    
    return countries_data

def calculate_severity_index(data: pd.DataFrame, variants: list) -> pd.Series:
    """
    Calculate severity index for each country based on variants present
    
    Mathematical Model:
    ------------------
    Severity_Index = Base_Severity * Σ(Variant_Severity_i * Prevalence_i)
    
    where Base_Severity is derived from:
    - Population density impact
    - Healthcare system capacity
    - Existing health conditions
    """
    base_severity = (
        0.4 * (data['population_density'] / data['population_density'].max()) +
        0.3 * (data['health_conditions_percentage'] / data['health_conditions_percentage'].max()) +
        0.3 * (data['infection_rate'])
    )
    
    if not variants:
        return base_severity
    
    # Add variant impact to severity
    variant_severity = sum(
        v['severity'] / 10 * (v['daily_cases'] / 1000)
        for v in variants
    )
    
    return base_severity * (1 + variant_severity)

def display_global_map():
    st.header("Global Disease Spread Visualization")
    
    # Load and prepare data
    countries_data = pd.read_csv('data/country_data.csv')
    variants = st.session_state.variants if 'variants' in st.session_state else []
    vaccination_params = st.session_state.vaccination_params if 'vaccination_params' in st.session_state else {}
    
    # Add coordinates
    coordinates = load_country_coordinates()
    countries_data['latitude'] = countries_data['country'].map(lambda x: coordinates.get(x, (0,0))[0])
    countries_data['longitude'] = countries_data['country'].map(lambda x: coordinates.get(x, (0,0))[1])
    
    # Calculate spread with variants
    spread_data = calculate_global_spread(
        st.session_state.pathogen_params,
        countries_data,
        variants,
        vaccination_params
    )
    
    # Create visualization
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Create map with variant information
        fig = create_map_visualization(spread_data, variants)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        display_variant_analysis(spread_data, variants)

def display_variant_params():
    """Display variant input section with removal option"""
    with st.expander("Variant Parameters", expanded=False):
        # Show current variants
        if st.session_state.variants:
            st.write("Current Variants:")
            for idx, variant in enumerate(st.session_state.variants):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{variant['name']}**")
                with col2:
                    if st.button(f"Remove", key=f"remove_{idx}"):
                        st.session_state.variants.pop(idx)
                        st.rerun()

        # Option to reset all variants
        if st.session_state.variants and st.button("Remove All Variants"):
            st.session_state.variants = []
            st.rerun()
        
        # Add new variant option
        if st.checkbox("Add New Variant"):
            variant = {
                'name': st.text_input("Variant Name", value=f"Variant {len(st.session_state.variants) + 1}"),
                'daily_cases': st.number_input("Cases per 1,000 people", min_value=0.0, step=0.1),
                'severity': st.slider("Severity of Symptoms", 1, 10, 5),
                'mortality_rate': st.number_input("Mortality Rate (%)", 0.0, 100.0, step=0.1),
                'recovery_rate': st.number_input("Recovery Rate (%)", 0.0, 100.0, step=0.1),
                'vaccine_effectiveness': st.number_input("Vaccine Effectiveness (%)", 0.0, 100.0, step=0.1)
            }
            if st.button("Add Variant"):
                if not any(v['name'] == variant['name'] for v in st.session_state.variants):
                    st.session_state.variants.append(variant)
                    st.rerun()

def calculate_severity_index(data: pd.DataFrame, variants: list) -> pd.Series:
    """
    Calculate severity index for each country based on variants present
    
    Mathematical Model:
    ------------------
    Severity_Index = Base_Severity * (1 + Variant_Impact)
    where:
    Base_Severity = (0.4 * PD + 0.3 * HC + 0.3 * IR)
    PD = Normalized Population Density
    HC = Normalized Health Conditions
    IR = Infection Rate
    """
    # Calculate base severity (0-1 scale)
    base_severity = (
        0.4 * (data['population_density'] / data['population_density'].max()) +
        0.3 * (data['health_conditions_percentage'] / 100) +
        0.3 * data['infection_rate']
    ).clip(0, 1)  # Ensure values are between 0 and 1
    
    if not variants:
        return base_severity * 10  # Scale to 0-10 range
    
    # Calculate variant impact (additive)
    variant_impact = sum(
        (v['severity'] / 10) * (v['daily_cases'] / 1000)
        for v in variants
    )
    
    # Combine base severity with variant impact
    final_severity = (base_severity * (1 + variant_impact)).clip(0, 1)
    
    # Scale to 0-10 range for better visualization
    return final_severity * 10

def create_map_visualization(data: pd.DataFrame, variants: list):
    """Create the map visualization with variant-specific data"""
    # Ensure severity_index is properly formatted for display
    data['severity_index'] = data['severity_index'].round(2)
    
    # Prepare hover data dictionary
    hover_data = {
        'active_cases': True,
        'infection_rate': ':.2%',
        'severity_index': ':.2f',
        'latitude': False,
        'longitude': False
    }
    
    # Add variant-specific cases to hover data if variants exist
    if variants:
        for variant in variants:
            hover_data[f'{variant["name"]}_cases'] = True
    
    # Create the scatter mapbox
    fig = px.scatter_mapbox(
        data_frame=data,
        lat='latitude',
        lon='longitude',
        size='active_cases',
        color='severity_index',
        hover_name='country',
        hover_data=hover_data,
        color_continuous_scale='RdYlBu_r',
        size_max=50,
        zoom=1,
        title='Global Disease Spread with Variant Impact',
        mapbox_style='carto-positron'
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        coloraxis_colorbar=dict(
            title="Severity Index (0-10)",
            tickformat=".1f"
        ),
        showlegend=False
    )
    
    # Update hover template for better formatting
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>" +
            "Active Cases: %{customdata[0]:,.0f}<br>" +
            "Infection Rate: %{customdata[1]:.2%}<br>" +
            "Severity Index: %{customdata[2]:.1f}/10<br>" +
            "<extra></extra>"
        )
    )
    
    return fig

def calculate_global_spread(params: dict, countries_data: pd.DataFrame, variants: list = None, vaccination_params: dict = None):
    """Calculate disease spread across different countries"""
    # Create a copy of the dataframe to avoid modifications to original
    data = countries_data.copy()
    
    # Calculate base risk factors
    data['risk_score'] = (
        0.3 * (data['population_density'] / data['population_density'].max()) +
        0.2 * (data['air_quality_index'] / data['air_quality_index'].max()) +
        0.2 * (data['water_quality_index'] / data['water_quality_index'].max()) +
        0.3 * (data['health_conditions_percentage'] / data['health_conditions_percentage'].max())
    ).clip(0, 1)
    
    # Calculate variant-adjusted transmission rate
    if variants:
        adjusted_transmission = calculate_variant_impact(variants, params['transmission_rate'])
    else:
        adjusted_transmission = params['transmission_rate']
    
    # Calculate vaccine effectiveness
    if vaccination_params and variants:
        vaccine_protection = calculate_vaccine_effectiveness(variants, vaccination_params)
    else:
        vaccine_protection = 0
    
    # Calculate infection rate
    data['infection_rate'] = (
        data['risk_score'] * 
        (adjusted_transmission / 100) *
        (1 - vaccine_protection) *
        (1 + params['mutation_rate'] / 100)
    ).clip(0, 1)  # Ensure rate is between 0 and 1
    
    # Calculate variant-specific cases if variants exist
    if variants:
        for variant in variants:
            variant_name = variant['name']
            data[f'{variant_name}_cases'] = np.floor(
                data['population'] * 
                data['infection_rate'] * 
                (variant['daily_cases'] / 1000) *
                (variant['severity'] / 10)
            ).astype(int)
    
    # Calculate total active cases
    data['active_cases'] = np.floor(
        data['population'] * 
        data['infection_rate']
    ).astype(int)
    
    # Calculate severity index
    data['severity_index'] = calculate_severity_index(data, variants if variants else [])
    
    return data

def display_variant_analysis(data: pd.DataFrame, variants: list):
    """Display variant-specific analysis"""
    st.subheader("Variant Analysis")
    
    if variants:
        for variant in variants:
            st.write(f"**{variant['name']} Impact**")
            total_variant_cases = data[f'{variant["name"]}_cases'].sum()
            st.metric(
                "Total Cases",
                f"{total_variant_cases:,}",
                delta=f"Severity: {variant['severity']}/10"
            )
    
    st.subheader("Country Impact Analysis")
    metric_option = st.selectbox(
        "Sort countries by",
        ['Total Cases', 'Severity Index', 'Variant Distribution']
    )
    
    display_country_rankings(data, metric_option, variants)

# WORLD HEATMAP MATHEMATICAL EXPLANATIONS

"""
Risk Score Calculation (in calculate_global_spread):

Risk Score = 0.3*(PD_norm) + 0.2*(AQ_norm) + 0.2*(WQ_norm) + 0.3*(HC_norm)

Where:
- PD_norm = Normalized population density (density/max_density)
- AQ_norm = Normalized air quality index (higher value = worse air quality)
- WQ_norm = Normalized water quality index (higher value = worse water quality)
- HC_norm = Normalized health conditions percentage

Weights:
- Population density: 0.3 (30%) - Higher weight due to direct impact on transmission
- Air quality: 0.2 (20%) - Medium weight as respiratory conditions affect spread
- Water quality: 0.2 (20%) - Medium weight for general health impact
- Health conditions: 0.3 (30%) - Higher weight due to comorbidity risks

Infection Rate Calculation:
IR = RS * (TR/100) * (1 + MR/100)

Where:
- IR = Infection Rate
- RS = Risk Score (0-1)
- TR = Transmission Rate (from user input)
- MR = Mutation Rate (from user input)

Active Cases Calculation:
AC = Population * (IR/100)

This creates a proportional relationship between population size and cases,
modified by the infection rate.
"""