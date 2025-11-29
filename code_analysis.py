import subprocess
import sys

def run_command(command):
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command)
    if result.returncode != 0:
        print(f"Command {' '.join(command)} failed!")
        return False
    return True

def main():
    check_passed = 0

    check_passed += 1 if run_command(["black", "src", "tests"]) else 0
    check_passed += 1 if run_command(["isort", "src", "tests"]) else 0
    check_passed += 1 if run_command(["flake8", "src", "tests"]) else 0

    print(f"{check_passed}/3 checks passed.")
