import pandas as pd
import re
import streamlit as st

def clean_column(text):
    """Clean column text by stripping whitespace"""
    return text.strip() if isinstance(text, str) else text

def load_patient_data(file):
    """Load and validate patient data from uploaded file"""
    try:
        df = pd.read_csv(file, sep='\t', header=None, dtype=str, encoding='latin1')
        df.columns = ['PatientID', 'Gene', 'Phenotype']
        return df
    except Exception as e:
        st.error(f"❌ Error loading patient data: {str(e)}")
        return pd.DataFrame()

def load_trial_data(file):
    """Load and validate clinical trial data from uploaded file"""
    try:
        df = pd.read_csv(file, sep='\t', header=None, dtype=str, encoding='latin1')
        df.columns = ['ClinicalTrialID', 'StudyTitle', 'StudyURL', 'StudyStatus', 'BriefSummary', 'ConditionGenePhenotype']
        return df
    except Exception as e:
        st.error(f"❌ Error loading trial data: {str(e)}")
        return pd.DataFrame()

def load_csv_data(file):
    """Load CSV data from uploaded file with error handling"""
    try:
        return pd.read_csv(file, encoding='latin1')
    except Exception as e:
        st.error(f"❌ Error loading CSV data: {str(e)}")
        return pd.DataFrame()

def filter_valid_patients(df):
    """Filter out invalid patient records"""
    return df[df['PatientID'] != 'PatientID']

def load_local_database_files(gene_disease_path="gene_disease.txt", orphan_drugs_path="orphan_drugs.txt"):
    """Load local database files with comprehensive error handling"""
    try:
        gene_disease_df = pd.read_csv(gene_disease_path, sep='\t', dtype=str, encoding='latin1')
        st.info(f"📊 Loaded gene-disease database: {len(gene_disease_df)} entries")
    except FileNotFoundError:
        st.error("❌ gene_disease.txt not found. Please ensure the file exists in the app directory.")
        return None, None
    except Exception as e:
        st.error(f"❌ Error loading gene-disease database: {str(e)}")
        return None, None
    
    try:
        orphan_df = pd.read_csv(orphan_drugs_path, sep='\t', dtype=str, encoding='latin1')
        st.info(f"💊 Loaded orphan drugs database: {len(orphan_df)} entries")
    except FileNotFoundError:
        st.error("❌ orphan_drugs.txt not found. Please ensure the file exists in the app directory.")
        return None, None
    except Exception as e:
        st.error(f"❌ Error loading orphan drugs database: {str(e)}")
        return None, None
    
    return gene_disease_df, orphan_df

def create_exclusion_patterns():
    """Create comprehensive exclusion patterns for different condition categories"""
    return {
        'Cancer/Oncology': r'cancer|carcinoma|tumor|leukemia|lymphoma|metastases|glioma|glioblastoma|neoplasm|meningioma|melanoma|astrocytoma|sarcoma|AML|mesothelioma|myeloproliferative',
        'Trauma/Injury': r'trauma|injury|wound|burn|fracture|accident',
        'Infectious Disease': r'bacter|viral|infection|sepsis|pneumonia|influenza|covid',
        'Cardiovascular': r'cardiac|heart|coronary|myocardial|cardiovascular|stroke',
        'Neurological': r'alzheimer|parkinson|dementia|epilepsy|seizure|migraine',
        'Psychiatric': r'depression|anxiety|bipolar|schizophrenia|psychiatric',
        'Metabolic': r'diabetes|obesity|metabolic syndrome|hypertension',
        'Autoimmune': r'arthritis|lupus|autoimmune|inflammatory bowel'
    }

def apply_exclusion_filters(trials_df, exclusion_filters):
    """Apply selected exclusion filters to trials dataframe"""
    if not exclusion_filters or len(exclusion_filters) == 0:
        return pd.Series([True] * len(trials_df))
    
    default_exclusions = create_exclusion_patterns()
    patterns = []
    
    for filter_name in exclusion_filters:
        if filter_name in default_exclusions:
            patterns.append(default_exclusions[filter_name])
    
    if patterns:
        exclusion_pattern = re.compile('|'.join(patterns), re.IGNORECASE)
        return ~trials_df['ConditionGenePhenotype'].str.contains(exclusion_pattern, na=False)
    
    return pd.Series([True] * len(trials_df))

def validate_file_structure(df, expected_columns, file_type=""):
    """Validate that uploaded file has expected structure"""
    if df.empty:
        st.error(f"❌ {file_type} file appears to be empty.")
        return False
    
    if len(df.columns) != len(expected_columns):
        st.error(f"❌ {file_type} file should have {len(expected_columns)} columns: {', '.join(expected_columns)}")
        return False
    
    return True

def create_gene_regex(gene):
    """Create regex pattern for gene matching"""
    return rf'\b{str(gene).upper()}\b'

def calculate_match_statistics(results_df, patients_df):
    """Calculate comprehensive matching statistics"""
    if results_df.empty:
        return {}
    
    stats = {
        "Total Matches": len(results_df),
        "Unique Patients": results_df['PatientID'].nunique() if 'PatientID' in results_df.columns else 0,
        "Success Rate": f"{(len(results_df)/len(patients_df)*100):.1f}%" if not patients_df.empty else "0%"
    }
    
    # Add conditional statistics based on available columns
    if 'ClinicalTrialID' in results_df.columns:
        stats["Unique Trials"] = results_df['ClinicalTrialID'].nunique()
    
    if 'GenericName' in results_df.columns:
        stats["Unique Drugs"] = results_df['GenericName'].nunique()
    
    if 'SponsorCompany' in results_df.columns:
        stats["Companies"] = results_df['SponsorCompany'].nunique()
    
    return stats
