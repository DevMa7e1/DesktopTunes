# DesktopTunes
Simple music player with fun visuals that react to your music

## Download links
* ### Windows
    x86_64 binary --> [Download here](download-link)

* ### Linux
    x86_64 binary --> [Download here](download-link)

## How to run the executable
### Linux
After unzipping, you will need to open a terminal, go to the location of the binary, and run the command `chmod +x DesktopTunes`. Afterwards, you can run the ELF binary through the terminal or by just double-clicking it.

Please note, it might take a little while for the main window to appear.

### Windows
After unzipping the archive which contains the Windows build, you're going to have to right click and open the properties of the executable file. In the properties window, click on the checkbox next to Unblock and hit Ok. Now, you can run the software by just double-clicking the exe.

Please note, it might take a little while for the main window to appear.

## How to use DesktopTunes?
* ### Playing an audio file
    After opening the program, press on the **Open** button. A file dialog will appear from which you can select the audio file(s) that you want to play. The program supports playing the following formats: 
    | Format | What works |
    | --------- | -------------- |
    | **FLAC** | playing and displaying cover image |
    | **WAV** | playing |
    | **OGG** | playing |
    | **MP3** | playing and displaying cover image |
* ### Using the media controls
    | Button | Top bar action | What it does |
    | -------- | ------------------- | ---------------- |
    | Open | File > Open audio file(s) | Opens the file dialog for selecting files to be played |
    | Play (Pause) | Media > Play/Pause | Plays (or pauses) playback
    | Stop | Media > Stop | Stops playback and returns to the start of the first file |
* ### Changing visual effect
    You can change the current visual effect (even while audio is playing) by clicking on the **Visuals** menu in the top bar and selecting a visual effect (e.g. **Amplitude responsive (full)**).
* ### Enabling gapless playback
    You can remove the automatically added fade-out at the end of songs and play audio from multiple files without interruptions by clicking on the **Fading** menu in the top bar and selecting **Enable gapless playback**.
    
    Please note, the change only applies to files that you open after adjusting the setting. The files opened before changing the setting will still fade-out automatically.

    Not all songs are meant to be played in gapless mode. If you hear clicking at the transition from a song to another, you might want to consider disabling gapless playback.

### Linux
1. Install all necessary tools
    
    Debian and Debian-based distros:
    * `sudo apt install git python3-full`

    Arch Linux and Arch-based distros:
    * `sudo pacman -S git python`
2. `git clone https://github.com/DevMa7e1/DesktopTunes.git`
3. `cd DesktopTunes`
4. `python3 -m venv venv`
5. `source venv/bin/activate` (modify for your shell)
6. `pip install -r requirements.txt`
7. `pip install pyinstaller`
8. `python3 -m PyInstaller -F -n DesktopTunes main.py --add-data icon.png:. --noconsole --hidden-import='_cffi_backend'`

The resulting executable can be found in the **dist** folder.

## Windows
1. Install the latest version of Python
2. [Download the source code of DesktopTunes](https://github.com/DevMa7e1/DesktopTunes/archive/refs/heads/main.zip)
3. Unzip it and go into the created folder
4. Open a new CMD window
5. Copy the path of the previously opened folder and run the command `cd *your path here*`
6. Run the command `python -m venv venv`
7. Run the command `venv\Scripts\activate`
8. Run the command `pip install -r requirements.txt`
9. Run the command `pip install pyinstaller`
10. Run the command `python -m PyInstaller -F -n DesktopTunes --noconsole main.py --add-data icon.png:. --icon icon_big.png --hidden-import="_cffi_backend"`

The resulting executable can be found in the **dist** folder.