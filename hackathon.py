import os
import google.genai as genai
import boto3

def run_cloud_waste_audit():
    try:
        ec2 = boto3.client('ec2', region_name='us-east-1')
        
        # 1. Check for unattached EBS volumes
        volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])['Volumes']
        volume_data = []
        if not volumes:
            print("No unattached EBS volumes found.")
        else:
            for vol in volumes:
                vol_info = f"Volume ID: {vol['VolumeId']} | Size: {vol['Size']} GB"
                print(f" - {vol_info}")
                volume_data.append(vol_info)

        # 2. Check for stopped EC2 instances
        instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['stopped']}])
        stopped_instances = []
        has_stopped = False
        for reservation in instances.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                has_stopped = True
                inst_info = f"Instance ID: {instance['InstanceId']} | Type: {instance['InstanceType']}"
                print(f" - {inst_info}")
                stopped_instances.append(inst_info)
                
        if not has_stopped:
            print("No stopped EC2 instances found.")

        print("\n" + "="*40)
        print("AUDIT COMPLETE")
        
        # 3. Ask Gemini for advice on both
        print("Asking Gemini for cost-optimization advice...")
        client = genai.Client(api_key="AQ.Ab8RN6J3jkqDZHU52xAyoh74j4EYVBclCxzJw0PVfoz3X0k_Kw")

        prompt = f"Analyze these unattached AWS EBS volumes: {volume_data} and these stopped EC2 instances: {stopped_instances}, and give me optimization recommendations."
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        print("\n--- GEMINI RECOMMENDATIONS ---")
        print(response.text)
        
    except Exception as e:
        print(f"AWS or Gemini Error: {e}")

if __name__ == "__main__":
    run_cloud_waste_audit()