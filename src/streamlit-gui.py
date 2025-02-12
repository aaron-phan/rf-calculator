import streamlit as st
import pandas as pd
import plotly.express as px  # For better charts
from reach_frequency_calculator import ReachFrequencyCalculator

def create_gui():
    st.set_page_config(layout="wide")  # Makes better use of screen space
    
    # Title and tabs
    st.title("Reach & Frequency Calculator")
    tab1, tab2, tab3 = st.tabs(["Input Parameters", "Channel Distribution", "Results Dashboard"])
    
    with tab1:
        # Basic and Advanced Parameters
        col1, col2 = st.columns(2)
        
        with col1:
            with st.container():
                st.markdown("### Basic Parameters")
                
                total_universe = st.number_input(
                    "Total Universe 👥", 
                    value=1000000,
                    min_value=1000000,
                    help="The total addressable audience size"
                )

                total_impressions = st.number_input(
                    "Total Impressions 👁️",
                    value=10000,
                    min_value=10000,
                    help="Total number of impressions across all channels"
                )
            
        with col2:
            with st.container():
                st.markdown("### Advanced Settings")
                
                max_reach_percent = st.number_input(
                    "Maximum Reach % 📊",
                    value=98.2,
                    min_value=0.0,
                    max_value=99.8,
                    help="Maximum possible reach percentage"
                )
                
                global_overlap_factor = st.number_input(
                    "Global Overlap Factor 🔄",
                    value=0.5,
                    min_value=0.35,
                    max_value=0.6,
                    help="Factor determining audience overlap between channels"
                )
    
    with tab2:
        # Channel Distribution
        st.header("Channel Distribution")
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Ensure default_channels is defined
            default_channels = {
                "TV": 5000,
                "Social Media": 3000,
                "Search Ads": 2000
            }
            
            df = pd.DataFrame(
                [[channel, impressions] for channel, impressions in default_channels.items()],
                columns=['Channel', 'Impressions']
            )
            
            edited_df = st.data_editor(
                df,
                num_rows="fixed",
                disabled=["Channel"],
                column_config={
                    "Channel": st.column_config.TextColumn(
                        "Channel",
                        help="Media channel name",
                        width="medium",
                    ),
                    "Impressions": st.column_config.NumberColumn(
                        "Impressions",
                        help="Number of impressions",
                        min_value=0,
                        width="medium",
                        format="%d"
                    )
                }
            )
        
        with col2:
            # Add distribution preview
            if edited_df['Impressions'].sum() > 0:
                fig = px.pie(edited_df, values='Impressions', names='Channel', title='Channel Distribution')
                st.plotly_chart(fig)
    
    with tab3:
        # Results Dashboard (only show when calculate button is clicked)
        if 'results' in st.session_state:
            results = st.session_state.results
            
            # Key metrics in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Final Reach %", f"{results['final_reach_percent']:.1f}%")
            with col2:
                st.metric("Final Reach", f"{results['final_reach']:,.0f}")
            with col3:
                st.metric("Average Frequency", f"{results['average_frequency']:.1f}")
            
            # Effective reach chart
            st.subheader("Effective Reach Curve")
            reach_df = pd.DataFrame([
                {"Frequency": freq, "Reach %": reach}
                for freq, reach in results['effective_reach'].items()
            ])
            fig = px.line(reach_df, x='Frequency', y='Reach %', title='Effective Reach by Frequency')
            st.plotly_chart(fig)
            
            # Channel contributions
            st.subheader("Channel Contributions")
            contrib_df = pd.DataFrame([
                {"Channel": channel, "Contribution %": contrib}
                for channel, contrib in results['channel_contributions'].items()
            ])
            fig = px.bar(contrib_df, x='Channel', y='Contribution %', title='Channel Contributions')
            st.plotly_chart(fig)

    # Calculate button at the bottom
    if st.button("Calculate Results"):
        # Placeholder for actual calculation logic
        calculator = ReachFrequencyCalculator(
            total_universe=total_universe,
            total_impressions=total_impressions,
            max_reach_percent=max_reach_percent,
            global_overlap_factor=global_overlap_factor,
            channel_data=edited_df
        )
        results = calculator.run_all_calculations()
        st.session_state.results = results

if __name__ == "__main__":
    create_gui()
