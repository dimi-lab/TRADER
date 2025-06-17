import streamlit as st
from ui.styles import apply_page_config, apply_enhanced_styles
from ui.components import create_header, create_feature_card, create_custom_divider
from modules.enhanced_trial_matcher import run_trial_matcher
from modules.enhanced_file_comparison import run_file_comparison
from modules.enhanced_rare_disease_matcher import run_rare_disease_match

def main():
    """Enhanced main application entry point with dynamic styling"""
    # Apply page configuration and enhanced styles
    apply_page_config()
    apply_enhanced_styles()
    
    # Dynamic animated header
    create_header()
    
    # Main content sections with enhanced styling
    create_custom_divider()
    
    create_feature_card(
        "🧬", 
        "Gene-Based Trial Matcher",
        "Match patients with relevant clinical trials based on genetic markers and phenotypes. Advanced filtering excludes cancer-related studies for rare disease focus.",
        run_trial_matcher
    )
    
    create_custom_divider()

    create_feature_card(
        "📊", 
        "Dataset Comparison Tool",
        "Compare patient datasets to identify new matches and track changes over time. Perfect for monitoring database updates and patient cohort evolution.",
        run_file_comparison
    )

    create_custom_divider()
    
    create_feature_card(
        "💊", 
        "Rare Disease Drug Matcher",
        "Connect patients with FDA-designated orphan drugs based on gene-disease associations. Leverages comprehensive drug databases for therapeutic options.",
        run_rare_disease_match
    )
    
    # Footer
    create_custom_divider()
    st.markdown("""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        <p>🔬 <strong>TRADER</strong> - Empowering rare disease research through intelligent data matching</p>
        <p><small>Built with Streamlit • Designed for researchers and clinicians</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    
