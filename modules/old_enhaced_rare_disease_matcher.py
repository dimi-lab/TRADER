import streamlit as st
import pandas as pd
import re
import time
from datetime import date
from ui.components import (
    display_file_uploader_with_preview, display_results_with_download,
    create_loading_context, update_progress, simulate_progress_with_delay
)
from utils.enhanced_data_utils import (
    clean_column, load_patient_data, load_backend_gene_disease_database,
    load_backend_orphan_drugs_database, validate_file_structure
)

def find_rare_disease_matches(patients_df, gene_disease_df, orphan_df):
    """Find matches between patients and FDA orphan designated drugs"""
    # Clean phenotype data
    patients_df['Phenotype'] = patients_df['Phenotype'].apply(clean_column)
    
    # Merge patients with gene-disease mapping
    matched_genes = pd.merge(patients_df, gene_disease_df, left_on='Gene', right_on='Symbol')

    all_matches = []
    for _, row in matched_genes.iterrows():
        disease_name = re.escape(row['Name'])
        pattern = rf'\b{disease_name}\b'
        
        # Search in OrphanDesignation column of orphan drugs
        orphan_matches = orphan_df[orphan_df['OrphanDesignation'].str.contains(
            pattern, flags=re.IGNORECASE, na=False
        )]
        
        if not orphan_matches.empty:
            repeated_row = pd.DataFrame([row] * len(orphan_matches)).reset_index(drop=True)
            merged = pd.concat([repeated_row, orphan_matches.reset_index(drop=True)], axis=1)
            all_matches.append(merged)
    
    return pd.concat(all_matches, ignore_index=True).drop_duplicates() if all_matches else pd.DataFrame()

def process_rare_disease_matching(patients_df):
    """Process rare disease matching with backend database integration"""
    # Load backend database files
    gene_disease_df = load_backend_gene_disease_database()
    orphan_df = load_backend_orphan_drugs_database()
    
    if gene_disease_df.empty or orphan_df.empty:
        return pd.DataFrame()
    
    # Progress tracking
    progress_total = len(patients_df)
    progress_bar = st.progress(0, text="Processing rare disease matches...")
    
    matches = find_rare_disease_matches(patients_df, gene_disease_df, orphan_df)
    
    # Simulate progress for better UX
    simulate_progress_with_delay(progress_bar, progress_total, "Matching drugs")
    
    return matches

def run_rare_disease_match():
    """Enhanced rare disease matcher with backend database integration"""
    
    st.markdown("**💊 Rare Disease Drug Matcher**")
    st.markdown("*Connect patients with FDA-designated orphan drugs using integrated gene-disease databases*")
    
    # Patient file upload with enhanced preview
    st.markdown("**📁 Patient Data Upload**")
    patient_file = display_file_uploader_with_preview(
        "Upload Patient VCF File", 
        ['tsv', 'txt', 'vcf'], 
        'patient_vcf_rare_enhanced',
        "Patient genetic data file with PatientID, Gene, and Phenotype columns"
    )
    
    # Backend Database status check
    st.markdown("---")
    st.markdown("**📊 Backend Database Status**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            gene_disease_count = load_backend_gene_disease_database(check_only=True)
            st.success(f"✅ Gene-Disease DB: {gene_disease_count:,} entries")
        except Exception as e:
            st.error(f"❌ Gene-Disease DB: {str(e)}")
    
    with col2:
        try:
            orphan_count = load_backend_orphan_drugs_database(check_only=True)
            st.success(f"✅ Orphan Drugs DB: {orphan_count:,} entries")
        except Exception as e:
            st.error(f"❌ Orphan Drugs DB: {str(e)}")
    
    # Additional database info
    col3, col4 = st.columns(2)
    with col3:
        st.info("🔄 Last Updated: 2025-06-20")
    with col4:
        st.info("📊 Database Version: v4.1")
    
    st.markdown("---")
    
    # Enhanced matching button
    if st.button("🔬 **Run Comprehensive Drug Matching**", use_container_width=True):
        if not patient_file:
            st.error("❌ Please upload patient data first.")
            return
        
        with create_loading_context("Loading backend databases and analyzing rare disease drug matches..."):
            try:
                # Load and validate patient data
                patients_df = load_patient_data(patient_file)
                
                if not validate_file_structure(patients_df, ['PatientID', 'Gene', 'Phenotype'], "Patient"):
                    return
                
                # Process matching with backend databases
                matches = process_rare_disease_matching(patients_df)
                
                # Prepare comprehensive statistics and insights
                additional_info = []
                
                if len(matches) > 0:
                    # Calculate detailed statistics
                    unique_drugs = matches['GenericName'].nunique() if 'GenericName' in matches.columns else 0
                    unique_companies = matches['SponsorCompany'].nunique() if 'SponsorCompany' in matches.columns else 0
                    unique_diseases = matches['Name'].nunique() if 'Name' in matches.columns else 0
                    
                    # Additional insights
                    if 'OrphanDesignationStatus' in matches.columns:
                        designated_matches = len(matches[matches['OrphanDesignationStatus'] == 'Designated'])
                        additional_info.append(f"📊 **{designated_matches}** matches have designated orphan status")
                    
                    if unique_companies > 0:
                        additional_info.append(f"🏢 **{unique_companies}** different pharmaceutical companies involved")
                    
                    if unique_diseases > 0:
                        additional_info.append(f"🦠 **{unique_diseases}** distinct disease types matched")
                    
                    additional_info.extend([
                        f"👥 **Patients Processed:** {len(patients_df)}",
                        f"💊 **Unique Drugs Found:** {unique_drugs}"
                    ])
                    
                    success_message = f"🎯 Found {len(matches)} potential drug matches!"
                else:
                    success_message = "🔍 No matches found."
                    additional_info.extend([
                        "💡 **Suggestions:**",
                        "- Check gene names in your patient file",
                        "- Verify gene symbols match the database",
                        "- Consider that not all rare diseases have orphan drug designations"
                    ])
                
                display_results_with_download(
                    matches,
                    success_message,
                    f"rare_disease_matches_{date.today()}.csv",
                    additional_info
                )
            
            except Exception as e:
                st.error(f"❌ Error processing rare disease matches: {str(e)}")

                
