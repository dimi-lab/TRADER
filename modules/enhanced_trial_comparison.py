import streamlit as st
import pandas as pd
from datetime import date
from ui.components import (
    display_file_uploader_with_preview, display_results_with_download,
    create_loading_context, update_progress
)
from utils.enhanced_data_utils import load_csv_data, filter_valid_patients

def compare_patient_files(original_df, updated_df):
    """Compare two patient files and find new matches with progress tracking"""
    # Filter out invalid records
    original_df = filter_valid_patients(original_df)
    updated_df = filter_valid_patients(updated_df)
    
    progress_total = len(updated_df)
    progress_bar = st.progress(0, text="Comparing records...")

    new_matches = pd.DataFrame()
    for i, row in updated_df.iterrows():
        if row['PatientID'] not in original_df['PatientID'].values:
            new_matches = pd.concat([new_matches, pd.DataFrame([row])], ignore_index=True)
        update_progress(progress_bar, i + 1, progress_total, "Analyzing")

    return new_matches, original_df, updated_df

def run_file_comparison():
    """Enhanced file comparison with better UX and comprehensive statistics"""
    st.markdown("**REACTOR - Reanalysis Engine for Assessing Clinical Trials in Orphan Rare Diseases**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Original Dataset**")
        original_file = display_file_uploader_with_preview(
            "Upload Original Matched File", 
            ["csv", 'txt'], 
            "original_matched",
            "Upload the baseline dataset for comparison"
        )
    
    with col2:
        st.markdown("**🆕 Updated Dataset**")
        updated_file = display_file_uploader_with_preview(
            "Upload Updated Matched File", 
            ["csv", 'txt'], 
            "updated_matched",
            "Upload the new dataset to compare against the original"
        )

    st.markdown("---")

    if st.button("🔄 **Compare Datasets**", use_container_width=True):
        if not original_file or not updated_file:
            st.error("❌ Both files must be uploaded for comparison.")
            return

        with create_loading_context("Analyzing differences between datasets..."):
            try:
                original_df = load_csv_data(original_file)
                updated_df = load_csv_data(updated_file)
                
                if original_df.empty or updated_df.empty:
                    st.error("❌ One or both files could not be loaded properly.")
                    return
                
                new_matches, clean_original, clean_updated = compare_patient_files(original_df, updated_df)
                
                # Prepare additional statistics
                additional_info = [
                    f"📊 **Original Records:** {len(clean_original)}",
                    f"📈 **Updated Records:** {len(clean_updated)}",
                    f"📊 **Growth Rate:** {(len(new_matches)/len(clean_original)*100):.1f}%" if len(clean_original) > 0 else "**Growth Rate:** N/A"
                ]
                
                if len(new_matches) > 0:
                    success_message = f"🆕 Found {len(new_matches)} new patient matches!"
                else:
                    success_message = "ℹ️ No new matches found between the datasets."
                
                display_results_with_download(
                    new_matches,
                    success_message,
                    f"comparison_results_{date.today()}.csv",
                    additional_info
                )

            except Exception as e:
                st.error(f"❌ Error comparing files: {str(e)}")
