import subprocess
import sys


def run(script):
    subprocess.run(
        [sys.executable, script],
        check=True,
    )


if __name__ == "__main__":
    run("data/create_database.py")
    run("data/seed_database.py")
    print("Project database is ready.")