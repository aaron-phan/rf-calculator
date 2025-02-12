import streamlit as st
import pandas as pd
import pytesseract
import cv2
import numpy as np
from PIL import Image
from reach_frequency_calculator import ReachFrequencyCalculator

def extract_channels_from_image(image):
    """Extracts channel names and impressions from a flowchart image using OCR."""
    try:
        # Convert image to grayscale for better OCR
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

        # Apply thresholding to improve OCR accuracy
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Run OCR on the processed image
        extracted_text = pytesseract.image_to_string(thresh)

        # Split text into lines and filter out empty ones
        lines = [line.strip() for line in extracted_text.split("\n") if line.strip()]

        # Extract channels and impressions from the text
        extracted_data = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                # Assume last part is the impression value
                impressions = parts[-1].replace(",", "").strip()
                channel = " ".join(parts[:-1])  # Everything before the last part
                if impressions.isdigit():
                    extracted_data.append((channel, int(impressions)))

        return extracted_data

    except Exception as e:
        st.error(f"Error processing image: {e}")
        return []

def create_gui():
    st.set_page_config(layout="wide")  # Improves screen space usage
    
    # Title and tabs
    st.title("Reach & Frequency Calculator")
    tab1, tab2 = st.tabs(["Input Parameters & Channel Distribution", "Results Dashboard"])
    
    with tab1:
        # Basic Inputs
        st.header("Basic Inputs")
        col1, col2 = st.columns(2)
        
        with col1:
            total_universe = st.number_input(
                "Total Universe", 
                value=1_000_000,
                min_value=1_000_000,
                format="%d"  # Ensures comma formatting
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

        # Upload Image for OCR Processing
        st.header("Upload Flowchart Image for Auto Extraction")
        uploaded_file = st.file_uploader("Upload an image (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])
        
        extracted_data = []
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            extracted_data = extract_channels_from_image(image)
            if extracted_data:
                st.success(f"Extracted {len(extracted_data)} entries from image.")

        # Channel Distribution (Moved Here)
        st.header("Channel Impressions")
        
        # Default channels
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

        # Override defaults with extracted values
        for channel, impressions in extracted_data:
            default_channels[channel] = impressions

        # Convert to DataFrame and keep it editable
        df = pd.DataFrame(list(default_channels.items()), columns=['Channel', 'Impressions'])
        
        edited_df = st.data_editor(
            df,
            key="channel_data",
            disabled=["Channel"],  # Lock channel names
            hide_index=True
        )

        # Calculate Total Impressions dynamically
        total_impressions = edited_df["Impressions"].sum()

        # Display Total Impressions (Now Auto-Calculated)
        st.metric("Total Impressions", f"{total_impressions:,}")

    with tab2:
        # Results Dashboard (only show when calculate button is clicked)
        if st.button("Calculate Results"):
            calculator = ReachFrequencyCalculator(
                total_universe=total_universe,
                total_impressions=total_impressions,  # Now dynamically calculated
                max_reach_percent=max_reach_percent,
                global_overlap_factor=global_overlap_factor,
                distributed_impressions={
                    channel: int(impressions) 
                    for channel, impressions in zip(edited_df['Channel'], edited_df['Impressions'])
                },
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
            
            # Ensure "Contribution %" is numeric before applying formatting
            contrib_df["Contribution %"] = contrib_df["Contribution %"].str.replace('%', '').astype(float)
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
            
            # Ensure "Reach %" is numeric before applying formatting
            effective_df["Reach %"] = effective_df["Reach %"].str.replace('%', '').astype(float)
            
            st.dataframe(effective_df.style.format({"Reach %": "{:,.1f}%"}), hide_index=True)

if __name__ == "__main__":
    create_gui()
