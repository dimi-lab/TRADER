import streamlit as st
import pandas as pd
import re
from datetime import date


st.markdown("""
    <style>
    body, .main, .block-container {
        background-color: #e6f2ff !important;
        font-family: 'Segoe UI', sans-serif;
        max-width: 100% !important;
        padding: 2rem 4rem;
    }
    .block-container {
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }
    .css-18e3th9 {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    h1, h2, h3 {
        color: #014f86;
        font-weight: 700;
    }
    .stButton button {
        background-color: #0d6efd;
        color: white;
        font-weight: 600;
        border-radius: 0.5rem;
        padding: 0.6rem 1.2rem;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #084298;
    }
    .stDownloadButton button {
        background-color: #198754;
        color: white;
        font-weight: bold;
        border-radius: 0.5rem;
    }
    .stProgress > div > div > div > div {
        background-color: #0d6efd;
    }
    .title-banner {
        font-size: 2rem;
        font-weight: 700;
        padding-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)


    
# -------------------- Core Utilities --------------------
def clean_column(text):
    return text.strip() if isinstance(text, str) else text

def update_progress(progress_bar, value, total):
    progress_percent = value / total
    progress_bar.progress(progress_percent, text=f"{value} out of {total}")

# -------------------- Match Functions --------------------
def find_gene_matches(patient_row, trials_df):
    gene = str(patient_row['Gene']).upper()
    gene_regex = rf'\b{gene}\b'
    exclusion_pattern = re.compile(
        r'cancer|carcinoma|tumor|leukemia|lymphoma|metastases|glioma|glioblastoma|'
        r'neoplasm|meningioma|melanoma|astrocytoma|sarcoma|AML|mesothelioma|'
        r'myeloproliferative|trauma|injury|bacter.*',
        re.IGNORECASE
    )

    mask = (
        ~trials_df['ConditionGenePhenotype'].str.contains(exclusion_pattern, na=False) &
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

def rare_disease_match(patients_df, fda_drug_list, gene_disease):
#    patients_df = pd.read_csv(patient_vcf, sep='\t', header=None, dtype=str, encoding='latin1')
#    patients_df.columns = ['PatientID', 'Gene', 'Phenotype']
    patients_df['Phenotype'] = patients_df['Phenotype'].apply(clean_column)
    fda_df = pd.read_csv(fda_drug_list, sep='\t', dtype=str, encoding='latin1')
    gene_disease_df = pd.read_csv(gene_disease, sep='\t', dtype=str, encoding='latin1')

    matched_genes = pd.merge(patients_df, gene_disease_df, left_on='Gene', right_on='Symbol')

    all_matches = []
    for _, row in matched_genes.iterrows():
        disease_name = re.escape(row['Name'])
        pattern = rf'\b{disease_name}\b'
        fda_matches = fda_df[fda_df['OrphanDesignation'].str.contains(pattern, flags=re.IGNORECASE, na=False)]
        if not fda_matches.empty:
            repeated_row = pd.DataFrame([row] * len(fda_matches)).reset_index(drop=True)
            merged = pd.concat([repeated_row, fda_matches.reset_index(drop=True)], axis=1)
            all_matches.append(merged)
    return pd.concat(all_matches, ignore_index=True).drop_duplicates() if all_matches else pd.DataFrame()

# -------------------- UI Logic --------------------
def run_trial_matcher():
    st.subheader("Rare Disease Clinical Trial Matcher")
    patient_file = st.file_uploader("Upload Patient VCF", type=['tsv', 'txt', 'vcf'], key='match_patient')
    trial_file = st.file_uploader("Upload Clinical Trial VCF", type=['tsv', 'txt', 'vcf'], key='match_trial')

    if st.button("Match Trials"):
        if not patient_file or not trial_file:
            st.error("Please upload both files.")
            return

        patient_df = pd.read_csv(patient_file, sep='\t', header=None, dtype=str, encoding='latin1')
        trial_df = pd.read_csv(trial_file, sep='\t', header=None, dtype=str, encoding='latin1')
        patient_df.columns = ['PatientID', 'Gene', 'Phenotype']
        trial_df.columns = ['ClinicalTrialID', 'StudyTitle', 'StudyURL', 'StudyStatus', 'BriefSummary', 'ConditionGenePhenotype']

        progress_total = len(patient_df)
        progress_bar = st.progress(0, text="Starting matching...")

        results = []
        for i, row in patient_df.iterrows():
            update_progress(progress_bar, i + 1, progress_total)
            match_df = find_gene_matches(row, trial_df)
            if match_df is not None:
                results.append(match_df)

        if results:
            matched_df = pd.concat(results, ignore_index=True).drop_duplicates()
            st.success(f"Found {len(matched_df)} matches.")
            st.dataframe(matched_df)
            st.download_button("Download Matches", matched_df.to_csv(index=False), file_name="clinical_trial_matches.csv", mime="text/csv")
        else:
            st.warning("No matches found.")
    return patient_file
        
def run_file_comparison():
    st.subheader("REACTOR - Reanalysis Engine for Assessing Clinical Trials in Orphan Rare Diseases")
    original_file = st.file_uploader("Upload Original File", type=["csv", 'txt'], key="Original Matched File")
    updated_file = st.file_uploader("Upload Updated File", type=["csv", 'txt'], key="Updated Matched File")

    if st.button("Compare Files"):
        if not original_file or not updated_file:
            st.error("Both files must be uploaded.")
            return

        original_df = pd.read_csv(original_file, encoding='latin1')
        updated_df = pd.read_csv(updated_file, encoding='latin1')
        original_df = original_df[original_df['PatientID'] != 'PatientID']
        updated_df = updated_df[updated_df['PatientID'] != 'PatientID']

        progress_total = len(updated_df)
        progress_bar = st.progress(0, text="Comparing records...")

        new_matches = pd.DataFrame()
        for i, row in updated_df.iterrows():
            if row['PatientID'] not in original_df['PatientID'].values:
                new_matches = pd.concat([new_matches, pd.DataFrame([row])], ignore_index=True)
            update_progress(progress_bar, i + 1, progress_total)

        st.success(f"Found {len(new_matches)} new patients.")
        st.dataframe(new_matches)
        st.download_button("Download Comparison Results", new_matches.to_csv(index=False), file_name=f"comparison_results_{date.today()}.csv", mime="text/csv")

def run_rare_disease_match():
    st.subheader("Rare Disease Drug Matcher")
    patient_file = st.file_uploader("Upload Patient VCF", type=['tsv', 'txt', 'vcf'], key='Patient VCF file')
    fda_list = st.file_uploader("FDA Drug List", type=["tsv", 'txt'], key="FDA Orphan Designated Drug List")
    gene_disease = st.file_uploader("Gene-Disease Map", type=["tsv", 'txt'], key="Gene-Disease File")

    if st.button("Run Rare Disease Match"):
        if not (fda_list and gene_disease):
            st.error("All three files are required.")
            return

        patients_df = pd.read_csv(patient_file, sep='\t', header=None, dtype=str, encoding='latin1')
        patients_df.columns = ['PatientID', 'Gene', 'Phenotype']
        progress_total = len(patients_df)
        progress_bar = st.progress(0, text="Starting match...")

        matches = rare_disease_match(patients_df, fda_list, gene_disease)
        for i in range(progress_total):
            update_progress(progress_bar, i + 1, progress_total)

        st.success(f"Rare disease matching complete. Found {len(matches)} matches.")
        st.dataframe(matches)
        st.download_button("Download Rare Disease Matches", matches.to_csv(index=False),
                           file_name=f"rare_disease_matches_{date.today()}.csv", mime="text/csv")

#col1, col2 = st.columns([2, 3])
#with col1:
st.image("trader_image_new.png", width=600)
#with col2:
#    st.markdown('<div class="title-banner">TRADER — Trials and Drugs Explorer for Rare Diseases</div>', unsafe_allow_html=True)
#    st.markdown("Explore and match patients with clinical trials and FDA-designated orphan drugs for rare diseases.")

# --- Main Section Buttons ---
st.markdown("---")
with st.container():
    st.subheader("🧬 Gene-Based Trial Matcher")
    run_trial_matcher()

    st.subheader("📊 Compare Uploaded Patient Files")
    run_file_comparison()

    st.subheader("💊 Rare Disease Drug Matches")
    run_rare_disease_match()
# -------------------- Main App --------------------
#st.title("TRADER -Trails and Drugs Explorer for Rare Diseases")
#col1, col2 = st.columns([1, 1])
#with col1:
#    st.image("trader_logo.png", width=600)
#with col2:
#    st.write("")
#    st.button("Get Started")
#    run_trial_matcher()
#    run_file_comparison()
#    run_rare_disease_match()

