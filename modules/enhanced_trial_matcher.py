import streamlit as st
import pandas as pd
import re
import time
from datetime import date
from ui.components import (
    display_file_uploader_with_preview, create_exclusion_filters,
    display_results_with_download, create_loading_context,
    update_progress, simulate_progress_with_delay
)
from utils.enhanced_data_utils import (
    load_patient_data, load_trial_data, apply_exclusion_filters,
    create_gene_regex, validate_file_structure
)

def find_gene_matches(patient_row, trials_df, exclusion_filters=None):
    """
    Find gene matches with configurable exclusion filters
    
    Args:
        patient_row: Patient data row
        trials_df: Clinical trials dataframe
        exclusion_filters: List of exclusion patterns to apply
    """
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

def run_trial_matcher():
    """Enhanced trial matcher with better UX and configurable filters"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📁 Patient Data**")
        patient_file = display_file_uploader_with_preview(
            "Upload Patient VCF File", 
            ['tsv', 'txt', 'vcf'], 
            'match_patient',
            "Upload a tab-separated file with PatientID, Gene, and Phenotype columns"
        )
    
    with col2:
        st.markdown("**🧪 Clinical Trials Data**")
        trial_file = display_file_uploader_with_preview(
            "Upload Clinical Trial Database", 
            ['tsv', 'txt', 'vcf'], 
            'match_trial',
            "Upload a tab-separated file with clinical trial information",
            columns=['ClinicalTrialID', 'StudyTitle', 'StudyURL', 'StudyStatus', 'BriefSummary', 'ConditionGenePhenotype']
        )

    # Exclusion Filters Section
    selected_filters = create_exclusion_filters()
    
    st.markdown("---")
    
    # Enhanced button with loading state
    if st.button("🔍 **Start Matching Process**", use_container_width=True):
        if not patient_file or not trial_file:
            st.error("❌ Please upload both files before proceeding.")
            return

        with create_loading_context("Processing files and finding matches..."):
            try:
                patient_df = load_patient_data(patient_file)
                trial_df = load_trial_data(trial_file)
                
                # Validate file structures
                if not validate_file_structure(patient_df, ['PatientID', 'Gene', 'Phenotype'], "Patient"):
                    return
                if not validate_file_structure(trial_df, ['ClinicalTrialID', 'StudyTitle', 'StudyURL', 'StudyStatus', 'BriefSummary', 'ConditionGenePhenotype'], "Trial"):
                    return
                
                matched_df = process_trial_matching(patient_df, trial_df, selected_filters)
                
                # Prepare additional info for display
                additional_info = []
                if selected_filters:
                    additional_info.append(f"🎛️ **Filters Applied:** {', '.join(selected_filters)}")
                
                success_rate = f"{(len(matched_df)/len(patient_df)*100):.1f}%" if not patient_df.empty else "0%"
                additional_info.append(f"📊 **Success Rate:** {success_rate}")
                
                display_results_with_download(
                    matched_df,
                    f"🎉 Successfully found {len(matched_df)} matches!",
                    f"clinical_trial_matches_{date.today()}.csv",
                    additional_info
                )
                    
            except Exception as e:
                st.error(f"❌ Error processing files: {str(e)}")
