import streamlit as st
from agents import BlogGenerator
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set up page configuration
st.set_page_config(
    page_title="✍️ AI Collective Blog Generator",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0066cc;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #0066cc;
        color: white;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton > button:hover {
        background-color: #0052a3;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #f0f7ff;
        border-left: 5px solid #0066cc;
    }
    .assistant-message {
        background-color: #f9f9f9;
        border-left: 5px solid #1fd655;
    }
    .highlight {
        background-color: #ffffcc;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
    }
    .stSpinner > div {
        border-color: #0066cc !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "linkup_api_key" not in st.session_state:
    st.session_state.linkup_api_key = os.getenv("LINKUP_API_KEY", "")
if "blog_history" not in st.session_state:
    st.session_state.blog_history = []
if "generator" not in st.session_state:
    st.session_state.generator = None

def initialize_generator():
    """Initialize the blog generator with API key."""
    try:
        if st.session_state.linkup_api_key:
            os.environ["LINKUP_API_KEY"] = st.session_state.linkup_api_key
            st.session_state.generator = BlogGenerator()
            return True
        return False
    except Exception as e:
        logger.error(f"Error initializing generator: {str(e)}")
        st.error(f"Error initializing generator: {str(e)}")
        return False

def reset_history():
    """Reset the blog history."""
    st.session_state.blog_history = []

# Sidebar: Configuration
with st.sidebar:
    st.image("https://avatars.githubusercontent.com/u/175112039?s=200&v=4", width=80)
    st.markdown("<h2>AI Collective</h2>", unsafe_allow_html=True)
    st.markdown("<p>Substack Blog Generator</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # API Key input
    linkup_api_key = st.text_input(
        "LinkUp API Key", 
        value=st.session_state.linkup_api_key,
        type="password",
        help="Get your key at https://app.linkup.so/sign-up"
    )
    
    if linkup_api_key:
        st.session_state.linkup_api_key = linkup_api_key
        os.environ["LINKUP_API_KEY"] = linkup_api_key
        
    # Advanced settings (collapsible)
    with st.expander("✨ Style Settings"):
        st.write("Your blog uses Alex's personalized style:")
        st.info("""
        • Conversational & casual
        • Direct & personal ("you" and occasional "bro")
        • Short & punchy sentences
        • Encouraging & supportive language
        • Emotionally honest tone
        """)
    
    # Action buttons
    st.button("🧹 Clear History", on_click=reset_history)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Powered by</p>
            <div style='display: flex; justify-content: center; gap: 15px; align-items: center;'>
                <img src="https://cdn.prod.website-files.com/66cf2bfc3ed15b02da0ca770/66d07240057721394308addd_Logo%20(1).svg" width="80">
                <span>+</span>
                <img src="https://framerusercontent.com/images/wLLGrlJoyqYr9WvgZwzlw91A8U.png?scale-down-to=512" width="100">
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Main content area
st.markdown("<h1 class='main-header'>✍️ AI Collective Blog Generator</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Create engaging, conversational blogs ready for Substack</p>", unsafe_allow_html=True)

# Blog topic input
topic = st.text_input(
    "What would you like to blog about?",
    placeholder="e.g., AI trends for productivity in 2025",
    help="Be specific about your topic for better results"
)

# Blog generation
if st.button("✨ Generate Blog Post", disabled=not st.session_state.linkup_api_key):
    if not topic:
        st.warning("Please enter a blog topic")
    else:
        # Initialize generator if needed
        if not st.session_state.generator:
            success = initialize_generator()
            if not success:
                st.error("Failed to initialize the blog generator. Please check your API key.")
                st.stop()
        
        # Generate blog
        with st.spinner("🔍 Researching and writing your blog post... (this might take 1-2 minutes)"):
            try:
                # Add progress indicators for better UX
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Show research phase
                status_text.text("Researching your topic...")
                time.sleep(0.5)
                progress_bar.progress(25)
                
                # Show writing phase
                status_text.text("Crafting your blog in Alex's style...")
                time.sleep(0.5)
                progress_bar.progress(50)
                
                # Generate the actual blog
                blog_content = st.session_state.generator.create_blog_post(topic)
                
                # Show formatting phase
                status_text.text("Formatting for Substack...")
                time.sleep(0.5)
                progress_bar.progress(75)
                
                # Final step
                status_text.text("Finalizing your blog post...")
                time.sleep(0.5)
                progress_bar.progress(100)
                
                # Clear progress indicators
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # Add to history
                st.session_state.blog_history.append({
                    "topic": topic,
                    "content": blog_content,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                
            except Exception as e:
                logger.error(f"Error generating blog: {str(e)}")
                st.error(f"Error generating blog: {str(e)}")

# Display blog history (most recent first)
if st.session_state.blog_history:
    st.divider()
    st.subheader("📚 Your Blog Posts")
    
    for i, blog in enumerate(reversed(st.session_state.blog_history)):
        with st.expander(f"**{blog['topic']}** - {blog['timestamp']}"):
            st.markdown(blog["content"])
            
            # Add copy and download buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📋 Copy to Clipboard", key=f"copy_{i}"):
                    # This uses JavaScript to copy to clipboard
                    st.markdown(
                        f"""
                        <textarea id="clipboard_text" style="position: absolute; left: -9999px;">{blog['content']}</textarea>
                        <script>
                            navigator.clipboard.writeText(document.getElementById("clipboard_text").value);
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
                    st.success("Copied to clipboard!")
            with col2:
                # Create download link
                blog_filename = blog['topic'].lower().replace(" ", "_")[:30] + ".txt"
                st.download_button(
                    label="💾 Download as Text",
                    data=blog['content'],
                    file_name=blog_filename,
                    mime="text/plain",
                    key=f"download_{i}"
                )
else:
    if st.session_state.linkup_api_key:
        st.info("👋 Enter a topic above and click 'Generate Blog Post' to get started!")
    else:
        st.warning("⚠️ Please enter your LinkUp API Key in the sidebar to get started")

# Tips for better results
with st.expander("💡 Tips for great blog posts"):
    st.markdown("""
    * **Be specific** in your topic - "AI productivity tools for remote teams" is better than just "AI tools"
    * **Include your target audience** - "AI for small business owners" helps tailor the content
    * **Mention the angle** - "Pros and cons of..." or "Beginner's guide to..." helps set the focus
    * **Add timeframes** - "2025 trends in..." makes the content more relevant and specific
    * **Include questions** you want answered in the blog - "How can small businesses use AI without technical expertise?"
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Made with ❤️ by AI Collective</p>",
    unsafe_allow_html=True
)