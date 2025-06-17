import streamlit as st
import pandas as pd
import re
from datetime import date
import time

# -------------------- Enhanced Styling --------------------
st.set_page_config(
    page_title="TRADER - Rare Disease Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    .main {
        padding-top: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 100% !important;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }
    
    /* Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        text-align: center;
        color: #6c757d;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* Card styling */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        transition: all 0.3s ease;
        border-left: 4px solid #667eea;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .card-icon {
        font-size: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2d3748;
        margin: 0;
    }
    
    .card-description {
        color: #718096;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
    }
    
    /* File uploader styling */
    .uploadedFile {
        background: #f8f9fa;
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .uploadedFile:hover {
        border-color: #764ba2;
        background: #f0f8ff;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    .stError {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        border: none;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-top: 3px solid #667eea;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
        margin: 0;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Animated elements */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Dividers */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #667eea 50%, transparent 100%);
        border: none;
        margin: 2rem 0;
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
    }
    
    /* Loading spinner */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
""", unsafe_allow_html=True)

# -------------------- Core Utilities --------------------
def clean_column(text):
    return text.strip() if isinstance(text, str) else text

def update_progress(progress_bar, value, total, message="Processing..."):
    progress_percent = value / total
    progress_bar.progress(progress_percent, text=f"{message} {value}/{total}")

def show_loading():
    """Display loading animation"""
    return st.markdown("""
        <div class="loading-spinner">
            <div class="spinner"></div>
        </div>
    """, unsafe_allow_html=True)

# -------------------- Match Functions --------------------
def find_gene_matches(patient_row, trials_df, exclusion_filters=None):
    """
    Find gene matches with configurable exclusion filters
    
    Args:
        patient_row: Patient data row
        trials_df: Clinical trials dataframe
        exclusion_filters: List of exclusion patterns to apply
    """
    gene = str(patient_row['Gene']).upper()
    gene_regex = rf'\b{gene}\b'
    
    # Default exclusion patterns
    default_exclusions = {
        'Cancer/Oncology': r'cancer|carcinoma|tumor|leukemia|lymphoma|metastases|glioma|glioblastoma|neoplasm|meningioma|melanoma|astrocytoma|sarcoma|AML|mesothelioma|myeloproliferative',
        'Trauma/Injury': r'trauma|injury|wound|burn|fracture|accident',
        'Infectious Disease': r'bacter|viral|infection|sepsis|pneumonia|influenza|covid',
        'Cardiovascular': r'cardiac|heart|coronary|myocardial|cardiovascular|stroke',
        'Neurological': r'alzheimer|parkinson|dementia|epilepsy|seizure|migraine',
        'Psychiatric': r'depression|anxiety|bipolar|schizophrenia|psychiatric',
        'Metabolic': r'diabetes|obesity|metabolic syndrome|hypertension',
        'Autoimmune': r'arthritis|lupus|autoimmune|inflammatory bowel'
    }
    
    # Build exclusion pattern based on selected filters
    if exclusion_filters and len(exclusion_filters) > 0:
        patterns = []
        for filter_name in exclusion_filters:
            if filter_name in default_exclusions:
                patterns.append(default_exclusions[filter_name])
        
        if patterns:
            exclusion_pattern = re.compile('|'.join(patterns), re.IGNORECASE)
            exclusion_mask = ~trials_df['ConditionGenePhenotype'].str.contains(exclusion_pattern, na=False)
        else:
            exclusion_mask = pd.Series([True] * len(trials_df))
    else:
        exclusion_mask = pd.Series([True] * len(trials_df))

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

def rare_disease_match(patients_df, gene_disease_path="gene_disease.txt", orphan_drugs_path="orphan_drugs.txt"):
    """
    Match patients with orphan drugs using local files
    
    Args:
        patients_df: DataFrame with patient data
        gene_disease_path: Path to local gene_disease.txt file
        orphan_drugs_path: Path to local orphan_drugs.txt file
    """
    patients_df['Phenotype'] = patients_df['Phenotype'].apply(clean_column)
    
    try:
        # Load both files from local directory
        orphan_df = pd.read_csv(orphan_drugs_path, sep='\t', dtype=str, encoding='latin1')
        gene_disease_df = pd.read_csv(gene_disease_path, sep='\t', dtype=str, encoding='latin1')

        # Match patients with gene-disease associations
        matched_genes = pd.merge(patients_df, gene_disease_df, left_on='Gene', right_on='Symbol')

        all_matches = []
        for _, row in matched_genes.iterrows():
            disease_name = re.escape(row['Name'])
            pattern = rf'\b{disease_name}\b'
            # Search in OrphanDesignation column of orphan drugs
            orphan_matches = orphan_df[orphan_df['OrphanDesignation'].str.contains(pattern, flags=re.IGNORECASE, na=False)]
            if not orphan_matches.empty:
                repeated_row = pd.DataFrame([row] * len(orphan_matches)).reset_index(drop=True)
                merged = pd.concat([repeated_row, orphan_matches.reset_index(drop=True)], axis=1)
                all_matches.append(merged)
        
        return pd.concat(all_matches, ignore_index=True).drop_duplicates() if all_matches else pd.DataFrame()
        
    except FileNotFoundError as e:
        if "gene_disease.txt" in str(e):
            st.error("❌ gene_disease.txt file not found. Please ensure the file exists in the app directory.")
        elif "orphan_drugs.txt" in str(e):
            st.error("❌ orphan_drugs.txt file not found. Please ensure the file exists in the app directory.")
        else:
            st.error(f"❌ Required file not found: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error processing drug matching data: {str(e)}")
        return pd.DataFrame()

# -------------------- Enhanced UI Components --------------------
def create_feature_card(icon, title, description, content_func):
    """Create a styled feature card with content"""
    with st.container():
        st.markdown(f"""
        <div class="feature-card animate-fade-in">
            <div class="card-header">
                <div class="card-icon">{icon}</div>
                <h3 class="card-title">{title}</h3>
            </div>
            <p class="card-description">{description}</p>
        </div>
        """, unsafe_allow_html=True)
        content_func()

def create_stats_display(stats_data):
    """Create statistics display cards"""
    cols = st.columns(len(stats_data))
    for i, (label, value) in enumerate(stats_data.items()):
        with cols[i]:
            st.markdown(f"""
            <div class="stat-card">
                <p class="stat-number">{value}</p>
                <p class="stat-label">{label}</p>
            </div>
            """, unsafe_allow_html=True)

# -------------------- Enhanced UI Logic --------------------
def run_trial_matcher():
    """Enhanced trial matcher with better UX and configurable filters"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📁 Patient Data**")
        patient_file = st.file_uploader(
            "Upload Patient VCF File", 
            type=['tsv', 'txt', 'vcf'], 
            key='match_patient',
            help="Upload a tab-separated file with PatientID, Gene, and Phenotype columns"
        )
        
        if patient_file:
            st.success("✅ Patient file uploaded successfully!")
            # Show preview
            try:
                preview_df = pd.read_csv(patient_file, sep='\t', header=None, nrows=3, encoding='latin1')
                preview_df.columns = ['PatientID', 'Gene', 'Phenotype']
                st.markdown("**Preview:**")
                st.dataframe(preview_df, use_container_width=True)
            except:
                st.warning("⚠️ Could not preview file")
    
    with col2:
        st.markdown("**🧪 Clinical Trials Data**")
        trial_file = st.file_uploader(
            "Upload Clinical Trial Database", 
            type=['tsv', 'txt', 'vcf'], 
            key='match_trial',
            help="Upload a tab-separated file with clinical trial information"
        )
        
        if trial_file:
            st.success("✅ Trial file uploaded successfully!")

    # Exclusion Filters Section
    st.markdown("---")
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
    
    # Create filter selection
    col1, col2 = st.columns(2)
    selected_filters = []
    
    with col1:
        for i, (key, description) in enumerate(list(exclusion_options.items())[:4]):
            if st.checkbox(f"{description}", key=f"filter_{key}"):
                selected_filters.append(key)
    
    with col2:
        for i, (key, description) in enumerate(list(exclusion_options.items())[4:]):
            if st.checkbox(f"{description}", key=f"filter_{key}"):
                selected_filters.append(key)
    
    # Show selected filters summary
    if selected_filters:
        st.info(f"🎯 **Active Filters:** {', '.join(selected_filters)}")
    else:
        st.warning("⚠️ **No filters selected** - All trial types will be included in matching")

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    
    # Enhanced button with loading state
    if st.button("🔍 **Start Matching Process**", use_container_width=True):
        if not patient_file or not trial_file:
            st.error("❌ Please upload both files before proceeding.")
            return

        # Loading state
        with st.spinner("🔄 Processing files and finding matches..."):
            try:
                patient_df = pd.read_csv(patient_file, sep='\t', header=None, dtype=str, encoding='latin1')
                trial_df = pd.read_csv(trial_file, sep='\t', header=None, dtype=str, encoding='latin1')
                patient_df.columns = ['PatientID', 'Gene', 'Phenotype']
                trial_df.columns = ['ClinicalTrialID', 'StudyTitle', 'StudyURL', 'StudyStatus', 'BriefSummary', 'ConditionGenePhenotype']

                progress_total = len(patient_df)
                progress_bar = st.progress(0, text="Initializing matching algorithm...")

                results = []
                for i, row in patient_df.iterrows():
                    update_progress(progress_bar, i + 1, progress_total, "Matching genes")
                    # Pass selected filters to the matching function
                    match_df = find_gene_matches(row, trial_df, selected_filters)
                    if match_df is not None:
                        results.append(match_df)
                    time.sleep(0.01)  # Small delay for visual effect

                if results:
                    matched_df = pd.concat(results, ignore_index=True).drop_duplicates()
                    
                    # Success metrics
                    create_stats_display({
                        "Total Matches": len(matched_df),
                        "Unique Patients": matched_df['PatientID'].nunique(),
                        "Unique Trials": matched_df['ClinicalTrialID'].nunique(),
                        "Success Rate": f"{(len(matched_df)/len(patient_df)*100):.1f}%"
                    })
                    
                    st.success(f"🎉 Successfully found {len(matched_df)} matches!")
                    
                    # Show applied filters in results
                    if selected_filters:
                        st.info(f"🎛️ **Filters Applied:** {', '.join(selected_filters)}")
                    
                    # Enhanced data display
                    st.markdown("### 📊 Matching Results")
                    st.dataframe(matched_df, use_container_width=True, height=400)
                    
                    # Download button
                    csv_data = matched_df.to_csv(index=False)
                    st.download_button(
                        "💾 **Download Complete Results**",
                        csv_data,
                        file_name=f"clinical_trial_matches_{date.today()}.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("🔍 No drug matches found for the provided patients.")
                    st.info("💡 **Suggestions:**\n- Check gene names in your patient file\n- Verify gene symbols match the database\n- Consider that not all rare diseases have orphan drug designations")
                    
            except Exception as e:
                st.error(f"❌ Error processing rare disease matches: {str(e)}")

# -------------------- Main App --------------------
def main():
    # Hero section
    st.markdown("""
    <div class="animate-fade-in">
        <h1 class="main-header">🧬 TRADER</h1>
        <p class="subtitle">
            <strong>Trials and Drugs Explorer for Rare Diseases</strong><br>
            Advanced matching platform connecting patients with clinical trials and FDA-designated orphan drugs
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # Feature cards
    create_feature_card(
        "🧬", 
        "Gene-Based Trial Matcher",
        "Match patients with relevant clinical trials based on genetic markers and phenotypes. Advanced filtering excludes cancer-related studies for rare disease focus.",
        run_trial_matcher
    )

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    create_feature_card(
        "📊", 
        "Dataset Comparison Tool",
        "Compare patient datasets to identify new matches and track changes over time. Perfect for monitoring database updates and patient cohort evolution.",
        run_file_comparison
    )

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    create_feature_card(
        "💊", 
        "Rare Disease Drug Matcher",
        "Connect patients with FDA-designated orphan drugs based on gene-disease associations. Leverages comprehensive drug databases for therapeutic options.",
        run_rare_disease_match
    )

    # Footer
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        <p>🔬 <strong>TRADER</strong> - Empowering rare disease research through intelligent data matching</p>
        <p><small>Built with Streamlit • Designed for researchers and clinicians</small></p>
    </div>
    """, unsafe_allow_html=True)


def run_file_comparison():
    """Enhanced file comparison with better UX"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Original Dataset**")
        original_file = st.file_uploader(
            "Upload Original Matched File", 
            type=["csv", 'txt'], 
            key="original_matched",
            help="Upload the baseline dataset for comparison"
        )
    
    with col2:
        st.markdown("**🆕 Updated Dataset**")
        updated_file = st.file_uploader(
            "Upload Updated Matched File", 
            type=["csv", 'txt'], 
            key="updated_matched",
            help="Upload the new dataset to compare against the original"
        )

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    if st.button("🔄 **Compare Datasets**", use_container_width=True):
        if not original_file or not updated_file:
            st.error("❌ Both files must be uploaded for comparison.")
            return

        with st.spinner("🔄 Analyzing differences between datasets..."):
            try:
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
                    update_progress(progress_bar, i + 1, progress_total, "Analyzing")

                # Results display
                create_stats_display({
                    "Original Records": len(original_df),
                    "Updated Records": len(updated_df),
                    "New Patients": len(new_matches),
                    "Growth Rate": f"{(len(new_matches)/len(original_df)*100):.1f}%"
                })

                if len(new_matches) > 0:
                    st.success(f"🆕 Found {len(new_matches)} new patient matches!")
                    st.markdown("### 📈 New Matches Found")
                    st.dataframe(new_matches, use_container_width=True)
                    
                    csv_data = new_matches.to_csv(index=False)
                    st.download_button(
                        "💾 **Download New Matches**",
                        csv_data,
                        file_name=f"comparison_results_{date.today()}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("ℹ️ No new matches found between the datasets.")

            except Exception as e:
                st.error(f"❌ Error comparing files: {str(e)}")

def run_rare_disease_match():
    """Simplified rare disease matcher with automatic database loading"""
    
    # Patient file upload
    st.markdown("**📁 Patient Data Upload**")
    patient_file = st.file_uploader(
        "Upload Patient VCF File", 
        type=['tsv', 'txt', 'vcf'], 
        key='patient_vcf_rare_final',
        help="Patient genetic data file with PatientID, Gene, and Phenotype columns"
    )
    
    # Show patient file status
    if patient_file:
        st.success("✅ Patient data uploaded successfully!")
        try:
            preview_df = pd.read_csv(patient_file, sep='\t', header=None, nrows=3, encoding='latin1')
            preview_df.columns = ['PatientID', 'Gene', 'Phenotype']
            st.markdown("**Preview:**")
            st.dataframe(preview_df, use_container_width=True)
        except:
            st.warning("⚠️ Could not preview patient file")
    
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    
    # Single button to run the entire process
    if st.button("🔬 **Run Rare Disease Drug Matcher**", use_container_width=True):
        if not patient_file:
            st.error("❌ Please upload patient data first.")
            return
        
        with st.spinner("🔄 Loading databases and analyzing rare disease drug matches..."):
            try:
                # Load patient data
                patients_df = pd.read_csv(patient_file, sep='\t', header=None, dtype=str, encoding='latin1')
                patients_df.columns = ['PatientID', 'Gene', 'Phenotype']
                
                # Check and load local database files
                gene_disease_path = "gene_disease.txt"
                orphan_drugs_path = "orphan_drugs.txt"
                
                # Validate database files exist
                try:
                    gene_disease_df = pd.read_csv(gene_disease_path, sep='\t', dtype=str, encoding='latin1')
                    st.info(f"📊 Loaded gene-disease database: {len(gene_disease_df)} entries")
                except FileNotFoundError:
                    st.error("❌ gene_disease.txt not found. Please ensure the file exists in the app directory.")
                    return
                
                try:
                    orphan_df = pd.read_csv(orphan_drugs_path, sep='\t', dtype=str, encoding='latin1')
                    st.info(f"💊 Loaded orphan drugs database: {len(orphan_df)} entries")
                except FileNotFoundError:
                    st.error("❌ orphan_drugs.txt not found. Please ensure the file exists in the app directory.")
                    return
                
                # Run matching process
                progress_total = len(patients_df)
                progress_bar = st.progress(0, text="Processing rare disease matches...")
                
                matches = rare_disease_match(patients_df, gene_disease_path, orphan_drugs_path)
                
                for i in range(progress_total):
                    update_progress(progress_bar, i + 1, progress_total, "Matching drugs")
                    time.sleep(0.01)
                
                # Display results
                if len(matches) > 0:
                    # Success metrics
                    unique_drugs = matches['GenericName'].nunique() if 'GenericName' in matches.columns else 0
                    unique_companies = matches['SponsorCompany'].nunique() if 'SponsorCompany' in matches.columns else 0
                    unique_diseases = matches['Name'].nunique() if 'Name' in matches.columns else 0
                    
                    create_stats_display({
                        "Total Matches": len(matches),
                        "Matched Patients": matches['PatientID'].nunique(),
                        "Unique Drugs": unique_drugs,
                        "Disease Types": unique_diseases
                    })
                    
                    st.success(f"🎯 Found {len(matches)} potential drug matches!")
                    
                    # Additional insights
                    if 'OrphanDesignationStatus' in matches.columns:
                        designated_matches = len(matches[matches['OrphanDesignationStatus'] == 'Designated'])
                        st.info(f"📊 **{designated_matches}** matches have designated orphan status")
                    
                    if 'SponsorCompany' in matches.columns and unique_companies > 0:
                        st.info(f"🏢 **{unique_companies}** different pharmaceutical companies involved")
                    
                    # Show results
                    st.markdown("### 💊 Drug Matching Results")
                    st.dataframe(matches, use_container_width=True, height=400)
                    
                    # Download option
                    csv_data = matches.to_csv(index=False)
                    st.download_button(
                        "💾 **Download Drug Matches**",
                        csv_data,
                        file_name=f"rare_disease_matches_{date.today()}.csv",
                        mime="text/csv",
                        use_container_width=True)
                else:
                    st.warning("🔍 No matches found. Try adjusting your search criteria or exclusion filters.")
            
            except Exception as e:
                st.error(f"❌ Error processing files: {str(e)}")

#def main():
#    # Hero section
#    st.markdown("""
#    <div class="animate-fade-in">
#        <h1 class="main-header">🧬 TRADER</h1>
#        <p class="subtitle">
#            <strong>Trials and Drugs Explorer for Rare Diseases</strong><br>
#            Advanced matching platform connecting patients with clinical trials and FDA-designated orphan drugs
#        </p>
#    </div>
#    """, unsafe_allow_html=True)


#    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # Feature cards
#    create_feature_card(
#        "🧬", 
#        "Gene-Based Trial Matcher",
#        "Match patients with relevant clinical trials based on genetic markers and phenotypes. Advanced filtering excludes cancer-related studies for rare disease focus.",
#        run_trial_matcher
#    )

#    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

#    create_feature_card(
#        "📊", 
#        "Dataset Comparison Tool",
#        "Compare patient datasets to identify new matches and track changes over time. Perfect for monitoring database updates and patient cohort evolution.",
#        run_file_comparison
#    )

#    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

#    create_feature_card(
#        "💊", 
#        "Rare Disease Drug Matcher",
#        "Connect patients with FDA-designated orphan drugs based on gene-disease associations. Leverages comprehensive drug databases for therapeutic options.",
#        run_rare_disease_match
#    )

    # Footer
#    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
#    st.markdown("""
#    <div style="text-align: center; color: #6c757d; padding: 2rem;">
#        <p>🔬 <strong>TRADER</strong> - Empowering rare disease research through intelligent data matching</p>
#        <p><small>Built with Streamlit • Designed for researchers and clinicians</small></p>
#    </div>
#    """, unsafe_allow_html=True)

#if __name__ == "__main__":
#    main()
def main():
    # Dynamic blue header with animations
    st.markdown("""
    <style>
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .dynamic-header {
        background: linear-gradient(-45deg, #1e3a8a, #3b82f6, #1d4ed8, #2563eb);
        background-size: 400% 400%;
        animation: gradient-shift 4s ease infinite;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .main-header-dynamic {
        color: white;
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        animation: pulse 3s ease-in-out infinite;
        letter-spacing: 2px;
    }
    
    .subtitle-dynamic {
        color: rgba(255, 255, 255, 0.95);
        font-size: 1.2rem;
        margin-top: 1rem;
        line-height: 1.6;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    .header-accent {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 25px;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    </style>
    
    <div class="animate-fade-in">
        <div class="dynamic-header">
            <h1 class="main-header-dynamic">🧬 TRADER</h1>
            <p class="subtitle-dynamic">
                <strong>Trials and Drugs Explorer for Rare Diseases</strong><br>
                <span class="header-accent">Advanced matching platform connecting patients with clinical trials and FDA-designated orphan drugs</span>
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    create_feature_card(
        "🧬", 
        "Gene-Based Trial Matcher",
        "Match patients with relevant clinical trials based on genetic markers and phenotypes. Advanced filtering excludes cancer-related studies for rare disease focus.",
        run_trial_matcher
    )
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    create_feature_card(
        "📊", 
        "Dataset Comparison Tool",
        "Compare patient datasets to identify new matches and track changes over time. Perfect for monitoring database updates and patient cohort evolution.",
        run_file_comparison
    )

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    create_feature_card(
        "💊", 
        "Rare Disease Drug Matcher",
        "Connect patients with FDA-designated orphan drugs based on gene-disease associations. Leverages comprehensive drug databases for therapeutic options.",
        run_rare_disease_match
    )
    # Footer
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        <p>🔬 <strong>TRADER</strong> - Empowering rare disease research through intelligent data matching</p>
        <p><small>Built with Streamlit • Designed for researchers and clinicians</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
