import streamlit as st
import time

def create_header():
    """Create dynamic animated header"""
    st.markdown("""
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

def create_custom_divider():
    """Create custom styled divider"""
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

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

def update_progress(progress_bar, value, total, message="Processing..."):
    """Update progress bar with current value and message"""
    progress_percent = value / total
    progress_bar.progress(progress_percent, text=f"{message} {value}/{total}")

def show_loading():
    """Display loading animation"""
    return st.markdown("""
        <div class="loading-spinner">
            <div class="spinner"></div>
        </div>
    """, unsafe_allow_html=True)

def display_file_uploader_with_preview(label, file_types, key, help_text, columns=['PatientID', 'Gene', 'Phenotype']):
    """Create file uploader with preview functionality"""
    uploaded_file = st.file_uploader(label, type=file_types, key=key, help=help_text)
    
    if uploaded_file:
        st.success("✅ File uploaded successfully!")
        try:
            import pandas as pd
            preview_df = pd.read_csv(uploaded_file, sep='\t', header=None, nrows=3, encoding='latin1')
            preview_df.columns = columns[:len(preview_df.columns)]
            st.markdown("**Preview:**")
            st.dataframe(preview_df, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Could not preview file: {str(e)}")
    
    return uploaded_file

def create_exclusion_filters():
    """Create exclusion filter selection interface"""
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
    
    # Create filter selection in two columns
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
    
    return selected_filters

def display_results_with_download(results_df, success_message, filename, additional_info=None):
    """Display results with statistics and download functionality"""
    if len(results_df) > 0:
        # Success metrics based on dataframe columns
        stats = {
            "Total Matches": len(results_df),
            "Unique Patients": results_df['PatientID'].nunique() if 'PatientID' in results_df.columns else 0,
        }
        
        # Add conditional stats based on available columns
        if 'ClinicalTrialID' in results_df.columns:
            stats["Unique Trials"] = results_df['ClinicalTrialID'].nunique()
        if 'GenericName' in results_df.columns:
            stats["Unique Drugs"] = results_df['GenericName'].nunique()
        if 'SponsorCompany' in results_df.columns:
            stats["Companies"] = results_df['SponsorCompany'].nunique()
        
        create_stats_display(stats)
        st.success(success_message)
        
        # Display additional information if provided
        if additional_info:
            for info in additional_info:
                st.info(info)
        
        # Show results table
        st.markdown("### 📊 Results")
        st.dataframe(results_df, use_container_width=True, height=400)
        
        # Download button
        csv_data = results_df.to_csv(index=False)
        st.download_button(
            "💾 **Download Results**",
            csv_data,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.warning("🔍 No matches found.")
        st.info("💡 **Suggestions:**\n- Check your input data format\n- Verify gene names or patient IDs\n- Try adjusting exclusion filters")

def create_loading_context(message="Processing..."):
    """Create loading context manager"""
    return st.spinner(f"🔄 {message}")

def simulate_progress_with_delay(progress_bar, total_steps, base_message, delay=0.01):
    """Simulate progress with visual delay for better UX"""
    for i in range(total_steps):
        update_progress(progress_bar, i + 1, total_steps, base_message)
        time.sleep(delay)
