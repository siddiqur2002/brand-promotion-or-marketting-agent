import os
import requests
import streamlit as st
from streamlit_option_menu import option_menu

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="GenAI Campaign Hub",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend URL Configuration (Supports Docker internal network & Environment Vars)
BACKEND_URL = os.getenv("BACKEND_URL", "https://brand-promotion-or-marketting-agent.onrender.com/api/v1/campaigns")

# --- 2. Streamlit Modern Custom Styling ---
st.markdown("""
    <style>
    /* Global Layout Adjustments */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* Modern Status Badges */
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.88rem;
        text-align: center;
    }
    .status-completed { background-color: #10B981; color: #ffffff; }
    .status-processing { background-color: #F59E0B; color: #ffffff; }
    .status-failed { background-color: #EF4444; color: #ffffff; }
    .status-pending { background-color: #6B7280; color: #ffffff; }

    /* Card Box for Containers */
    .stCard {
        background: #1e222d;
        border: 1px solid #2e3440;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. Session State Initialization ---
if "current_task_id" not in st.session_state:
    st.session_state["current_task_id"] = None

# --- 4. API Service Handlers ---
def post_campaign_payload(payload: dict):
    try:
        response = requests.post(f"{BACKEND_URL}/", json=payload, timeout=10)
        return response.json(), response.status_code
    except Exception as e:
        return {"error": f"Failed to connect to backend service: {str(e)}"}, 500

def fetch_campaign_status(task_id: str):
    try:
        response = requests.get(f"{BACKEND_URL}/{task_id}", timeout=60)
        return response.json(), response.status_code
    except Exception as e:
        return {"error": f"Failed to reach backend API: {str(e)}"}, 500

# --- 5. Sidebar Navigation ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/rocket--v1.png", width=60)
    st.title("AI Campaign Studio")
    st.caption("Powered by CrewAI & FastAPI")
    st.markdown("---")
    
    selected_menu = option_menu(
        menu_title=None,
        options=["New Campaign", "Campaign Status", "Architecture"],
        icons=["plus-circle-fill", "activity", "cpu-fill"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#9ca3af", "font-size": "16px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "4px 0px",
                "border-radius": "8px",
            },
            "nav-link-selected": {"background-color": "#2563eb", "color": "#ffffff"},
        }
    )

# --- 6. PAGE 1: NEW CAMPAIGN CREATION ---
if selected_menu == "New Campaign":
    st.title("✨ Launch New AI Marketing Campaign")
    st.write("Fill in the details below to trigger Multi-Agent Research & Strategic Copywriting.")
    st.markdown("---")

    with st.form("campaign_creation_form", border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            brand_name = st.text_input("Brand Name *", placeholder="e.g., EcoDrinkware")
            target_audience = st.text_input("Target Audience *", placeholder="e.g., Health-conscious commuters & fitness lovers")
            
        with col2:
            campaign_goal = st.text_input("Campaign Goal *", placeholder="e.g., Drive online sales for smart insulated bottle")
            
        product_description = st.text_area(
            "Product Description *", 
            placeholder="e.g., Smart insulated water bottle that tracks daily hydration via app and keeps drinks cold for 24 hours.",
            height=130
        )

        submitted = st.form_submit_button("🚀 Execute Marketing Crew", type="primary", use_container_width=True)

    if submitted:
        if not all([brand_name.strip(), target_audience.strip(), campaign_goal.strip(), product_description.strip()]):
            st.warning("⚠️ Please fill in all mandatory fields before submitting.")
        else:
            payload = {
                "brand_name": brand_name,
                "product_description": product_description,
                "target_audience": target_audience,
                "campaign_goal": campaign_goal
            }
            
            with st.spinner("Dispatching task to Celery & Redis Queue..."):
                res, status_code = post_campaign_payload(payload)
                
            if status_code in [200, 201, 202]:
                task_id = res.get("task_id")
                st.session_state["current_task_id"] = task_id
                st.success("🎉 Campaign task queued successfully!")
                st.code(f"Task ID: {task_id}", language="text")
                st.info("💡 You can now head over to the **'Campaign Status'** tab to view execution logs and results.")
            else:
                st.error(f"❌ Creation Failed: {res.get('error', res.get('detail', 'Unknown error occurred'))}")

# --- 7. PAGE 2: CAMPAIGN MONITOR & POLLED RESULTS ---
elif selected_menu == "Campaign Status":
    st.title("📊 Live Campaign Execution Monitor")
    st.write("Track async worker progress and retrieve Agent-generated marketing assets.")
    st.markdown("---")

    query_task_id = st.text_input(
        "Enter Task ID:", 
        value=st.session_state.get("current_task_id") or "",
        placeholder="e.g., 4cf1ee6d-0f89-4a29-ae3b-b6e3dda3b7f8"
    )

    fetch_click = st.button("🔎 Fetch Campaign Data", type="primary")

    if query_task_id and (fetch_click or st.session_state.get("current_task_id")):
        st.session_state["current_task_id"] = query_task_id
        
        # Modern Streamlit Fragment for Local Area Polling
        @st.fragment(run_every=5 if st.session_state.get("auto_poll", False) else None)
        def render_campaign_dashboard(task_id: str):
            res, status_code = fetch_campaign_status(task_id)

            if status_code != 200:
                st.error(f"❌ Task Error: {res.get('detail', 'Task ID not found in database.')}")
                st.session_state["auto_poll"] = False
                return

            status = res.get("status", "UNKNOWN")
            brand = res.get("brand_name", "N/A")

            # Status Header Cards
            m1, m2, m3 = st.columns(3)
            m1.metric("Brand Name", brand)
            m2.metric("Task Reference", f"{task_id[:8]}...")
            
            with m3:
                st.write("**Current Status**")
                if status == "COMPLETED":
                    st.markdown("<span class='status-badge status-completed'>COMPLETED</span>", unsafe_allow_html=True)
                    st.session_state["auto_poll"] = False
                elif status == "PROCESSING":
                    st.markdown("<span class='status-badge status-processing'>PROCESSING</span>", unsafe_allow_html=True)
                    st.session_state["auto_poll"] = True
                elif status == "FAILED":
                    st.markdown("<span class='status-badge status-failed'>FAILED</span>", unsafe_allow_html=True)
                    st.session_state["auto_poll"] = False
                else:
                    st.markdown("<span class='status-badge status-pending'>PENDING</span>", unsafe_allow_html=True)
                    st.session_state["auto_poll"] = True

            st.markdown("---")

            # Output Render Strategy
            if status == "COMPLETED":
                research = res.get("research_result")
                ad_copies = res.get("ad_copies")

                tab_res, tab_ads = st.tabs(["📈 Market Analysis Output", "✍️ Ad Copy Variations"])

                with tab_res:
                    st.subheader("Market Research & Insights")
                    st.markdown(research if research else "*No research data returned.*")

                with tab_ads:
                    st.subheader("Generated Marketing Copies")
                    st.markdown(ad_copies if ad_copies else "*No ad copies returned.*")

            elif status in ["PENDING", "PROCESSING"]:
                st.info("⏳ AI Agents are executing research and copywriting tasks in background... Auto-refreshing status every 5 seconds.")
                st.progress(0.65 if status == "PROCESSING" else 0.15)

            elif status == "FAILED":
                st.error("🚨 Execution Failed During Task Processing!")
                st.code(res.get("error_message", "No specific error trace recorded in DB."))

        render_campaign_dashboard(query_task_id)

# --- 8. PAGE 3: SYSTEM ARCHITECTURE ---
elif selected_menu == "Architecture":
    st.title("🏛️ Production Stack Architecture")
    st.markdown("""
    This full-stack AI application utilizes an **Asynchronous Producer-Consumer Architecture**:

    - **Frontend**: Streamlit 1.4x (Interactive Dashboard with Fragment Polling)
    - **API Gateway**: FastAPI (Asynchronous Endpoints + CORS enabled)
    - **Task Queue & Broker**: Celery + Upstash Redis
    - **Orchestration & LLM**: CrewAI Multi-Agent Pipeline running Groq (Llama-3.3 70B)
    - **Database**: PostgreSQL (SQLAlchemy Async ORM)
    """)



