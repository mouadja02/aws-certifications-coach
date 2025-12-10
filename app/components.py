"""
Premium UI Components for AWS Certifications Coach
Reusable components for toast notifications, modals, and animations
"""

import streamlit as st


def show_toast(message, type="success", duration=3):
    """
    Display a toast notification
    
    Args:
        message: The message to display
        type: success, error, warning, info
        duration: How long to show (seconds)
    """
    icons = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    colors = {
        "success": "#10b981",
        "error": "#ef4444",
        "warning": "#f59e0b",
        "info": "#3b82f6"
    }
    
    backgrounds = {
        "success": "rgba(16, 185, 129, 0.1)",
        "error": "rgba(239, 68, 68, 0.1)",
        "warning": "rgba(245, 158, 11, 0.1)",
        "info": "rgba(59, 130, 246, 0.1)"
    }
    
    icon = icons.get(type, "ℹ️")
    color = colors.get(type, "#3b82f6")
    bg = backgrounds.get(type, "rgba(59, 130, 246, 0.1)")
    
    st.markdown(f"""
    <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(15px);
        border-left: 4px solid {color};
        border-radius: 0.75rem;
        padding: 1rem 1.5rem;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        z-index: 9999;
        animation: slideInRight 0.3s ease-out, fadeOut 0.5s ease-out {duration - 0.5}s forwards;
        min-width: 300px;
        max-width: 400px;
    ">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 1.5rem;">{icon}</div>
            <div style="flex: 1; color: #4b5563; font-weight: 500;">{message}</div>
        </div>
    </div>
    
    <style>
    @keyframes slideInRight {{
        from {{
            transform: translateX(100%);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
    
    @keyframes fadeOut {{
        from {{
            opacity: 1;
        }}
        to {{
            opacity: 0;
            transform: translateX(100%);
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


def show_confetti():
    """Trigger confetti animation for celebrations"""
    st.markdown("""
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <script>
        var duration = 3 * 1000;
        var animationEnd = Date.now() + duration;
        var defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 0 };

        function randomInRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        var interval = setInterval(function() {
            var timeLeft = animationEnd - Date.now();

            if (timeLeft <= 0) {
                return clearInterval(interval);
            }

            var particleCount = 50 * (timeLeft / duration);
            
            confetti(Object.assign({}, defaults, {
                particleCount,
                origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
                colors: ['#FF9900', '#EC7211', '#667eea', '#764ba2', '#10b981']
            }));
            confetti(Object.assign({}, defaults, {
                particleCount,
                origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
                colors: ['#FF9900', '#EC7211', '#667eea', '#764ba2', '#10b981']
            }));
        }, 250);
    </script>
    """, unsafe_allow_html=True)


def show_loading_skeleton(type="card", count=1):
    """
    Display loading skeletons
    
    Args:
        type: card, list, text
        count: Number of skeletons to show
    """
    if type == "card":
        for _ in range(count):
            st.markdown("""
            <div class="glass-card" style="padding: 1.5rem;">
                <div class="skeleton" style="height: 30px; width: 60%; margin-bottom: 1rem;"></div>
                <div class="skeleton" style="height: 20px; width: 100%; margin-bottom: 0.5rem;"></div>
                <div class="skeleton" style="height: 20px; width: 90%; margin-bottom: 0.5rem;"></div>
                <div class="skeleton" style="height: 20px; width: 70%;"></div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
    
    elif type == "list":
        for _ in range(count):
            st.markdown("""
            <div class="glass-card" style="padding: 1rem; display: flex; align-items: center; gap: 1rem;">
                <div class="skeleton" style="width: 60px; height: 60px; border-radius: 50%;"></div>
                <div style="flex: 1;">
                    <div class="skeleton" style="height: 20px; width: 40%; margin-bottom: 0.5rem;"></div>
                    <div class="skeleton" style="height: 16px; width: 70%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
    
    elif type == "text":
        for _ in range(count):
            st.markdown("""
            <div style="margin-bottom: 0.5rem;">
                <div class="skeleton" style="height: 16px; width: 100%;"></div>
            </div>
            """, unsafe_allow_html=True)


def show_modal(title, content, show_close=True):
    """
    Display a modal dialog
    
    Args:
        title: Modal title
        content: Modal content (HTML)
        show_close: Show close button
    """
    st.markdown(f"""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(5px);
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s ease-out;
    ">
        <div style="
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-radius: 1.5rem;
            padding: 2rem;
            max-width: 600px;
            width: 90%;
            box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
            animation: scaleIn 0.3s ease-out;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h2 style="margin: 0; color: #232F3E;">{title}</h2>
                {f'<button style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #6b7280;">✕</button>' if show_close else ''}
            </div>
            <div>
                {content}
            </div>
        </div>
    </div>
    
    <style>
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    @keyframes scaleIn {{
        from {{ transform: scale(0.9); opacity: 0; }}
        to {{ transform: scale(1); opacity: 1; }}
    }}
    </style>
    """, unsafe_allow_html=True)


def create_feature_card(icon, title, description, button_text=None, button_action=None):
    """Create a premium feature card"""
    button_html = ""
    if button_text:
        button_html = f"""
        <button style="
            background: linear-gradient(135deg, #FF9900 0%, #EC7211 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
            {button_text}
        </button>
        """
    
    return f"""
    <div class="glass-card" style="text-align: center; padding: 2rem; min-height: 300px; display: flex; flex-direction: column;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
        <h3 style="color: #FF9900; margin-bottom: 1rem; flex-grow: 0;">{title}</h3>
        <p style="color: #6b7280; line-height: 1.6; flex-grow: 1; margin-bottom: 1.5rem;">{description}</p>
        {button_html}
    </div>
    """


def create_stat_badge(value, label, icon, color="#FF9900"):
    """Create a small stat badge"""
    return f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        border: 2px solid {color};
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    ">
        <span style="font-size: 1.2rem;">{icon}</span>
        <div>
            <div style="font-size: 1.2rem; font-weight: 800; color: {color};">{value}</div>
            <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase;">{label}</div>
        </div>
    </div>
    """


def create_timeline_item(icon, title, description, time, is_completed=True):
    """Create a timeline activity item"""
    status_color = "#10b981" if is_completed else "#9ca3af"
    
    return f"""
    <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
        <div style="
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, {status_color} 0%, {status_color} 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            flex-shrink: 0;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        ">
            {icon}
        </div>
        <div style="flex: 1; padding-top: 0.25rem;">
            <div style="font-weight: 700; color: #232F3E; margin-bottom: 0.25rem;">{title}</div>
            <div style="color: #6b7280; margin-bottom: 0.5rem; line-height: 1.5;">{description}</div>
            <div style="color: #9ca3af; font-size: 0.875rem;">{time}</div>
        </div>
    </div>
    """


def create_quiz_option(letter, text, is_selected=False, is_correct=None, show_result=False):
    """Create a premium quiz option button"""
    border_color = "#e5e7eb"
    bg_color = "rgba(255, 255, 255, 0.9)"
    
    if show_result:
        if is_correct:
            border_color = "#10b981"
            bg_color = "rgba(16, 185, 129, 0.1)"
        else:
            border_color = "#ef4444"
            bg_color = "rgba(239, 68, 68, 0.1)"
    elif is_selected:
        border_color = "#FF9900"
        bg_color = "rgba(255, 153, 0, 0.1)"
    
    result_icon = ""
    if show_result:
        if is_correct:
            result_icon = '<span style="color: #10b981; font-size: 1.5rem; margin-left: auto;">✓</span>'
        else:
            result_icon = '<span style="color: #ef4444; font-size: 1.5rem; margin-left: auto;">✗</span>'
    
    return f"""
    <div style="
        background: {bg_color};
        backdrop-filter: blur(15px);
        border: 2px solid {border_color};
        border-radius: 0.75rem;
        padding: 1rem 1.5rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 1rem;
    " onmouseover="this.style.transform='translateX(5px)'" onmouseout="this.style.transform='translateX(0)'">
        <div style="
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #FF9900 0%, #EC7211 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            color: white;
            flex-shrink: 0;
        ">
            {letter}
        </div>
        <div style="flex: 1; color: #4b5563; font-weight: 500;">{text}</div>
        {result_icon}
    </div>
    """

