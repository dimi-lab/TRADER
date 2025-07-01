import streamlit as st
import pandas as pd
import re
import time
from datetime import date
from ui.components import (
    display_results_with_download, create_loading_context,
    update_progress, simulate_progress_with_delay
)
from utils.enhanced_data_utils import (
    load_backend_trial_database, apply_exclusion_filters,
    create_gene_regex, validate_file_structure
)

def create_exclusion_filters():
    """Create exclusion filter selection interface"""
    st.markdown("**🎛️ Exclusion Filters**")
    st.markdown("*Select condition categories to exclude from matching (helps focus on rare diseases):*")
    
    # Available exclusion categories
    exclusion_options = {
        'Cancer/Oncology': '🎗️ Cancer, carcinoma, tumor, leukemia, lymphoma, etc.',
        'Trauma/Injury': '🚑 Trauma, injury, wounds, burns, fractures',
        'Infectious Disease': '🦠 Bacterial, viral infections, sepsis, pneumonia',
        'Cardiovascular': '❤️ Cardiac, heart disease, stroke, coronary conditions',
        'Neurological': '🧠 Alzheimer\'s, Parkinson\'s, dementia, epilepsy',
        'Psychiatric': '🧘 Depression, anxiety, bipolar, schizophrenia',
        'Metabolic': '⚖️ Diabetes, obesity, metabolic syndrome',
        'Autoimmune': '🛡️ Arthritis, lupus, inflammatory bowel disease'
    }
    
    # Create filter selection in two columns
    col1, col2 = st.columns(2)
    selected_filters = []
    
    with col1:
        for i, (key, description) in enumerate(list(exclusion_options.items())[:4]):
            if st.checkbox(f"{description}", key=f"trial_filter_{key}"):
                selected_filters.append(key)
    
    with col2:
        for i, (key, description) in enumerate(list(exclusion_options.items())[4:]):
            if st.checkbox(f"{description}", key=f"trial_filter_{key}"):
                selected_filters.append(key)
    
    # Show selected filters summary
    if selected_filters:
        st.info(f"🎯 **Active Filters:** {', '.join(selected_filters)}")
    else:
        st.warning("⚠️ **No filters selected** - All trial types will be included in matching")
    
    return selected_filters

def find_gene_matches(patient_row, trials_df, exclusion_filters=None):
    """Find gene matches with configurable exclusion filters"""
    gene = str(patient_row['Gene']).upper()
    gene_regex = create_gene_regex(gene)
    
    # Apply exclusion filters
    exclusion_mask = apply_exclusion_filters(trials_df, exclusion_filters)
    
    # Apply gene matching and exclusion filters
    mask = (
        exclusion_mask &
        (
            trials_df['StudyTitle'].str.contains(gene_regex, case=True, na=False) |
            trials_df['BriefSummary'].str.contains(gene_regex, case=True, na=False)
        )
    )
    
    matches = trials_df[mask].copy()
    if not matches.empty:
        patient_df = pd.DataFrame([patient_row])
        combined = patient_df.merge(matches, how='cross')
        combined = combined[combined['PatientID'] != 'PatientID']
        return combined
    return None

def process_trial_matching(patient_df, trial_df, exclusion_filters):
    """Process trial matching for all patients with progress tracking"""
    progress_total = len(patient_df)
    progress_bar = st.progress(0, text="Initializing matching algorithm...")

    results = []
    for i, row in patient_df.iterrows():
        update_progress(progress_bar, i + 1, progress_total, "Matching genes")
        match_df = find_gene_matches(row, trial_df, exclusion_filters)
        if match_df is not None:
            results.append(match_df)
        time.sleep(0.01)  # Small delay for visual effect

    if results:
        matched_df = pd.concat(results, ignore_index=True).drop_duplicates()
        return matched_df
    return pd.DataFrame()

def run_trial_matcher_with_data(patient_data):
    """Enhanced trial matcher using provided patient data"""
    
    if patient_data.empty:
        st.warning("⚠️ No patient data provided. Please enter patient data in the main input section above.")
        return
    
    st.markdown("### 🧬 Gene-Based Trial Matcher")
    st.markdown("*Using the patient data from above to match with clinical trials*")
    
    # Show current patient data summary
    st.info(f"📊 **Current Dataset:** {len(patient_data)} patients loaded")
    
    # Backend Database Status Check
    st.markdown("**🗄️ Backend Database Status**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Check clinical trials database
        try:
            trial_count = load_backend_trial_database(check_only=True)
            st.success(f"✅ Clinical Trials DB: {trial_count:,} active trials")
        except Exception as e:
            st.error(f"❌ Clinical Trials DB: {str(e)}")
    
    with col2:
        # Show database last updated info
        st.info("🔄 Last Updated: 2025-06-20")
        st.info("📊 Database Version: v2.1")

    # Show exclusion filters
    selected_filters = create_exclusion_filters()
    
    st.markdown("---")
    
    # Enhanced button with loading state
    if st.button("🔍 **Start Matching Process**", use_container_width=True, key="start_trial_matching"):
        with create_loading_context("Loading backend database and finding matches..."):
            try:
                # Validate patient file structure
                if not validate_file_structure(patient_data, ['PatientID', 'Gene'], "Patient"):
                    return
                
                # Load backend clinical trials database
                trial_df = load_backend_trial_database()
                if trial_df.empty:
                    st.error("❌ Failed to load clinical trials database.")
                    return
                
                # Process matching
                matched_df = process_trial_matching(patient_data, trial_df, selected_filters)
                
                # Prepare additional info for display
                additional_info = []
                if selected_filters:
                    additional_info.append(f"🎛️ **Filters Applied:** {', '.join(selected_filters)}")
                
                success_rate = f"{(len(matched_df)/len(patient_data)*100):.1f}%" if not patient_data.empty else "0%"
                additional_info.extend([
                    f"📊 **Success Rate:** {success_rate}",
                    f"🗄️ **Database:** {len(trial_df):,} trials searched",
                    f"👥 **Patients Processed:** {len(patient_data)}"
                ])
                
                display_results_with_download(
                    matched_df,
                    f"🎉 Successfully found {len(matched_df)} matches!",
                    f"clinical_trial_matches_{date.today()}.csv",
                    additional_info
                )
                    
            except Exception as e:
                st.error(f"❌ Error processing files: {str(e)}")
                st.exception(e)

# Keep the old function for backward compatibility
def run_trial_matcher():
    """Legacy function - redirects to the unified version"""
    if 'patient_data' in st.session_state and not st.session_state['patient_data'].empty:
        run_trial_matcher_with_data(st.session_state['patient_data'])
    else:
        st.warning("⚠️ No patient data available. Please enter patient data in the main input section.")
