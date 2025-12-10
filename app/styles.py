"""
Premium UI/UX Styling for AWS Certifications Coach
World-class design with AWS colors, glassmorphism, and modern animations
"""

def get_custom_css():
    """Return comprehensive custom CSS for the application"""
    return """
    <style>
    /* ============================================
       FONTS & TYPOGRAPHY
       ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700;
    }
    
    /* ============================================
       COLOR VARIABLES
       ============================================ */
    :root {
        /* AWS Brand Colors */
        --aws-orange: #FF9900;
        --aws-orange-dark: #EC7211;
        --aws-orange-light: #FFB84D;
        --aws-blue: #232F3E;
        --aws-blue-light: #37475A;
        --aws-squid-ink: #161E2D;
        
        /* Gradients */
        --gradient-primary: linear-gradient(135deg, #FF9900 0%, #EC7211 100%);
        --gradient-hero: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #FF9900 100%);
        --gradient-success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        --gradient-danger: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        --gradient-info: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --gradient-dark: linear-gradient(135deg, #232F3E 0%, #37475A 100%);
        
        /* Semantic Colors */
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --info: #3b82f6;
        
        /* Neutrals */
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-300: #d1d5db;
        --gray-400: #9ca3af;
        --gray-500: #6b7280;
        --gray-600: #4b5563;
        --gray-700: #374151;
        --gray-800: #1f2937;
        --gray-900: #111827;
        
        /* Shadows */
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
        --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
        --shadow-glow: 0 0 30px rgba(255, 153, 0, 0.3);
        
        /* Border Radius */
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --radius-2xl: 1.5rem;
        --radius-full: 9999px;
        
        /* Transitions */
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-base: 300ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* ============================================
       GLOBAL STYLES
       ============================================ */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #FF9900 100%);
        background-attachment: fixed;
    }
    
    .main {
        background: transparent;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* ============================================
       GLASSMORPHIC CONTAINERS
       ============================================ */
    .glass-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: var(--radius-2xl);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: var(--shadow-2xl);
        padding: 2rem;
        margin: 1rem 0;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(15px);
        border-radius: var(--radius-xl);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: var(--shadow-lg);
        padding: 1.5rem;
        margin: 0.75rem 0;
        transition: all var(--transition-base);
        animation: fadeInUp 0.4s ease-out;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-2xl);
        border: 1px solid rgba(255, 153, 0, 0.3);
    }
    
    /* ============================================
       HERO SECTION
       ============================================ */
    .hero-container {
        text-align: center;
        padding: 3rem 2rem;
        margin: 2rem 0;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: var(--radius-2xl);
        box-shadow: var(--shadow-2xl);
        animation: fadeInUp 0.6s ease-out;
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: slideInDown 0.8s ease-out;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        color: var(--gray-700);
        margin-bottom: 2rem;
        animation: slideInUp 0.8s ease-out;
    }
    
    .hero-cta {
        display: inline-block;
        padding: 1rem 2.5rem;
        background: var(--gradient-primary);
        color: white;
        font-weight: 700;
        border-radius: var(--radius-full);
        box-shadow: var(--shadow-lg);
        transition: all var(--transition-base);
        cursor: pointer;
        animation: pulse 2s infinite;
    }
    
    .hero-cta:hover {
        transform: scale(1.05);
        box-shadow: var(--shadow-glow);
    }
    
    /* ============================================
       BUTTONS
       ============================================ */
    .stButton>button {
        background: var(--gradient-primary) !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: var(--radius-lg) !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        transition: all var(--transition-base) !important;
        box-shadow: var(--shadow-md) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-xl) !important;
        background: linear-gradient(135deg, #EC7211 0%, #FF9900 100%) !important;
    }
    
    .stButton>button:active {
        transform: translateY(0) !important;
    }
    
    /* Primary button variant */
    .stButton>button[kind="primary"] {
        background: var(--gradient-primary) !important;
        box-shadow: var(--shadow-lg), 0 0 20px rgba(255, 153, 0, 0.3) !important;
    }
    
    /* Secondary button variant */
    .stButton>button[kind="secondary"] {
        background: var(--gradient-dark) !important;
    }
    
    /* ============================================
       METRIC CARDS
       ============================================ */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        border-radius: var(--radius-xl);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: var(--shadow-lg);
        transition: all var(--transition-base);
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-2xl);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: var(--gray-600) !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* ============================================
       PROGRESS BARS
       ============================================ */
    .stProgress > div > div > div {
        background: var(--gradient-primary) !important;
        border-radius: var(--radius-full);
        animation: progressAnimation 1s ease-out;
    }
    
    @keyframes progressAnimation {
        from { width: 0%; }
    }
    
    /* ============================================
       CHAT INTERFACE
       ============================================ */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: var(--radius-xl) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        box-shadow: var(--shadow-md) !important;
        margin: 0.75rem 0 !important;
        padding: 1rem !important;
        animation: slideInRight 0.3s ease-out;
    }
    
    [data-testid="stChatMessage"][data-testid-type="user"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%) !important;
        border-left: 4px solid var(--aws-orange) !important;
    }
    
    [data-testid="stChatMessage"][data-testid-type="assistant"] {
        background: linear-gradient(135deg, rgba(255, 153, 0, 0.05) 0%, rgba(236, 114, 17, 0.05) 100%) !important;
        border-left: 4px solid var(--info) !important;
    }
    
    .stChatInputContainer {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border-radius: var(--radius-xl);
        border: 2px solid rgba(255, 153, 0, 0.3);
        padding: 0.5rem;
        box-shadow: var(--shadow-lg);
    }
    
    /* ============================================
       SIDEBAR
       ============================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #232F3E 0%, #37475A 100%) !important;
        border-right: 1px solid rgba(255, 153, 0, 0.2);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Sidebar navigation active state */
    .css-1544g2n {
        background: var(--gradient-primary) !important;
        border-radius: var(--radius-lg) !important;
    }
    
    /* ============================================
       INPUT FIELDS
       ============================================ */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(255, 153, 0, 0.2) !important;
        border-radius: var(--radius-lg) !important;
        padding: 0.75rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all var(--transition-base) !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus,
    .stSelectbox>div>div>select:focus {
        border-color: var(--aws-orange) !important;
        box-shadow: 0 0 0 3px rgba(255, 153, 0, 0.1) !important;
        outline: none !important;
    }
    
    /* ============================================
       EXPANDERS
       ============================================ */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.9) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: var(--radius-lg) !important;
        border: 1px solid rgba(255, 153, 0, 0.2) !important;
        padding: 1rem !important;
        font-weight: 600 !important;
        transition: all var(--transition-base) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 153, 0, 0.1) !important;
        border-color: var(--aws-orange) !important;
    }
    
    /* ============================================
       ALERTS & NOTIFICATIONS
       ============================================ */
    .stAlert {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: var(--radius-lg) !important;
        border-left: 4px solid !important;
        padding: 1rem 1.5rem !important;
        box-shadow: var(--shadow-md) !important;
        animation: slideInRight 0.3s ease-out;
    }
    
    .stSuccess {
        border-left-color: var(--success) !important;
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.1) 0%, rgba(255, 255, 255, 0.95) 20%) !important;
    }
    
    .stError {
        border-left-color: var(--error) !important;
        background: linear-gradient(90deg, rgba(239, 68, 68, 0.1) 0%, rgba(255, 255, 255, 0.95) 20%) !important;
    }
    
    .stWarning {
        border-left-color: var(--warning) !important;
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.1) 0%, rgba(255, 255, 255, 0.95) 20%) !important;
    }
    
    .stInfo {
        border-left-color: var(--info) !important;
        background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, rgba(255, 255, 255, 0.95) 20%) !important;
    }
    
    /* ============================================
       TABS
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(15px);
        border-radius: var(--radius-xl);
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: var(--radius-lg);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all var(--transition-base);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 153, 0, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-primary) !important;
        color: white !important;
        box-shadow: var(--shadow-md);
    }
    
    /* ============================================
       RADIO BUTTONS & CHECKBOXES
       ============================================ */
    .stRadio > label > div[role="radiogroup"] > label {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(255, 153, 0, 0.2);
        border-radius: var(--radius-lg);
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all var(--transition-base);
        cursor: pointer;
    }
    
    .stRadio > label > div[role="radiogroup"] > label:hover {
        border-color: var(--aws-orange);
        background: rgba(255, 153, 0, 0.05);
        transform: translateX(5px);
    }
    
    .stCheckbox {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(15px);
        border-radius: var(--radius-lg);
        padding: 0.75rem;
        margin: 0.25rem 0;
        transition: all var(--transition-base);
    }
    
    .stCheckbox:hover {
        background: rgba(255, 153, 0, 0.05);
    }
    
    /* ============================================
       LOADING SPINNER
       ============================================ */
    .stSpinner > div {
        border-color: var(--aws-orange) !important;
        border-right-color: transparent !important;
    }
    
    /* ============================================
       CUSTOM ANIMATIONS
       ============================================ */
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
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(255, 153, 0, 0.7);
        }
        50% {
            transform: scale(1.02);
            box-shadow: 0 0 0 10px rgba(255, 153, 0, 0);
        }
    }
    
    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    @keyframes spin {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }
    
    /* ============================================
       SKELETON LOADERS
       ============================================ */
    .skeleton {
        background: linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.1) 0%,
            rgba(255, 255, 255, 0.3) 50%,
            rgba(255, 255, 255, 0.1) 100%
        );
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
        border-radius: var(--radius-lg);
    }
    
    /* ============================================
       TOOLTIPS
       ============================================ */
    [data-testid="stTooltipIcon"] {
        color: var(--aws-orange) !important;
    }
    
    /* ============================================
       SCROLLBAR
       ============================================ */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: var(--radius-full);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--gradient-primary);
        border-radius: var(--radius-full);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #EC7211 0%, #FF9900 100%);
    }
    
    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .glass-container,
        .glass-card {
            padding: 1rem;
        }
    }
    
    /* ============================================
       UTILITY CLASSES
       ============================================ */
    .text-gradient {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .glow {
        box-shadow: var(--shadow-glow);
    }
    
    .bounce {
        animation: bounce 2s infinite;
    }
    
    .fade-in {
        animation: fadeInUp 0.5s ease-out;
    }
    </style>
    """

def get_confetti_animation():
    """Return JavaScript for confetti animation"""
    return """
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <script>
        function triggerConfetti() {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 },
                colors: ['#FF9900', '#EC7211', '#667eea', '#764ba2']
            });
        }
    </script>
    """

def show_loading_animation():
    """Return HTML for custom loading animation"""
    return """
    <div style="display: flex; justify-content: center; align-items: center; padding: 2rem;">
        <div style="
            width: 60px;
            height: 60px;
            border: 4px solid rgba(255, 153, 0, 0.2);
            border-top: 4px solid #FF9900;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        "></div>
    </div>
    """

def create_metric_card(icon, title, value, delta=None):
    """Create an animated metric card"""
    delta_html = ""
    if delta:
        color = "#10b981" if delta > 0 else "#ef4444"
        arrow = "↑" if delta > 0 else "↓"
        delta_html = f'<div style="color: {color}; font-size: 0.9rem; font-weight: 600;">{arrow} {abs(delta)}%</div>'
    
    return f"""
    <div class="glass-card" style="text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #FF9900 0%, #EC7211 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value}</div>
        <div style="color: #6b7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.5rem;">{title}</div>
        {delta_html}
    </div>
    """

def create_progress_ring(percentage, label, size=120):
    """Create an animated circular progress indicator"""
    circumference = 2 * 3.14159 * 45
    offset = circumference - (percentage / 100) * circumference
    
    return f"""
    <div style="text-align: center; margin: 1rem;">
        <svg width="{size}" height="{size}" style="transform: rotate(-90deg);">
            <circle cx="{size/2}" cy="{size/2}" r="45" stroke="rgba(255, 153, 0, 0.2)" stroke-width="10" fill="none"/>
            <circle cx="{size/2}" cy="{size/2}" r="45" 
                stroke="url(#gradient)" 
                stroke-width="10" 
                fill="none"
                stroke-dasharray="{circumference}"
                stroke-dashoffset="{offset}"
                stroke-linecap="round"
                style="transition: stroke-dashoffset 1s ease-out;"/>
            <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#FF9900;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#EC7211;stop-opacity:1" />
                </linearGradient>
            </defs>
        </svg>
        <div style="margin-top: -80px; font-size: 1.5rem; font-weight: 800; color: #FF9900;">{percentage}%</div>
        <div style="margin-top: 45px; font-weight: 600; color: #6b7280;">{label}</div>
    </div>
    """

def create_badge(text, type="default"):
    """Create a badge with different styles"""
    colors = {
        "default": "linear-gradient(135deg, #6b7280 0%, #4b5563 100%)",
        "success": "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
        "warning": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
        "error": "linear-gradient(135deg, #ee0979 0%, #ff6a00 100%)",
        "primary": "linear-gradient(135deg, #FF9900 0%, #EC7211 100%)",
    }
    
    return f"""
    <span style="
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: {colors.get(type, colors['default'])};
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    ">{text}</span>
    """

