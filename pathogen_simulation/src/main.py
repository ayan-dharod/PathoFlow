# src/main.py
import streamlit as st
import plotly.express as px
from data_handler import CountryDataHandler

def main():
    st.title("Global Country Analysis Dashboard")
    
    # Initialize data handler
    handler = CountryDataHandler()
    df = handler.load_country_data()
    
    # Sidebar for filters
    st.sidebar.title("Filters")
    selected_continent = st.sidebar.multiselect(
        "Select Continents",
        options=sorted(df['continent'].unique()),
        default=sorted(df['continent'].unique())
    )
    
    # Filter data
    filtered_df = df[df['continent'].isin(selected_continent)]
    
    # Main content
    st.header("Country Overview")
    
    # Display total countries and other stats
    stats = handler.get_country_stats()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Countries", stats['total_countries'])
    with col2:
        st.metric("Avg Air Quality Index", f"{stats['avg_air_quality']:.1f}")
    with col3:
        st.metric("Avg Water Quality Index", f"{stats['avg_water_quality']:.1f}")
    
    # Population Map
    st.subheader("Population Distribution")
    fig = px.scatter_geo(filtered_df,
                        locations='country',
                        locationmode='country names',
                        size='population',
                        color='continent',
                        hover_name='country',
                        hover_data=['population_density', 
                                  'air_quality_index',
                                  'water_quality_index'],
                        title='Population by Country')
    st.plotly_chart(fig)
    
    # Additional visualizations
    st.subheader("Quality Indices by Country")
    quality_fig = px.scatter(filtered_df,
                           x='air_quality_index',
                           y='water_quality_index',
                           size='population',
                           color='continent',
                           hover_name='country',
                           title='Air Quality vs Water Quality')
    st.plotly_chart(quality_fig)
    
    # Display detailed data
    st.subheader("Detailed Country Data")
    st.dataframe(filtered_df)
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name="country_data.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()