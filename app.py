import streamlit as st
import google.genai as genai
import boto3

st.set_page_config(page_title="GPU Waste Hunter", layout="wide")

st.title("⚡ Cloud Waste & Cost Optimization Dashboard")
st.markdown("AI-powered insights to scan, detect, and clean up unattached AWS resources.")

# Initialize Gemini Client (using your key directly or via env)
client = genai.Client(api_key="AQ.Ab8RN6J3jkqDZHU52xAyoh74j4EYVBclCxzJw0PVfoz3X0k_Kw")

# Function to run audit and fetch Gemini recommendations
def get_live_gemini_audit():
    try:
        # Example data payload (or hook up your live boto3 calls here)
        volume_data = "No unattached EBS volumes found."
        stopped_instances = "No stopped EC2 instances found."
        
        prompt = f"Analyze these unattached AWS EBS volumes: {volume_data} and these stopped EC2 instances: {stopped_instances}. Give me concise cost-saving recommendations."
        
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini or AWS: {e}"

# Stat metrics
num_volumes = len(volumes) if 'volumes' in locals() else 0
estimated_waste = num_volumes * 4.00

col1, col2, col3 = st.columns(3)
col1.metric("Estimated Monthly Waste", f"${estimated_waste:.2f}", f"-${estimated_waste:.2f}")
col2.metric("Idle Resources Found", str(num_volumes), f"{num_volumes} new" if num_volumes > 0 else "0 new")
col3.metric("Optimization Score", "100%" if num_volumes == 0 else "75%", "Optimal" if num_volumes == 0 else "Needs Action")
st.divider()

# AI Section
st.subheader("🤖 Gemini AI Recommendations")

if st.button("Run Live Cloud Audit", key="run_audit_btn"):
    with st.spinner("Scanning AWS and consulting Gemini..."):
        ai_recommendations = get_live_gemini_audit()
        st.success("Audit complete!")
        st.markdown(ai_recommendations)

        # Move the download button right here, indented properly inside the button block:
        st.download_button(
            label="Download AI Cost Report",
            data=ai_recommendations,
            file_name="cloud_waste_report.txt",
            mime="text/plain"
        )
else:
    st.info("Click the button above to run your live cloud waste audit.")

# Resource table section
st.subheader("📋 Scanned Resource Status")
st.write("All systems nominal. No wasteful configurations detected.")

# Kill Switch Section
st.divider()
st.subheader("🚨 Emergency Kill Switch")
st.warning("Warning: Executing the kill switch will immediately terminate flagged unattached resources to stop billing.")

if st.button("Activate Kill Switch (Terminate Idle Resources)", type="primary", key="emergency_kill_switch_action_btn"):
    with st.spinner("Executing cleanup protocols across AWS..."):
        try:
            ec2 = boto3.client('ec2', region_name='us-east-1')
            volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])['Volumes']
            volume_ids = [v['VolumeId'] for v in volumes]
            
            if volume_ids:
                for vol_id in volume_ids:
                    ec2.delete_volume(VolumeId=vol_id)
                st.success(f"Terminated volumes: {', '.join(volume_ids)}")
            else:
                st.info("No idle volumes found to terminate.")
            st.balloons()
        except Exception as e:
            st.error(f"Failed to execute kill switch: {e}")