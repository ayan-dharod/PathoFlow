import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any
import time
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import visualization components
from visualizations.infection_progress import display_infection_progress
from visualizations.world_heatmap import display_global_map
from visualizations.healthcare_load import display_healthcare_load
from visualizations.variant_analysis import display_variant_tracking
from visualizations.home import display_home_page
from src.data_handler import CountryDataHandler

def initialize_session_state():
    """Initialize all parameter values in session state"""
    # Initialize show_visualization
    if 'show_visualization' not in st.session_state:
        st.session_state.show_visualization = True  # True by default for Home page
    
    # Reset show_visualization when changing from Home to other pages
    if 'previous_page' not in st.session_state:
        st.session_state.previous_page = "Home"
    
    current_page = st.session_state.get('nav_page', "Home")  # Get current page
    if st.session_state.previous_page == "Home" and current_page != "Home":
        st.session_state.show_visualization = False
    st.session_state.previous_page = current_page
    
    if 'pathogen_params' not in st.session_state:
        st.session_state.pathogen_params = {
            'type': 'Virus',
            'transmission_route': 'Airborne',
            'transmission_rate': 50.0,
            'incubation_period': 5,
            'infectious_period': 14,
            'recovery_rate': 95.0,
            'mortality_rate': 2.0,
            'mutation_rate': 0.1
        }
    
    if 'variants' not in st.session_state:
        st.session_state.variants = []
        
    if 'healthcare_params' not in st.session_state:
        st.session_state.healthcare_params = {
            'hospital_beds': 20.0,
            'icu_beds': 5.0,
            'ventilators': 2.0,
            'transmission_rate': 5.0,
            'research_labs': 1.0,
            'reporting_systems': 10.0,
            'diagnostic_centers': 3.0,
            'healthcare_workers': 25.0,
            'epidemiologists': 2.0,
            'ppe_kits': 50.0,
            'medicine_stock': 1000.0,
            'healthcare_budget': 5000.0,
            'daily_tests': 100.0,
            'testing_accuracy': 95.0,
            'daily_vaccinations': 100.0
        }
    
    if 'vaccination_params' not in st.session_state:
        st.session_state.vaccination_params = {
            'vaccines': []
        }

    # Initialize vaccine-related session state variables
    if 'vaccine_to_remove' not in st.session_state:
        st.session_state.vaccine_to_remove = None
        
    if 'pending_vaccine' not in st.session_state:
        st.session_state.pending_vaccine = None
        
    if 'temp_vaccines' not in st.session_state:
        st.session_state.temp_vaccines = []

    if 'show_visualization' not in st.session_state:
        st.session_state.show_visualization = False

def main():
    # Set page config
    st.set_page_config(
        page_title="PathFlow",  # Updated title
        page_icon="🦠",
        layout="wide"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Navigation in sidebar at the top
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select a View",
        ["Home",
         "Infection Progression",
         "Global Spread Map",
         "Healthcare System Load",
         "Variant Tracking"]
    )
    
    # Main content area
    if page == "Home":
        display_home_page()
    else:
        # Parameter inputs in sidebar below navigation
        display_parameter_inputs(page)
        
        # Show visualizations only if parameters have been updated
        if st.session_state.show_visualization:
            if page == "Infection Progression":
                display_infection_progress()
            elif page == "Global Spread Map":
                display_global_map()
            elif page == "Healthcare System Load":
                display_healthcare_load()
            elif page == "Variant Tracking":
                display_variant_tracking()
        else:
            st.info("👈 Adjust parameters in the sidebar and click 'Update Visualization' to see the simulation results.")

def get_required_sections(page: str) -> list:
    """Return list of required parameter sections based on selected page"""
    sections = {
        "Home": [],
        "Infection Progression": ["pathogen"],
        "Global Spread Map": ["pathogen", "variants"],
        "Healthcare System Load": ["pathogen", "healthcare", "vaccination"],
        "Variant Tracking": ["pathogen", "variants"]
    }
    return sections.get(page, [])

def display_parameter_inputs(page: str):
    """Display parameter inputs based on selected visualization"""
    st.sidebar.header("Simulation Parameters")
    
    required_sections = get_required_sections(page)
    
    with st.sidebar.form("disease_parameters"):
        # 1. Pathogen Characteristics - always shown
        if "pathogen" in required_sections:
            st.subheader("Pathogen Characteristics")
            # Now this will be nested under Pathogen Characteristics
            display_pathogen_params()
        
        # 2. Variants Section
        if "variants" in required_sections:
            st.subheader("Variants")
            display_variant_params()
        
        # 3. Healthcare and Outbreak Response
        if "healthcare" in required_sections:
            st.subheader("Healthcare Response")
            display_healthcare_params()
        
        # 4. Vaccination Parameters
        if "vaccination" in required_sections:
            st.subheader("Vaccination")
            display_vaccination_params()

        # Submit button at the bottom
        st.form_submit_button("Update Visualization")

def display_pathogen_params() -> Dict[str, Any]:
    """Display pathogen characteristic inputs"""
    with st.expander("Basic Pathogen Parameters", expanded=False):
        st.session_state.pathogen_params['type'] = st.selectbox(
            "Type of Pathogen",
            options=['Virus', 'Bacteria', 'Fungi', 'Parasite'],
            help="Select the type of infectious agent"
        )
        
        # Rest of your parameter inputs remain the same
        st.session_state.pathogen_params['transmission_route'] = st.selectbox(
            "Route of Transmission",
            options=['Airborne', 'Droplet', 'Contact', 'Vector-borne', 'Food-borne', 'Water-borne'],
            help="How the pathogen spreads between hosts"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.pathogen_params['transmission_rate'] = st.number_input(
                "Transmission Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.pathogen_params['transmission_rate'],
                step=0.1
            )
            
            st.session_state.pathogen_params['incubation_period'] = st.number_input(
                "Incubation Period (days)",
                min_value=0,
                max_value=60,
                value=st.session_state.pathogen_params['incubation_period']
            )
            
            st.session_state.pathogen_params['infectious_period'] = st.number_input(
                "Infectious Period (days)",
                min_value=0,
                max_value=60,
                value=st.session_state.pathogen_params['infectious_period']
            )
            
        with col2:
            st.session_state.pathogen_params['recovery_rate'] = st.number_input(
                "Recovery Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.pathogen_params['recovery_rate'],
                step=0.1
            )
            
            st.session_state.pathogen_params['mortality_rate'] = st.number_input(
                "Mortality Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.pathogen_params['mortality_rate'],
                step=0.1
            )
            
            st.session_state.pathogen_params['mutation_rate'] = st.number_input(
                "Mutation Rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.pathogen_params['mutation_rate'],
                step=0.1
            )
    
    return st.session_state.pathogen_params

def display_variant_params():
    """Display variant input section"""
    with st.expander("Variant Parameters", expanded=False):
        num_variants = st.number_input(
            "Number of Variants",
            min_value=0,
            max_value=10,
            value=len(st.session_state.variants)
        )
        
        if st.checkbox("Add New Variant"):
            variant = {
                'name': st.text_input("Variant Name", value=f"Variant {len(st.session_state.variants) + 1}"),
                'daily_cases': st.number_input("Cases per 1,000 people", min_value=0.0, step=0.1),
                'severity': st.slider("Severity of Symptoms", 1, 10, 5),
                'mortality_rate': st.number_input("Mortality Rate (%)", 0.0, 100.0, step=0.1),
                'recovery_rate': st.number_input("Recovery Rate (%)", 0.0, 100.0, step=0.1),
                'vaccine_effectiveness': st.number_input("Vaccine Effectiveness (%)", 0.0, 100.0, step=0.1)
            }
            if not any(v['name'] == variant['name'] for v in st.session_state.variants):
                st.session_state.variants.append(variant)

def display_healthcare_params():
    """Display healthcare system parameters"""
    with st.expander("Healthcare System Parameters", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.healthcare_params['hospital_beds'] = st.number_input(
                "Hospital Beds (per 10,000)",
                min_value=0.0,
                max_value=10000.0,
                value=float(st.session_state.healthcare_params['hospital_beds']),
                step=0.1
            )
            
            st.session_state.healthcare_params['icu_beds'] = st.number_input(
                "ICU Beds (per 10,000)",
                min_value=0.0,
                max_value=10000.0,
                value=float(st.session_state.healthcare_params['icu_beds']),
                step=0.1
            )
            
            st.session_state.healthcare_params['ventilators'] = st.number_input(
                "Ventilators (per 10,000)",
                min_value=0.0,
                max_value=10000.0,
                value=float(st.session_state.healthcare_params['ventilators']),
                step=0.1
            )
        
        with col2:
            st.session_state.healthcare_params['healthcare_workers'] = st.number_input(
                "Healthcare Workers (per 10,000)",
                min_value=0.0,
                max_value=10000.0,
                value=float(st.session_state.healthcare_params['healthcare_workers']),
                step=0.1
            )
            
            st.session_state.healthcare_params['medicine_stock'] = st.number_input(
                "Medicine Stock (per 100)",
                min_value=0.0,
                max_value=100000.0,
                value=float(st.session_state.healthcare_params['medicine_stock']),
                step=0.1
            )

def display_vaccination_params():
    """Display vaccination program parameters"""
    if 'vaccination_params' not in st.session_state:
        st.session_state.vaccination_params = {
            'vaccines': []
        }
        
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
                    if st.form_submit_button("Remove", key=f"remove_vaccine_{idx}"):
                        vaccines_to_remove.append(idx)
            
            # Remove vaccines (if any) after the loop
            for idx in reversed(vaccines_to_remove):
                st.session_state.vaccination_params['vaccines'].pop(idx)
                st.rerun()

        # Add new vaccine interface
        if st.checkbox("Add New Vaccine"):
            vaccine_name = st.text_input(
                "Vaccine Name", 
                value=f"Vaccine {len(st.session_state.vaccination_params['vaccines']) + 1}"
            )
            population_vaccinated = st.number_input(
                "Population Vaccinated (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=0.0,
                step=0.1
            )
            effectiveness = st.number_input(
                "Effectiveness Against Infection (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=95.0,
                step=0.1
            )
            waning_immunity_rate = st.number_input(
                "Monthly Waning Rate (%)", 
                min_value=0.0, 
                max_value=100.0, 
                value=5.0,
                step=0.1
            )
            
            new_vaccine = {
                'name': vaccine_name,
                'population_vaccinated': population_vaccinated,
                'effectiveness': effectiveness,
                'waning_immunity_rate': waning_immunity_rate
            }
            
            # Directly update session state
            if not any(v['name'] == new_vaccine['name'] for v in st.session_state.vaccination_params['vaccines']):
                if 'temp_vaccines' not in st.session_state:
                    st.session_state.temp_vaccines = []
                st.session_state.temp_vaccines.append(new_vaccine)
                st.session_state.vaccination_params['vaccines'] = st.session_state.temp_vaccines

        # Display total number of vaccines
        total_vaccines = len(st.session_state.vaccination_params['vaccines'])
        st.metric(
            "Total Vaccines",
            total_vaccines,
            help="Number of vaccines currently configured"
        )
        
        # Debug information
        st.write("Debug Info:")
        st.write(f"Number of vaccines in system: {total_vaccines}")
        if total_vaccines > 0:
            st.write("Current vaccines:")
            for v in st.session_state.vaccination_params['vaccines']:
                st.write(f"- {v['name']}: {v['population_vaccinated']}% coverage")

if __name__ == "__main__":
    main()