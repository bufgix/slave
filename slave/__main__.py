from subprocess import Popen, PIPE
import pathlib
import sys


def create_executable(filename: str = 'bot.py'):
    bot_source = pathlib.Path().cwd() / 'bot.py'
    print(f"[i] Source: {bot_source}")
    print("[i] Creating executable file...")
    proc = Popen(['pyinstaller',
                  '-F', '-w', '--clean',
                  '--onefile',  str(bot_source)], stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    if 'completed successfully' in str(err):
        print(
            f"[*] Created executable file. Check {pathlib.Path().cwd() / 'dist/'}")
    else:
        print(str(err))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[!] Missing bot file path")
    else:   
        create_executable(sys.argv[1])
