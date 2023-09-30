import subprocess
import os
import sys

argc = len(sys.argv)
if(argc != 2):
    print("Usage: run_webserver.py [environment]")
    exit(1)

project_dir = os.path.join(os.path.dirname(__file__), "..")
js_dir = os.path.join(project_dir, "./Central-Server/hilsim-web")

def run():
    if(sys.argv[1] == "prod"):
        subprocess.run(f"cd {js_dir} & npm run build & node server.js", shell=True)
    elif(sys.argv[1] == "dev"):
        subprocess.run(f"cd {js_dir} & npm start", shell=True)
    

if __name__ == "__main__":
    run()