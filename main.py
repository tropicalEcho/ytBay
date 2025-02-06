import yt_dlp, os, sys, shlex, shutil

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

currentDirectory = os.path.expanduser('~\\Downloads')
os.chdir(currentDirectory)

def changePath(newCurrentDirectory):
    global currentDirectory
    try:
        os.chdir(newCurrentDirectory)
        currentDirectory = os.getcwd()
    except FileNotFoundError:
        print(f"ERROR: DIRECTORY '{newCurrentDirectory}' NOT FOUND.")
    except Exception as e:
        print(f"ERROR: {str(e).upper()}")

ffmpegPath = shutil.which('ffmpeg') or r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"

manual = """
CLEAR | CLS                - CLEARS SCREEN
HELP                       - PRINTS THIS
<URL>                      - DOWNLOAD THE GIVEN URL
    <--VIDEO | --AUDIO | -V | -A> - SPECIFIES THE FORMAT
EXIT | QUIT                - KILLS THE PROGRAM
CHDIR | CD <NEW DIRECTORY> - CHANGE DOWNLOAD PATH
"""

def progressBar(d):
    if d['status'] == 'downloading':
        try:
            total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            percent = (downloaded / total * 100) if total else 0
            width = 30
            filled = int(width * percent / 100)
            bar = '#' * filled + '-' * (width - filled)
            percent_str = f"{percent:5.1f}"
            sys.stdout.write(f'\rDOWNLOADING: [{bar}] {percent_str}%')
            sys.stdout.flush()
        except Exception:
            sys.stdout.write('\rDOWNLOADING...')
            sys.stdout.flush()
    elif d['status'] == 'finished':
        sys.stdout.write('\nDOWNLOAD COMPLETE!\n')
        sys.stdout.flush()

def get_ydl_opts():
    video_opts, audio_opts = {}, {}

    common_opts = {
        'outtmpl': os.path.join(currentDirectory, '%(title)s.%(ext)s'),
        'ffmpeg_location': ffmpegPath,
        'quiet': True,
        'progress_hooks': [progressBar],
    }

    video_opts.update(common_opts)
    video_opts.update({
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Use the original misspelling as required.
        }],
    })

    audio_opts.update(common_opts)
    audio_opts.update({
        'format': 'bestaudio[ext=mp3]/bestaudio[ext=m4a]/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    })

    return video_opts, audio_opts

def download(url, format_flag="-V"):
    ydl_opts_video, ydl_opts_audio = get_ydl_opts()
    try:
        if format_flag in ["-V", "--VIDEO", "-VIDEO"]:
            with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                ydl.download([url])
        elif format_flag in ["-A", "--AUDIO"]:
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.download([url])
        else:
            print("ERROR: INVALID FORMAT!")
    except Exception as e:
        print(f"ERROR: {str(e).upper()}")

if not ffmpegPath:
    ffmpegPath = input("FFMPEG EXECUTABLE LOCATION (USE \\): ")

while True:
    user_input = input(f"{currentDirectory}$ ").strip()
    if not user_input:
        continue
    cmd = shlex.split(user_input)
    if not cmd:
        continue
    command = cmd[0].upper()
    if command in {"CLEAR", "CLS"}:
        clear()
    elif command in {"EXIT", "QUIT"}:
        sys.exit("GOODBYE!")
    elif command in {"CHDIR", "CD"}:
        try:
            newPath = cmd[1]
            changePath(newPath)
        except IndexError:
            print("ERROR: GOT NO NEWPATH")
    elif command in {"HELP"}:
        print(manual)
    else:
        try:
            url = cmd[0]
            format_flag = cmd[1].upper() if len(cmd) == 2 else None

            if not any(url.lower().startswith(valid) for valid in ["http", "www", "youtube", "music"]):
                print("ERROR: INVALID URL")
                continue

            download(url, format_flag="-V")
        except IndexError:
            print("ERROR: INCORRECT COMMAND FORMAT")