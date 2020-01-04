import os

if __name__ == '__main__':
    with open("commands.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            os.system(line)
    print("\033[1;32mCollegeManager.app is ready to use!\033[1;32m")
