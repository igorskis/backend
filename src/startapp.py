import os, subprocess


def main():
    try:
        print("Choose Name")
        name = input()
        os.chdir("src/backend/apps")
        subprocess.run(f"uv run ../../manage.py startapp {name}")
        os.chdir("..")
        print("Created!")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()