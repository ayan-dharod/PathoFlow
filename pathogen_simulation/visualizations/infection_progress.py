# Infection progression visualization
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def calculate_infection_progression(params: dict, num_days: int = 100):
    """
    Calculate SEIR model progression based on input parameters
    """
    # Initial population parameters
    N = 100000  # Total population
    I0 = 100    # Initial infected
    E0 = 200    # Initial exposed
    R0 = 0      # Initial recovered
    D0 = 0      # Initial deceased
    S0 = N - I0 - E0 - R0 - D0  # Initial susceptible
    
    # Convert rates to daily probabilities
    beta = params['transmission_rate'] / 100  # Transmission rate
    sigma = 1 / params['incubation_period']   # Rate of exposed becoming infected
    gamma = 1 / params['infectious_period']    # Recovery rate
    mu = params['mortality_rate'] / 100        # Mortality rate
    
    # Initialize arrays to store values
    S = np.zeros(num_days)
    E = np.zeros(num_days)
    I = np.zeros(num_days)
    R = np.zeros(num_days)
    D = np.zeros(num_days)
    
    # Set initial values
    S[0] = S0
    E[0] = E0
    I[0] = I0
    R[0] = R0
    D[0] = D0
    
    # Calculate progression
    for t in range(1, num_days):
        # SEIR model differential equations
        new_exposed = (beta * S[t-1] * I[t-1]) / N
        new_infected = sigma * E[t-1]
        new_recovered = gamma * I[t-1] * (1 - mu)
        new_deceased = gamma * I[t-1] * mu
        
        S[t] = S[t-1] - new_exposed
        E[t] = E[t-1] + new_exposed - new_infected
        I[t] = I[t-1] + new_infected - new_recovered - new_deceased
        R[t] = R[t-1] + new_recovered
        D[t] = D[t-1] + new_deceased
    
    return pd.DataFrame({
        'Day': range(num_days),
        'Susceptible': S,
        'Exposed': E,
        'Infected': I,
        'Recovered': R,
        'Deceased': D
    })

def display_infection_progress():
    st.header("Infection Progression")
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Get relevant parameters from session state
        params = {
            'transmission_rate': st.session_state.pathogen_params['transmission_rate'],
            'incubation_period': st.session_state.pathogen_params['incubation_period'],
            'infectious_period': st.session_state.pathogen_params['infectious_period'],
            'recovery_rate': st.session_state.pathogen_params['recovery_rate'],
            'mortality_rate': st.session_state.pathogen_params['mortality_rate']
        }
        
        # Calculate the progression
        df = calculate_infection_progression(params)
        
        # Create the main progression plot
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Disease Progression', 'Daily New Cases'),
            vertical_spacing=0.15
        )
        
        # Add SEIR curves
        fig.add_trace(
            go.Scatter(x=df['Day'], y=df['Susceptible'], name='Susceptible', line=dict(color='blue')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['Day'], y=df['Exposed'], name='Exposed', line=dict(color='orange')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['Day'], y=df['Infected'], name='Infected', line=dict(color='red')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['Day'], y=df['Recovered'], name='Recovered', line=dict(color='green')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['Day'], y=df['Deceased'], name='Deceased', line=dict(color='black')),
            row=1, col=1
        )
        
        # Calculate and plot daily new cases
        daily_new = df['Infected'].diff()
        fig.add_trace(
            go.Bar(x=df['Day'], y=daily_new, name='New Cases', marker_color='red'),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text="Disease Spread Analysis",
            hovermode='x unified'
        )
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Key Statistics")
        
        # Calculate key metrics
        peak_infected = int(df['Infected'].max())
        peak_day = df.loc[df['Infected'].idxmax(), 'Day']
        total_infected = int(df['Infected'].sum())
        total_deceased = int(df['Deceased'].iloc[-1])
        mortality_percentage = (total_deceased / total_infected * 100) if total_infected > 0 else 0
        
        # Display metrics
        st.metric("Peak Active Cases", f"{peak_infected:,}")
        st.metric("Day of Peak", f"Day {int(peak_day)}")
        st.metric("Total Cases", f"{total_infected:,}")
        st.metric("Total Deceased", f"{total_deceased:,}")
        st.metric("Overall Mortality Rate", f"{mortality_percentage:.2f}%")
        
        # Display current parameters used
        st.subheader("Current Parameters")
        st.write(f"Transmission Rate: {params['transmission_rate']}%")
        st.write(f"Incubation Period: {params['incubation_period']} days")
        st.write(f"Infectious Period: {params['infectious_period']} days")
        st.write(f"Recovery Rate: {params['recovery_rate']}%")
        st.write(f"Mortality Rate: {params['mortality_rate']}%")

# INFECTION PROGRESSION MATHEMATICAL EXPLANATIONS

"""
SEIR Model Differential Equations:

The model uses the following compartments:
S: Susceptible
E: Exposed
I: Infected
R: Recovered
D: Deceased

Key Rates:
β (beta) = Transmission rate/100
σ (sigma) = 1/incubation_period (rate of exposed becoming infected)
γ (gamma) = 1/infectious_period (recovery rate)
μ (mu) = mortality_rate/100

Daily Change Equations:

1. New Exposed (dE/dt):
   dE = (β * S * I) / N
   - Based on mass action principle in epidemiology
   - N normalizes the interaction between S and I
   - β represents probability of transmission per contact

2. New Infected (dI/dt):
   dI = σ * E
   - Linear progression from exposed to infected
   - 1/σ is average incubation period

3. New Recovered (dR/dt):
   dR = γ * I * (1 - μ)
   - γ represents rate of leaving infected state
   - (1 - μ) represents proportion that recover vs die

4. New Deceased (dD/dt):
   dD = γ * I * μ
   - μ represents proportion of infected that die
   - Coupled with recovery rate (γ)

Daily Updates:
S(t) = S(t-1) - dE
E(t) = E(t-1) + dE - dI
I(t) = I(t-1) + dI - dR - dD
R(t) = R(t-1) + dR
D(t) = D(t-1) + dD

Key Metrics Calculations:

1. Peak Infected:
   max(I) over all t

2. Peak Day:
   argmax(I) over all t

3. Total Cases:
   sum(I) over all t

4. Overall Mortality Rate:
   (D_final / Total_Cases) * 100

Notes:
- Model assumes closed population (no births/deaths except from disease)
- Perfect mixing of population
- No reinfection possible
- No age or spatial structure
- Deterministic model (no randomness)
"""