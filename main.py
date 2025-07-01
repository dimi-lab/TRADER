import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path

# IMPORTANT: Page config must be the VERY FIRST Streamlit command
st.set_page_config(
    page_title="TRADER - Rare Disease Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add current directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Try imports with error handling
try:
    from ui.styles import apply_enhanced_styles
except ImportError as e:
    st.error(f"Could not import styles: {e}")
    apply_enhanced_styles = None

try:
    from ui.components import create_header, create_feature_card, create_custom_divider
except ImportError as e:
    st.error(f"Could not import components: {e}")
    create_header = None
    create_feature_card = None
    create_custom_divider = None

try:
    from utils.enhanced_data_utils import create_enhanced_patient_input
except ImportError as e:
    st.error(f"Could not import patient input: {e}")
    create_enhanced_patient_input = None

# Add try-catch for module imports to identify missing modules
try:
    from modules.enhanced_trial_matcher import run_trial_matcher_with_data
except ImportError as e:
    st.error(f"Could not import run_trial_matcher: {e}")
    run_trial_matcher_with_data = None

try:
    from modules.enhanced_file_comparison import run_file_comparison_with_data
except ImportError as e:
    st.error(f"Could not import run_file_comparison: {e}")
    run_file_comparison_with_data = None

try:
    from modules.enhanced_rare_disease_matcher import run_rare_disease_match_with_data
except ImportError as e:
    st.error(f"Could not import run_rare_disease_match: {e}")
    run_rare_disease_match_with_data = None

@st.cache_data
def load_backend_databases():
    """Load and validate all backend databases with proper error handling"""
    databases = {
        'clinical_trials': None,
        'gene_disease': None,
        'orphan_drugs': None,
        'rare_disease_matches': None,
        'status': {},
        'file_dates': {}
    }
    
    # Define file paths
    base_path = Path(__file__).parent
    files_to_load = {
        'clinical_trials': base_path / 'matched_clinical_trials_20240716_cleaned.csv',
        'gene_disease': base_path / 'gene_disease.test.txt',
        'orphan_drugs': base_path / 'orphan_drugs.test.txt',
        'rare_disease_matches': base_path / 'rare_disease_matches_20240716_cleaned.csv'
    }
    
    # Load each database with multi-encoding support
    for db_name, file_path in files_to_load.items():
        try:
            if file_path.exists():
                # Get file modification date
                import datetime
                mod_time = file_path.stat().st_mtime
                file_date = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M')
                databases['file_dates'][db_name] = file_date
                
                # Try multiple encodings
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                df = None
                
                for encoding in encodings:
                    try:
                        if file_path.suffix == '.csv':
                            df = pd.read_csv(file_path, encoding=encoding)
                        elif file_path.suffix == '.txt':
                            df = pd.read_csv(file_path, sep='\t', encoding=encoding)
                        
                        # If we get here, the encoding worked
                        databases[db_name] = df
                        databases['status'][db_name] = f"✅ Loaded {len(df)} records ({encoding})"
                        break
                        
                    except UnicodeDecodeError:
                        continue
                
                # If no encoding worked
                if df is None:
                    databases['status'][db_name] = f"❌ Could not decode file with any encoding"
                    databases[db_name] = None
            else:
                databases['status'][db_name] = f"❌ File not found: {file_path}"
                databases[db_name] = None
                databases['file_dates'][db_name] = "N/A"
                
        except Exception as e:
            databases['status'][db_name] = f"❌ Unexpected error: {str(e)}"
            databases[db_name] = None
            databases['file_dates'][db_name] = "Error"
    
    return databases

def display_database_status(databases):
    """Display database loading status in the UI with file dates"""
    st.subheader("🗄️ Backend Database Status")
    
    # Create expandable sections for each database with detailed info
    database_info = {
        'clinical_trials': {
            'name': 'Clinical Trials Database',
            'description': 'Active clinical trials for rare diseases',
            'icon': '🧪'
        },
        'gene_disease': {
            'name': 'Gene-Disease Associations',
            'description': 'Gene to disease mapping database',
            'icon': '🧬'
        },
        'orphan_drugs': {
            'name': 'FDA Orphan Drug Designations',
            'description': 'FDA-designated orphan drugs for rare diseases',
            'icon': '💊'
        },
        'rare_disease_matches': {
            'name': 'REACTOR Database',
            'description': 'Historical rare disease patient matches',
            'icon': '📊'
        }
    }
    
    # Create two columns for database status
    col1, col2 = st.columns(2)
    
    databases_list = list(database_info.items())
    
    # First column - first 2 databases
    with col1:
        for db_name, info in databases_list[:2]:
            with st.expander(f"{info['icon']} {info['name']}", expanded=False):
                # Status
                status = databases['status'].get(db_name, 'Not loaded')
                if "✅" in status:
                    st.success(status)
                else:
                    st.error(status)
                
                # File date
                file_date = databases['file_dates'].get(db_name, 'Unknown')
                st.info(f"📅 **File Date:** {file_date}")
                
                # Description
                st.write(f"📝 **Description:** {info['description']}")
                
                # Show sample data if available
                if databases[db_name] is not None:
                    df = databases[db_name]
                    st.write(f"📏 **Dimensions:** {df.shape[0]:,} rows × {df.shape[1]} columns")
                    st.write(f"🏷️ **Columns:** {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
    
    # Second column - remaining databases
    with col2:
        for db_name, info in databases_list[2:]:
            with st.expander(f"{info['icon']} {info['name']}", expanded=False):
                # Status
                status = databases['status'].get(db_name, 'Not loaded')
                if "✅" in status:
                    st.success(status)
                else:
                    st.error(status)
                
                # File date
                file_date = databases['file_dates'].get(db_name, 'Unknown')
                st.info(f"📅 **File Date:** {file_date}")
                
                # Description
                st.write(f"📝 **Description:** {info['description']}")
                
                # Show sample data if available
                if databases[db_name] is not None:
                    df = databases[db_name]
                    st.write(f"📏 **Dimensions:** {df.shape[0]:,} rows × {df.shape[1]} columns")
                    st.write(f"🏷️ **Columns:** {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
    
    # Overall summary
    total_records = 0
    loaded_databases = 0
    
    for db_name in database_info.keys():
        if databases[db_name] is not None:
            total_records += len(databases[db_name])
            loaded_databases += 1
    
    if loaded_databases > 0:
        st.success(f"📈 **Summary:** {loaded_databases}/{len(database_info)} databases loaded successfully • {total_records:,} total records available")
    else:
        st.error("❌ No databases loaded successfully")

def safe_run_trial_matcher(patient_data):
    """Safely run trial matcher with patient data"""
    try:
        if run_trial_matcher_with_data is None:
            st.error("Trial matcher module not available")
            return
        run_trial_matcher_with_data(patient_data)
    except Exception as e:
        st.error(f"Error running trial matcher: {str(e)}")
        st.exception(e)

def safe_run_file_comparison(patient_data):
    """Safely run file comparison with patient data"""
    try:
        if run_file_comparison_with_data is None:
            st.error("File comparison module not available")
            return
        run_file_comparison_with_data(patient_data)
    except Exception as e:
        st.error(f"Error running file comparison: {str(e)}")
        st.exception(e)

def safe_run_rare_disease_match(patient_data):
    """Safely run rare disease matcher with patient data"""
    try:
        if run_rare_disease_match_with_data is None:
            st.error("Rare disease matcher module not available")
            return
        run_rare_disease_match_with_data(patient_data)
    except Exception as e:
        st.error(f"Error running rare disease matcher: {str(e)}")
        st.exception(e)

def main():
    """Enhanced main application entry point with unified patient input"""
    try:
        # Apply enhanced styles if available
        if apply_enhanced_styles is not None:
            apply_enhanced_styles()
        
        # Load databases
        databases = load_backend_databases()
        
        # Store in session state for access by modules
        st.session_state['databases'] = databases
        
        # Dynamic animated header
        if create_header is not None:
            create_header()
        else:
            st.title("🧬 TRADER")
            st.subheader("Trials and Drugs Explorer for Rare Diseases")
        
        # Database status section
        display_database_status(databases)
        
        if create_custom_divider is not None:
            create_custom_divider()
        else:
            st.markdown("---")
        
        # UNIFIED PATIENT INPUT SECTION
        st.markdown("## 📁 Patient Data Input")
        st.markdown("*Enter your patient genetic data once to use across all three analysis tools*")
        
        # Get patient data using the enhanced input system
        patient_data = pd.DataFrame()
        if create_enhanced_patient_input is not None:
            patient_data = create_enhanced_patient_input("main_app")
        else:
            st.error("❌ Patient input system not available")
        
        # Store patient data in session state
        if not patient_data.empty:
            st.session_state['patient_data'] = patient_data
            st.success(f"✅ Patient data loaded! Ready to use across all {3} analysis tools.")
        
        # Main content sections - only show if we have patient data
        if create_custom_divider is not None:
            create_custom_divider()
        else:
            st.markdown("---")
        
        st.markdown("## 🔬 Analysis Tools")
        st.markdown("*Use the patient data above with any of the following analysis tools*")
        
        # Create three columns for the tools
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if create_feature_card is not None:
                create_feature_card(
                    "🧬", 
                    "Gene-Based Trial Matcher",
                    "Match patients with relevant clinical trials based on genetic markers and phenotypes.",
                    lambda: safe_run_trial_matcher(patient_data) if not patient_data.empty else st.warning("⚠️ Please provide patient data above first")
                )
            else:
                st.subheader("🧬 Gene-Based Trial Matcher")
                st.write("Match patients with relevant clinical trials.")
                if st.button("Run Trial Matcher", key="trial_btn"):
                    safe_run_trial_matcher(patient_data) if not patient_data.empty else st.warning("⚠️ Please provide patient data above first")
        
        with col2:
            if create_feature_card is not None:
                create_feature_card(
                    "📊", 
                    "Dataset Comparison Tool", 
                    "Compare current patient data against historical REACTOR database.",
                    lambda: safe_run_file_comparison(patient_data) if not patient_data.empty else st.warning("⚠️ Please provide patient data above first")
                )
            else:
                st.subheader("📊 Dataset Comparison Tool")
                st.write("Compare patient data against REACTOR database.")
                if st.button("Run File Comparison", key="file_btn"):
                    safe_run_file_comparison(patient_data) if not patient_data.empty else st.warning("⚠️ Please provide patient data above first")

        with col3:
            if create_feature_card is not None:
                create_feature_card(
                    "💊", 
                    "Rare Disease Drug Matcher",
                    "Connect patients with FDA-designated orphan drugs.",
                    lambda: safe_run_rare_disease_match(patient_data) if not patient_data.empty else st.warning("⚠️ Please provide patient data above first")
                )
            else:
                st.subheader("💊 Rare Disease Drug Matcher")
                st.write("Connect patients with FDA-designated orphan drugs.")
                if st.button("Run Rare Disease Matcher", key="drug_btn"):
                    safe_run_rare_disease_match(patient_data) if not patient_data.empty else st.warning("⚠️ Please provide patient data above first")
        
        # Footer
        if create_custom_divider is not None:
            create_custom_divider()
        else:
            st.markdown("---")
            
        st.markdown("""
        <div style="text-align: center; color: #6c757d; padding: 2rem;">
            <p>🔬 <strong>TRADER</strong> - Empowering rare disease research through intelligent data matching</p>
            <p><small>Built with Streamlit • Designed for researchers and clinicians</small></p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main()
