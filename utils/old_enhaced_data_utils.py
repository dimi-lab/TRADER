import pandas as pd
import streamlit as st
import re
from pathlib import Path

import streamlit as st
import pandas as pd
import io
import re
from pathlib import Path

def parse_vcf_file(uploaded_file):
    """Parse VCF file and extract relevant information"""
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Read file content
        content = uploaded_file.read().decode('utf-8')
        lines = content.split('\n')
        
        # Skip header lines that start with #
        data_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        
        if not data_lines:
            st.error("No data lines found in VCF file")
            return pd.DataFrame()
        
        # Parse VCF columns: CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, FORMAT, SAMPLE...
        vcf_data = []
        for i, line in enumerate(data_lines):
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 5:
                    # Extract basic VCF information
                    chrom = parts[0]
                    pos = parts[1]
                    variant_id = parts[2] if parts[2] != '.' else f"{chrom}:{pos}"
                    ref = parts[3]
                    alt = parts[4]
                    
                    # Create a patient entry
                    patient_id = f"Patient_{i+1}"  # Generate patient ID
                    gene = variant_id  # Use variant ID as gene for now
                    phenotype = f"Variant {chrom}:{pos} {ref}>{alt}"
                    
                    vcf_data.append({
                        'PatientID': patient_id,
                        'Gene': gene,
                        'Phenotype': phenotype,
                        'Chromosome': chrom,
                        'Position': pos,
                        'Reference': ref,
                        'Alternate': alt
                    })
        
        return pd.DataFrame(vcf_data)
        
    except Exception as e:
        st.error(f"Error parsing VCF file: {str(e)}")
        return pd.DataFrame()

def parse_excel_file(uploaded_file):
    """Parse Excel file with multiple encoding support"""
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        return df
        
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return pd.DataFrame()

def parse_csv_file(uploaded_file):
    """Parse CSV file with multiple encoding and delimiter support"""
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Try different encodings and delimiters
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        delimiters = [',', '\t', ';', '|']
        
        for encoding in encodings:
            for delimiter in delimiters:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=encoding, sep=delimiter)
                    
                    # Check if we got reasonable data
                    if len(df.columns) >= 2 and len(df) > 0:
                        # Clean column names
                        df.columns = df.columns.str.strip()
                        return df
                        
                except:
                    continue
        
        st.error("Could not parse CSV file with any encoding/delimiter combination")
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error reading CSV file: {str(e)}")
        return pd.DataFrame()

def parse_text_input(text_input):
    """Parse free text input into structured data"""
    try:
        lines = text_input.strip().split('\n')
        data = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Try different separators
            separators = ['\t', ',', ';', '|', '  ']  # Including double space
            
            parts = None
            for sep in separators:
                test_parts = [p.strip() for p in line.split(sep) if p.strip()]
                if len(test_parts) >= 2:  # At least PatientID and Gene
                    parts = test_parts
                    break
            
            if not parts:
                # Try space separation as last resort
                parts = [p.strip() for p in line.split() if p.strip()]
            
            if len(parts) >= 2:
                patient_id = parts[0] if parts[0] else f"Patient_{i+1}"
                gene = parts[1] if len(parts) > 1 else ""
                phenotype = parts[2] if len(parts) > 2 else ""
                
                # If only 2 parts, assume second is phenotype
                if len(parts) == 2:
                    gene = parts[1]
                    phenotype = ""
                
                data.append({
                    'PatientID': patient_id,
                    'Gene': gene,
                    'Phenotype': phenotype
                })
        
        if not data:
            st.error("Could not parse any valid data from text input")
            return pd.DataFrame()
        
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"Error parsing text input: {str(e)}")
        return pd.DataFrame()

def standardize_patient_data(df):
    """Standardize patient data to required format"""
    try:
        # Create a copy to avoid modifying original
        standardized_df = df.copy()
        
        # Map common column variations to standard names
        column_mappings = {
            'PatientID': ['patient_id', 'patientid', 'id', 'sample_id', 'sample'],
            'Gene': ['gene', 'gene_symbol', 'symbol', 'gene_name', 'variant_id'],
            'Phenotype': ['phenotype', 'condition', 'disease', 'description', 'clinical_notes']
        }
        
        # Apply column mappings
        for standard_col, variations in column_mappings.items():
            if standard_col not in standardized_df.columns:
                for var in variations:
                    if var in standardized_df.columns:
                        standardized_df[standard_col] = standardized_df[var]
                        break
                    # Check case-insensitive
                    for col in standardized_df.columns:
                        if col.lower() == var.lower():
                            standardized_df[standard_col] = standardized_df[col]
                            break
        
        # Ensure required columns exist
        required_columns = ['PatientID', 'Gene', 'Phenotype']
        for col in required_columns:
            if col not in standardized_df.columns:
                standardized_df[col] = ''
        
        # Clean data
        for col in required_columns:
            standardized_df[col] = standardized_df[col].astype(str).str.strip()
        
        # Filter out completely empty rows
        standardized_df = standardized_df[
            (standardized_df['PatientID'] != '') | 
            (standardized_df['Gene'] != '') | 
            (standardized_df['Phenotype'] != '')
        ]
        
        return standardized_df[required_columns]
        
    except Exception as e:
        st.error(f"Error standardizing data: {str(e)}")
        return pd.DataFrame()

def create_enhanced_patient_input():
    """Create enhanced patient input interface with multiple options"""
    
    st.markdown("**📁 Patient Data Input**")
    st.markdown("*Choose your preferred method to input patient genetic data*")
    
    # Input method selection
    input_method = st.radio(
        "Select input method:",
        ["📄 Upload File", "✏️ Text Input"],
        horizontal=True
    )
    
    patient_data = pd.DataFrame()
    
    if input_method == "📄 Upload File":
        st.markdown("**Supported formats:** VCF, CSV, TSV, TXT, Excel (XLSX, XLS)")
        
        uploaded_file = st.file_uploader(
            "Upload Patient Data File",
            type=['vcf', 'csv', 'tsv', 'txt', 'xlsx', 'xls'],
            help="Upload a file containing PatientID, Gene, and Phenotype data"
        )
        
        if uploaded_file:
            file_extension = Path(uploaded_file.name).suffix.lower()
            
            with st.spinner(f"Processing {file_extension} file..."):
                if file_extension == '.vcf':
                    patient_data = parse_vcf_file(uploaded_file)
                elif file_extension in ['.xlsx', '.xls']:
                    patient_data = parse_excel_file(uploaded_file)
                elif file_extension in ['.csv', '.tsv', '.txt']:
                    patient_data = parse_csv_file(uploaded_file)
                else:
                    st.error(f"Unsupported file format: {file_extension}")
            
            if not patient_data.empty:
                # Standardize the data
                patient_data = standardize_patient_data(patient_data)
                
                if not patient_data.empty:
                    st.success(f"✅ Successfully loaded {len(patient_data)} patient records!")
                    
                    # Show preview
                    st.markdown("**Preview:**")
                    st.dataframe(patient_data.head(), use_container_width=True)
                else:
                    st.error("❌ No valid patient data found after processing")
    
    elif input_method == "✏️ Text Input":
        st.markdown("**Format:** Enter patient data with each patient on a new line")
        st.markdown("**Columns:** PatientID, Gene, Phenotype (separated by tabs, commas, or spaces)")
        
        # Example text
        example_text = """Patient001	BRCA1	Breast cancer susceptibility
Patient002	TP53	Li-Fraumeni syndrome
Patient003	CFTR	Cystic fibrosis"""
        
        with st.expander("📋 Show Example Format"):
            st.code(example_text, language="text")
            st.markdown("**Supported separators:** Tabs, commas, semicolons, pipes (|), or spaces")
        
        text_input = st.text_area(
            "Enter patient data:",
            height=200,
            placeholder="Patient001\tBRCA1\tBreast cancer\nPatient002\tTP53\tLi-Fraumeni syndrome\n..."
        )
        
        if text_input.strip():
            with st.spinner("Processing text input..."):
                patient_data = parse_text_input(text_input)
            
            if not patient_data.empty:
                # Standardize the data
                patient_data = standardize_patient_data(patient_data)
                
                if not patient_data.empty:
                    st.success(f"✅ Successfully parsed {len(patient_data)} patient records!")
                    
                    # Show preview
                    st.markdown("**Preview:**")
                    st.dataframe(patient_data, use_container_width=True)
                else:
                    st.error("❌ No valid patient data found after processing")
    
    # Data validation and editing
    if not patient_data.empty:
        st.markdown("---")
        st.markdown("**📝 Data Validation & Editing**")
        
        # Show data quality metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            missing_ids = patient_data['PatientID'].isna().sum() + (patient_data['PatientID'] == '').sum()
            st.metric("Missing Patient IDs", missing_ids)
        
        with col2:
            missing_genes = patient_data['Gene'].isna().sum() + (patient_data['Gene'] == '').sum()
            st.metric("Missing Genes", missing_genes)
        
        with col3:
            missing_phenotypes = patient_data['Phenotype'].isna().sum() + (patient_data['Phenotype'] == '').sum()
            st.metric("Missing Phenotypes", missing_phenotypes)
        
        # Option to edit data
        if st.checkbox("🖊️ Edit data before processing"):
            patient_data = st.data_editor(
                patient_data,
                use_container_width=True,
                num_rows="dynamic"
            )
        
        # Final validation
        valid_rows = (patient_data['PatientID'] != '') & (patient_data['Gene'] != '')
        valid_data = patient_data[valid_rows]
        
        if len(valid_data) < len(patient_data):
            st.warning(f"⚠️ {len(patient_data) - len(valid_data)} rows will be excluded due to missing PatientID or Gene")
        
        if len(valid_data) > 0:
            st.info(f"✅ {len(valid_data)} valid patient records ready for processing")
            return valid_data
        else:
            st.error("❌ No valid records found. Please ensure each patient has at least PatientID and Gene.")
            return pd.DataFrame()
    
    return patient_data


def clean_column(text):
    """Clean text data for matching"""
    if pd.isna(text):
        return ""
    return str(text).strip().lower()

def load_csv_data(uploaded_file, file_type="patient"):
    """Legacy function name for backwards compatibility"""
    return load_patient_data(uploaded_file)

def load_patient_data(uploaded_file):
    """Load patient data with multiple encoding support"""
    try:
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep='\t', encoding=encoding)
                
                # Clean column names
                df.columns = df.columns.str.strip()
                
                # Remove any completely empty rows
                df = df.dropna(how='all')
                
                # Convert to string and clean
                for col in df.columns:
                    if col in ['PatientID', 'Gene', 'Phenotype']:
                        df[col] = df[col].astype(str).str.strip()
                
                return df
                
            except UnicodeDecodeError:
                continue
        
        # If all encodings fail
        st.error("Could not decode file with any standard encoding")
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"Error loading patient data: {str(e)}")
        return pd.DataFrame()

def load_trial_data(uploaded_file):
    """Load trial data - alias for patient data loader"""
    return load_patient_data(uploaded_file)

def filter_valid_patients(df):
    """Filter out invalid patient records"""
    if df.empty:
        return df
    
    # Remove rows where essential columns are missing or empty
    required_cols = ['PatientID', 'Gene']
    for col in required_cols:
        if col in df.columns:
            df = df[df[col].notna() & (df[col] != '') & (df[col] != 'nan')]
    
    return df

def validate_file_structure(df, required_columns, file_type):
    """Validate that the uploaded file has the required structure"""
    if df.empty:
        st.error(f"❌ {file_type} file is empty")
        return False
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(f"❌ {file_type} file missing required columns: {', '.join(missing_columns)}")
        st.info(f"Expected columns: {', '.join(required_columns)}")
        st.info(f"Found columns: {', '.join(df.columns.tolist())}")
        return False
    
    return True

def create_gene_regex(gene):
    """Create regex pattern for gene matching"""
    return rf'\b{re.escape(gene)}\b'

def apply_exclusion_filters(trials_df, exclusion_filters):
    """Apply exclusion filters to trials dataframe"""
    if not exclusion_filters:
        return pd.Series([True] * len(trials_df))
    
    # Define exclusion patterns for each category
    exclusion_patterns = {
        'Cancer/Oncology': r'\b(cancer|carcinoma|tumor|tumour|leukemia|leukaemia|lymphoma|oncol|malignant|neoplasm|metasta)\b',
        'Trauma/Injury': r'\b(trauma|injury|wound|burn|fracture|accident|emergency)\b',
        'Infectious Disease': r'\b(infection|bacterial|viral|sepsis|pneumonia|covid|influenza|hepatitis)\b',
        'Cardiovascular': r'\b(cardiac|heart|cardio|coronary|stroke|myocardial|angina|arrhythmia)\b',
        'Neurological': r'\b(alzheimer|parkinson|dementia|epilepsy|seizure|neurolog|brain|cognitive)\b',
        'Psychiatric': r'\b(depression|anxiety|bipolar|schizophrenia|psychiatric|mental|mood)\b',
        'Metabolic': r'\b(diabetes|diabetic|obesity|obese|metabolic|syndrome|glucose)\b',
        'Autoimmune': r'\b(arthritis|lupus|inflammatory|bowel|disease|autoimmune|rheumat)\b'
    }
    
    # Start with all trials included
    mask = pd.Series([True] * len(trials_df))
    
    # Apply each selected filter
    for filter_name in exclusion_filters:
        if filter_name in exclusion_patterns:
            pattern = exclusion_patterns[filter_name]
            # Exclude trials that match the pattern
            exclusion_mask = (
                trials_df['StudyTitle'].str.contains(pattern, case=False, na=False) |
                trials_df['BriefSummary'].str.contains(pattern, case=False, na=False)
            )
            mask = mask & ~exclusion_mask
    
    return mask

# Backend database loading functions

def load_backend_trial_database(check_only=False):
    """Load backend clinical trials database"""
    try:
        # Get from session state first
        if 'databases' in st.session_state:
            db = st.session_state['databases'].get('clinical_trials')
            if db is not None:
                if check_only:
                    return len(db)
                return db
        
        # Fallback to file loading
        base_path = Path(__file__).parent.parent
        file_path = base_path / 'matched_clinical_trials_20240716_cleaned.test.csv'
        
        if file_path.exists():
            df = pd.read_csv(file_path, encoding='utf-8')
            if check_only:
                return len(df)
            return df
        else:
            if check_only:
                return 0
            return pd.DataFrame()
            
    except Exception as e:
        if check_only:
            raise e
        st.error(f"Error loading clinical trials database: {str(e)}")
        return pd.DataFrame()

def load_backend_gene_disease_database(check_only=False):
    """Load backend gene-disease database"""
    try:
        # Get from session state first
        if 'databases' in st.session_state:
            db = st.session_state['databases'].get('gene_disease')
            if db is not None:
                if check_only:
                    return len(db)
                return db
        
        # Fallback to file loading
        base_path = Path(__file__).parent.parent
        file_path = base_path / 'gene_disease.test.txt'
        
        if file_path.exists():
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
            if check_only:
                return len(df)
            return df
        else:
            if check_only:
                return 0
            return pd.DataFrame()
            
    except Exception as e:
        if check_only:
            raise e
        st.error(f"Error loading gene-disease database: {str(e)}")
        return pd.DataFrame()

def load_backend_orphan_drugs_database(check_only=False):
    """Load backend orphan drugs database"""
    try:
        # Get from session state first
        if 'databases' in st.session_state:
            db = st.session_state['databases'].get('orphan_drugs')
            if db is not None:
                if check_only:
                    return len(db)
                return db
        
        # Fallback to file loading
        base_path = Path(__file__).parent.parent
        file_path = base_path / 'orphan_drugs.test.txt'
        
        if file_path.exists():
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
            if check_only:
                return len(df)
            return df
        else:
            if check_only:
                return 0
            return pd.DataFrame()
            
    except Exception as e:
        if check_only:
            raise e
        st.error(f"Error loading orphan drugs database: {str(e)}")
        return pd.DataFrame()

def load_backend_reactor_database(check_only=False):
    """Load backend REACTOR database"""
    try:
        # Get from session state first
        if 'databases' in st.session_state:
            db = st.session_state['databases'].get('rare_disease_matches')
            if db is not None:
                if check_only:
                    return len(db)
                return db
        
        # Fallback to file loading
        base_path = Path(__file__).parent.parent
        file_path = base_path / 'rare_disease_matches_20240716_cleaned.test.csv'
        
        if file_path.exists():
            df = pd.read_csv(file_path, encoding='utf-8')
            if check_only:
                return len(df)
            return df
        else:
            if check_only:
                return 0
            return pd.DataFrame()
            
    except Exception as e:
        if check_only:
            raise e
        st.error(f"Error loading REACTOR database: {str(e)}")
        return pd.DataFrame()
