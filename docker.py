import os
import sys

command = sys.argv[1] if len(sys.argv) > 1 else ""

if command == "up":
    os.system("docker compose up -d --build")
elif command == "down":
    os.system("docker compose down")
elif command == "destroy":
    os.system("docker compose down -v")
elif command == "logs":
    os.system("docker compose logs -f backend")
elif command == "ps":
    os.system("docker ps")
else:
    print("""
Comandos disponíveis para linux:

python3 docker.py up
python3 docker.py down
python3 docker.py destroy
python3 docker.py logs
python3 docker.py ps
""")
