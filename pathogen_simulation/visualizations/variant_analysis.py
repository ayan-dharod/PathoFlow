# Variant analysis visualization
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def calculate_variant_metrics(params: dict, variants: list):
    """
    Calculate metrics for different variants
    """
    base_transmission = params['transmission_rate']
    variant_data = []
    
    for variant in variants:
        relative_transmission = variant.get('daily_cases', 0) * 10  # Scale up for visibility
        variant_data.append({
            'name': variant['name'],
            'transmission_rate': relative_transmission,
            'severity': variant['severity'],
            'mortality_rate': variant['mortality_rate'],
            'vaccine_effectiveness': variant['vaccine_effectiveness']
        })
    
    return pd.DataFrame(variant_data)

def display_variant_tracking():
    st.header("Variant Analysis")
    
    if not st.session_state.variants:
        st.warning("No variants have been added yet. Add variants in the sidebar to see analysis.")
        return
    
    variant_data = calculate_variant_metrics(
        st.session_state.pathogen_params,
        st.session_state.variants
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create parallel coordinates plot for variant comparison
        fig = go.Figure(data=
            go.Parcoords(
                line=dict(color=variant_data.index,
                         colorscale='Viridis'),
                dimensions=[
                    dict(range=[0, 100],
                         label='Transmission Rate',
                         values=variant_data['transmission_rate']),
                    dict(range=[0, 10],
                         label='Severity',
                         values=variant_data['severity']),
                    dict(range=[0, 100],
                         label='Mortality Rate',
                         values=variant_data['mortality_rate']),
                    dict(range=[0, 100],
                         label='Vaccine Effectiveness',
                         values=variant_data['vaccine_effectiveness'])
                ]
            )
        )
        fig.update_layout(title='Variant Comparison')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Variant Details")
        selected_variant = st.selectbox(
            "Select Variant",
            options=variant_data['name'].tolist()
        )
        
        if selected_variant:
            variant = variant_data[variant_data['name'] == selected_variant].iloc[0]
            st.metric("Transmission Rate", f"{variant['transmission_rate']:.1f}")
            st.metric("Severity Score", f"{variant['severity']}/10")
            st.metric("Mortality Rate", f"{variant['mortality_rate']:.1f}%")
            st.metric("Vaccine Effectiveness", f"{variant['vaccine_effectiveness']:.1f}%")