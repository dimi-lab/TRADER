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
    """Find gene matches with configurable exclusion filters - FIXED VERSION"""
    try:
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
            # FIXED: Create results manually to avoid column conflicts
            results = []
            
            # For each matching trial, create a row with patient info + trial info
            for _, trial_row in matches.iterrows():
                combined_row = {}
                
                # Add patient information with prefix
                for col in patient_row.index:
                    combined_row[f"Patient_{col}"] = patient_row[col]
                
                # Add trial information with prefix
                for col in trial_row.index:
                    combined_row[f"Trial_{col}"] = trial_row[col]
                
                results.append(combined_row)
            
            # Convert to DataFrame
            if results:
                combined_df = pd.DataFrame(results)
                return combined_df
        
        return None
        
    except Exception as e:
        # Log error but don't stop processing
        patient_id = patient_row.get('Gene', 'Unknown')
        st.warning(f"⚠️ Error processing gene {patient_id}: {str(e)}")
        return None

def process_trial_matching(patient_df, trial_df, exclusion_filters):
    """Process trial matching for all patients with progress tracking - ENHANCED VERSION"""
    
    # Show debug info in an expander
    with st.expander("🔍 Debug Information", expanded=False):
        st.write(f"**Patient data shape:** {patient_df.shape}")
        st.write(f"**Patient columns:** {list(patient_df.columns)}")
        st.write(f"**Trial data shape:** {trial_df.shape}")
        st.write(f"**Trial columns (first 10):** {list(trial_df.columns)[:10]}")
        
        # Show sample data
        if not patient_df.empty:
            st.write("**Sample patient data:**")
            st.dataframe(patient_df.head(2), use_container_width=True)
    
    progress_total = len(patient_df)
    progress_bar = st.progress(0, text="Initializing matching algorithm...")

    results = []
    failed_count = 0
    
    for i, row in patient_df.iterrows():
        try:
            update_progress(progress_bar, i + 1, progress_total, f"Processing patient {i+1}")
            match_df = find_gene_matches(row, trial_df, exclusion_filters)
            if match_df is not None and len(match_df) > 0:
                results.append(match_df)
        except Exception as e:
            failed_count += 1
            patient_id = row.get('PatientID', f'Patient_{i+1}')
            st.warning(f"⚠️ Failed to process {patient_id}: {str(e)}")
            continue
        
        time.sleep(0.01)  # Small delay for visual effect

    # Show summary
    if failed_count > 0:
        st.warning(f"⚠️ {failed_count} patients failed to process")
    
    if results:
        try:
            # Combine all results
            matched_df = pd.concat(results, ignore_index=True)
            
            # Remove exact duplicates
            initial_rows = len(matched_df)
            matched_df = matched_df.drop_duplicates()
            final_rows = len(matched_df)
            
            if initial_rows > final_rows:
                st.info(f"ℹ️ Removed {initial_rows - final_rows} duplicate matches")
            
            st.success(f"✅ Successfully processed {len(patient_df) - failed_count}/{len(patient_df)} patients")
            return matched_df
            
        except Exception as e:
            st.error(f"❌ Error combining results: {str(e)}")
            return pd.DataFrame()
    
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
            
            # Show file date if available
            if 'databases' in st.session_state and st.session_state['databases'].get('file_dates'):
                file_date = st.session_state['databases']['file_dates'].get('clinical_trials', 'Unknown')
                st.info(f"📅 File Date: {file_date}")
            
        except Exception as e:
            st.error(f"❌ Clinical Trials DB: {str(e)}")
    
    with col2:
        # Show database version info
        st.info("📊 Database Version: v2.1")
        st.info("🔄 System Status: Active")

    # Show exclusion filters
    selected_filters = create_exclusion_filters()
    
    st.markdown("---")
    
    # Enhanced button with loading state
    if st.button("🔍 **Start Matching Process**", use_container_width=True, key="start_trial_matching"):
        with create_loading_context("Loading backend database and finding matches..."):
            try:
                # Validate patient file structure
                required_columns = ['PatientID', 'Gene']
                if not validate_file_structure(patient_data, required_columns, "Patient"):
                    st.error("❌ Patient data validation failed.")
                    return
                
                # Load backend clinical trials database
                trial_df = load_backend_trial_database()
                if trial_df.empty:
                    st.error("❌ Failed to load clinical trials database.")
                    return
                
                # Validate trial database has required columns
                required_trial_columns = ['StudyTitle', 'BriefSummary']
                missing_trial_cols = [col for col in required_trial_columns if col not in trial_df.columns]
                if missing_trial_cols:
                    st.error(f"❌ Trial database missing columns: {', '.join(missing_trial_cols)}")
                    return
                
                # Process matching
                matched_df = process_trial_matching(patient_data, trial_df, selected_filters)
                
                # Prepare additional info for display
                additional_info = []
                if selected_filters:
                    additional_info.append(f"🎛️ **Filters Applied:** {', '.join(selected_filters)}")
                
                if len(matched_df) > 0:
                    success_rate = f"{(len(matched_df)/len(patient_data)*100):.1f}%"
                    additional_info.extend([
                        f"📊 **Success Rate:** {success_rate}",
                        f"🗄️ **Database:** {len(trial_df):,} trials searched",
                        f"👥 **Patients Processed:** {len(patient_data)}",
                        f"🎯 **Total Matches:** {len(matched_df)}"
                    ])
                    
                    success_message = f"🎉 Successfully found {len(matched_df)} matches!"
                else:
                    success_message = "🔍 No matches found."
                    additional_info.extend([
                        "💡 **Suggestions:**",
                        "- Check gene names in your patient data",
                        "- Try different exclusion filter combinations",
                        "- Verify gene symbols match clinical trial descriptions"
                    ])
                
                display_results_with_download(
                    matched_df,
                    success_message,
                    f"clinical_trial_matches_{date.today()}.csv",
                    additional_info
                )
                    
            except Exception as e:
                st.error(f"❌ Error processing trial matching: {str(e)}")
                st.exception(e)

# Keep the old function for backward compatibility
def run_trial_matcher():
    """Legacy function - redirects to the unified version"""
    if 'patient_data' in st.session_state and not st.session_state['patient_data'].empty:
        run_trial_matcher_with_data(st.session_state['patient_data'])
    else:
        st.warning("⚠️ No patient data available. Please enter patient data in the main input section.")
