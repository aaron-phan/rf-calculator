import streamlit as st
import pandas as pd
from reach_frequency_calculator import ReachFrequencyCalculator

def create_gui():
    st.set_page_config(layout="wide")  # Makes better use of screen space
    
    # Title and tabs
    st.title("Reach & Frequency Calculator")
    tab1, tab2, tab3 = st.tabs(["Input Parameters", "Channel Distribution", "Results Dashboard"])
    
    with tab1:
        # Basic and Advanced Parameters
        st.header("Basic Inputs")
        col1, col2 = st.columns(2)
        
        with col1:
            total_universe = st.number_input(
                "Total Universe", 
                value=1_000_000,
                min_value=1_000_000,
                format="%d"  # Comma formatting
            )
            
            total_impressions = st.number_input(
                "Total Impressions",
                value=10_000,
                min_value=10_000,
                format="%d"
            )
        
        with col2:
            max_reach_percent = st.number_input(
                "Maximum Reach %",
                value=98.2,
                min_value=0.0,
                max_value=99.8
            )
            global_overlap_factor = st.number_input(
                "Global Overlap Factor",
                value=0.5,
                min_value=0.35,
                max_value=0.6
            )

    with tab2:
        # Channel Distribution
        st.header("Channel Impressions")
        
        default_channels = {
            "OOH": 0,
            "TV": 0,
            "CTV/FEP": 0,
            "YouTube": 0,
            "Console": 0,
            "Creators": 0,
            "Music Streaming": 0,
            "Programmatic": 0,
            "Display": 0,
            "Social": 0,
            "Search": 0
        }
        
        df = pd.DataFrame(list(default_channels.items()), columns=['Channel', 'Impressions'])
        
        edited_df = st.data_editor(
            df,
            key="channel_data",
            disabled=["Channel"],  # Lock channel names
            hide_index=True
        )
        
        distributed_impressions = {
            channel: int(impressions) 
            for channel, impressions in zip(edited_df['Channel'], edited_df['Impressions'])
        }
    
    with tab3:
        # Results Dashboard (only show when calculate button is clicked)
        if st.button("Calculate Results"):
            calculator = ReachFrequencyCalculator(
                total_universe=total_universe,
                total_impressions=total_impressions,
                max_reach_percent=max_reach_percent,
                global_overlap_factor=global_overlap_factor,
                distributed_impressions=distributed_impressions,
                channel_penetration={
                    "OOH": 0.08, "TV": 0.782, "CTV/FEP": 0.75, "YouTube": 0.91,
                    "Console": 0.39, "Creators": 0.17, "Music Streaming": 0.686,
                    "Programmatic": 0.941, "Display": 0.941, "Social": 0.913, "Search": 0.65
                },
                efficiency_factors={
                    "OOH": 0.5, "TV": 0.8, "CTV/FEP": 0.8, "YouTube": 0.8,
                    "Console": 0.9, "Creators": 0.85, "Music Streaming": 0.75,
                    "Programmatic": 0.35, "Display": 0.6, "Social": 0.6, "Search": 0.7
                }
            )
            
            results = calculator.run_all_calculations()
            
            st.header("Results")
            
            # Channel contributions
            st.subheader("Channel Contributions")
            contrib_df = pd.DataFrame([
                {"Channel": channel, "Contribution %": f"{contrib:.1f}%"}
                for channel, contrib in results['channel_contributions'].items()
            ])
            st.dataframe(contrib_df.style.format({"Contribution %": "{:,.1f}%"}), hide_index=True)
            
            # Main metrics
            st.subheader("Reach Metrics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Final Reach %", f"{results['final_reach_percent']:.1f}%")
            with col2:
                st.metric("Final Reach (Individuals)", f"{results['final_reach']:,}")  # Adds commas
            with col3:
                st.metric("Average Frequency", f"{results['average_frequency']:.1f}")
            
            # Effective reach
            st.subheader("Effective Reach")
            effective_df = pd.DataFrame([
                {"Frequency": freq, "Reach %": f"{reach:.1f}%"}
                for freq, reach in results['effective_reach'].items()
            ])
            st.dataframe(effective_df.style.format({"Reach %": "{:,.1f}%"}), hide_index=True)

if __name__ == "__main__":
    create_gui()
