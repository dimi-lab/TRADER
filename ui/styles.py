import streamlit as st

def apply_page_config():
    """Apply Streamlit page configuration"""
    st.set_page_config(
        page_title="TRADER - Rare Disease Explorer",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_enhanced_styles():
    """Apply comprehensive enhanced CSS styles"""
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
            color: #0066cc;
            font-size: 1.2rem;
            font-weight: 400;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        
        /* Card styling */
        .feature-card {
            background: blue;
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
        
        /* Dynamic header animations */
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
    """, unsafe_allow_html=True)
    
