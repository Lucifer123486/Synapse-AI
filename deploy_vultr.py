import paramiko
import time
import sys

hostname = '65.20.73.26'
password = '8hB]3AQnVjg5b2%!'
username = 'root'

def execute_command(ssh, command):
    print(f"Executing: {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    
    # Read output as it comes
    exit_status = stdout.channel.recv_exit_status()
    
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    
    if out:
        print("STDOUT: [omitted to avoid charmap errors]")
    if err:
        print("STDERR: [omitted to avoid charmap errors]")
        
    if exit_status != 0:
        print(f"Command failed with exit status {exit_status}")
    else:
        print("Command succeeded")
    print("-" * 40)
    return exit_status

def main():
    print("Connecting to Vultr server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname, username=username, password=password, timeout=30)
        print("Connected successfully!")
        
        # 1. Update and install dependencies
        execute_command(ssh, "export DEBIAN_FRONTEND=noninteractive && apt update && apt upgrade -y -q")
        execute_command(ssh, "export DEBIAN_FRONTEND=noninteractive && apt install docker.io docker-compose git -y -q")
        
        # 2. Clone repo
        # Remove if exists to avoid errors on rerun
        execute_command(ssh, "rm -rf Synapse-AI")
        execute_command(ssh, "git clone https://github.com/Lucifer123486/Synapse-AI.git")
        
        # 3. Create .env file
        env_content = """GEMINI_API_KEY=AIzaSyChT5Nn-prFnsE0NvOyoz5oqkKUiEoNPWw
FEATHERLESS_API_KEY=rc_ce6befbb6af0ccd3047ddc716f4ed1ddc4e8b9d7a86ce545e1deb3c722f5315d
SUPABASE_URL=https://mryfdjwmlrttlaoiztsg.supabase.co
SUPABASE_KEY=sb_publishable_uC7oR6SBHXbsWCo_mG0sFg_PAv1zPP-
SPEECHMATICS_API_KEY=H8KA7vDVYCVyZSu4MN6igcWKdd4wEV5h
CORS_ORIGINS=*
"""
        
        sftp = ssh.open_sftp()
        with sftp.file('/root/Synapse-AI/backend/.env', 'w') as f:
            f.write(env_content)
        sftp.close()
        print("Created .env file at /root/Synapse-AI/backend/.env")
        
        # 4. Start Docker Compose
        execute_command(ssh, "cd Synapse-AI && docker-compose up -d --build")
        
        print("Deployment sequence completed!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
