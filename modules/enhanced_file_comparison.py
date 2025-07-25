import streamlit as st
import pandas as pd
from datetime import date
from ui.components import (
    display_results_with_download,
    create_loading_context, update_progress
)
from utils.enhanced_data_utils import (
    load_backend_reactor_database, filter_valid_patients, validate_file_structure
)

def compare_with_reactor_database(current_df, reactor_df):
    """Compare current patient data with REACTOR database to find new matches"""
    # Filter out invalid records
    current_df = filter_valid_patients(current_df)
    reactor_df = filter_valid_patients(reactor_df)
    
    progress_total = len(current_df)
    progress_bar = st.progress(0, text="Comparing with REACTOR database...")

    new_matches = pd.DataFrame()
    for i, row in current_df.iterrows():
        if row['PatientID'] not in reactor_df['PatientID'].values:
            new_matches = pd.concat([new_matches, pd.DataFrame([row])], ignore_index=True)
        update_progress(progress_bar, i + 1, progress_total, "Analyzing")

    return new_matches, current_df, reactor_df

def run_file_comparison_with_data(patient_data):
    """Enhanced file comparison using provided patient data"""
    
    if patient_data.empty:
        st.warning("⚠️ No patient data provided. Please enter patient data in the main input section above.")
        return
    
    st.markdown("### 📊 Dataset Comparison Tool (REACTOR)")
    st.markdown("*Using the patient data from above to compare against REACTOR database*")
    
    # Show current patient data summary
    st.info(f"📊 **Current Dataset:** {len(patient_data)} patients loaded")

    # Backend Database Status
    st.markdown("**🗄️ REACTOR Database Status**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            reactor_count = load_backend_reactor_database(check_only=True)
            st.success(f"✅ REACTOR DB: {reactor_count:,} historical records")
        except Exception as e:
            st.error(f"❌ REACTOR DB: {str(e)}")
    
    with col2:
        st.info("🔄 Last Updated: 2025-06-20")
        st.info("📊 Database Version: v3.2")

    st.markdown("---")

    if st.button("🔄 **Compare with REACTOR Database**", use_container_width=True, key="start_reactor_comparison"):
        with create_loading_context("Loading REACTOR database and analyzing differences..."):
            try:
                # Validate patient data structure
                if not validate_file_structure(patient_data, ['PatientID', 'Gene'], "Patient"):
                    return
                
                # Load backend REACTOR database
                reactor_df = load_backend_reactor_database()
                if reactor_df.empty:
                    st.error("❌ Failed to load REACTOR database.")
                    return
                
                # Compare datasets
                new_matches, clean_current, clean_reactor = compare_with_reactor_database(patient_data, reactor_df)
                
                # Prepare additional statistics
                additional_info = [
                    f"📊 **Current Records:** {len(clean_current)}",
                    f"🗄️ **REACTOR Records:** {len(clean_reactor)}",
                    f"📈 **New Discoveries:** {len(new_matches)}",
                    f"📊 **Discovery Rate:** {(len(new_matches)/len(clean_current)*100):.1f}%" if len(clean_current) > 0 else "**Discovery Rate:** N/A"
                ]
                
                if len(new_matches) > 0:
                    success_message = f"🆕 Found {len(new_matches)} new patient records not in REACTOR database!"
                else:
                    success_message = "ℹ️ All patients already exist in REACTOR database."
                
                display_results_with_download(
                    new_matches,
                    success_message,
                    f"reactor_comparison_results_{date.today()}.csv",
                    additional_info
                )

            except Exception as e:
                st.error(f"❌ Error comparing with REACTOR database: {str(e)}")
                st.exception(e)

# Keep the old function for backward compatibility
def run_file_comparison():
    """Legacy function - redirects to the unified version"""
    if 'patient_data' in st.session_state and not st.session_state['patient_data'].empty:
        run_file_comparison_with_data(st.session_state['patient_data'])
    else:
        st.warning("⚠️ No patient data available. Please enter patient data in the main input section.")
        
