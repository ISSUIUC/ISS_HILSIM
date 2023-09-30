import subprocess
import os
import sys

argc = len(sys.argv)
if(argc != 2):
    print("Usage: run_api.py [environment]")
    exit(1)

project_dir = os.path.join(os.path.dirname(__file__), "..")
cwd = os.path.join(project_dir, "./Central-Server/API")

def run():
    if(sys.argv[1] == "prod"):
        subprocess.run(f"cd {cwd} & python main.py prod", shell=True)
    elif(sys.argv[1] == "dev"):
        subprocess.run(f"cd {cwd} & python main.py dev", shell=True)

if __name__ == "__main__":
    run()