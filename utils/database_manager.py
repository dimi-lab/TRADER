import pandas as pd
import streamlit as st
from pathlib import Path
import logging

class DatabaseManager:
    """Centralized database management for TRADER application"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.databases = {}
        self.status = {}
        
    def load_all_databases(self):
        """Load all required databases with comprehensive error handling"""
        file_configs = {
            'clinical_trials': {
                'file': 'matched_clinical_trials_20240716_cleaned.test.csv',
                'type': 'csv',
                'description': 'Clinical Trials Database'
            },
            'gene_disease': {
                'file': 'gene_disease.test.txt',
                'type': 'tsv',
                'description': 'Gene-Disease Associations'
            },
            'orphan_drugs': {
                'file': 'orphan_drugs.test.txt',
                'type': 'tsv',
                'description': 'FDA Orphan Drug Designations'
            },
            'rare_disease_matches': {
                'file': 'rare_disease_matches_20240716_cleaned.test.csv',
                'type': 'csv',
                'description': 'Rare Disease Matches'
            }
        }
        
        for db_name, config in file_configs.items():
            self._load_single_database(db_name, config)
            
        return self.databases, self.status
    
    def _load_single_database(self, db_name, config):
        """Load a single database file with proper error handling"""
        file_path = self.base_path / config['file']
        
        try:
            if not file_path.exists():
                self.status[db_name] = f"❌ File not found: {config['file']}"
                self.databases[db_name] = None
                return
                
            # Load based on file type
            if config['type'] == 'csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            elif config['type'] == 'tsv':
                df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
            else:
                raise ValueError(f"Unsupported file type: {config['type']}")
            
            # Validate DataFrame
            if df.empty:
                self.status[db_name] = f"⚠️ Empty file: {config['file']}"
            else:
                self.status[db_name] = f"✅ {config['description']}: {len(df)} records"
                
            self.databases[db_name] = df
            
        except pd.errors.EmptyDataError:
            self.status[db_name] = f"❌ Empty or invalid CSV: {config['file']}"
            self.databases[db_name] = None
        except UnicodeDecodeError:
            # Try different encodings
            try:
                if config['type'] == 'csv':
                    df = pd.read_csv(file_path, encoding='latin-1')
                else:
                    df = pd.read_csv(file_path, sep='\t', encoding='latin-1')
                self.databases[db_name] = df
                self.status[db_name] = f"✅ {config['description']}: {len(df)} records (latin-1 encoding)"
            except Exception as e:
                self.status[db_name] = f"❌ Encoding error: {str(e)}"
                self.databases[db_name] = None
        except Exception as e:
            self.status[db_name] = f"❌ Load error: {str(e)}"
            self.databases[db_name] = None
    
    def get_database(self, db_name):
        """Get a specific database with fallback"""
        return self.databases.get(db_name)
    
    def get_status(self, db_name):
        """Get status for a specific database"""
        return self.status.get(db_name, "Unknown status")
    
    def validate_gene_disease_format(self):
        """Validate gene-disease data format"""
        df = self.get_database('gene_disease')
        if df is not None:
            expected_columns = ['Name', 'Symbol']
            if not all(col in df.columns for col in expected_columns):
                return False, f"Missing columns. Expected: {expected_columns}, Found: {list(df.columns)}"
            return True, "Valid format"
        return False, "Database not loaded"
    
    def validate_orphan_drugs_format(self):
        """Validate orphan drugs data format"""
        df = self.get_database('orphan_drugs')
        if df is not None:
            expected_columns = ['GenericName', 'TradeName', 'DateDesignated', 'OrphanDesignation']
            if not all(col in df.columns for col in expected_columns):
                return False, f"Missing columns. Expected: {expected_columns}, Found: {list(df.columns)}"
            return True, "Valid format"
        return False, "Database not loaded"

# Global database manager instance
@st.cache_resource
def get_database_manager():
    """Get cached database manager instance"""
    return DatabaseManager()

def display_enhanced_database_status():
    """Enhanced database status display"""
    db_manager = get_database_manager()
    databases, status = db_manager.load_all_databases()
    
    st.markdown("### 🗄️ Backend Database Status")
    
    # Create expandable sections for each database
    for db_name, db_status in status.items():
        with st.expander(f"{db_name.replace('_', ' ').title()}: {db_status}"):
            df = databases.get(db_name)
            if df is not None:
                st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
                st.write(f"**Columns:** {', '.join(df.columns)}")
                if len(df) > 0:
                    st.write("**Sample data:**")
                    st.dataframe(df.head(3), use_container_width=True)
            else:
                st.error("Database not loaded successfully")
    
    return databases, status
