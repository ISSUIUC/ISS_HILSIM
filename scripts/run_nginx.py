import subprocess
import os
import sys

argc = len(sys.argv)
if(argc != 2):
    print("Usage: run_nginx.py [environment]")
    exit(1)

project_dir = os.path.join(os.path.dirname(__file__), "..")
cwd = os.path.join(project_dir, "./nginx")

def run():
    if(sys.argv[1] == "prod"):
        print("Initialized nginx reverse proxy on localhost:80")
        print("Point localhost:80/* to localhost:8080")
        print("Point localhost:80/api/* to localhost:443")
        subprocess.run(f"cd {cwd} & nginx.exe", shell=True)
    if(sys.argv[1] == "dev"):
        print("Initialized nginx reverse proxy on localhost:80")
        print("Point localhost:80/* to localhost:3000")
        print("Point localhost:80/api/* to localhost:443")
        subprocess.run(f"cd {cwd} & nginx.exe -c ./conf/dev.conf", shell=True)
    

if __name__ == "__main__":
    run()