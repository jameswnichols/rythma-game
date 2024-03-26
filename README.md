# Rythma
A basic rhythm game written in `pygame-ce`. Can load Clone Hero tracks, as long as they aren't midi. Also features a note scoring system, though never fully implemented so only printed in console.

### Features
- State-of-the-art one-point perspective. Would change it but haven't touched project for months.
- When holding keys, the associated barriers will wave. Can be seen in the first image in Gameplay below.

### Requirements

Python 3.10+ is needed. The only module required is `pygame-ce`. Obtain it by executing `python3 -m pip install pygame-ce` in the terminal.

### Usage
- Obtain a non-midi Clone Hero chart `___.chart` and its associated music file `.ogg`, `.mp3`, etc. Make sure they're in the same directory.
- In `config.py` change the `CHART_PATH` constant to the full path to the chart file. Also change `DIFFICULTY_PREF` to whatever difficulty the chart supports.
- Run `python3 -m rythma.py`.
- Controls for the five lanes are "A","S","D",":" and "'" accordingly.
- Controls can be changed by modifiying the `KEYS` constant dictionary keys in `rythma.py`.

### Gameplay Screenshots
<img width="799" alt="Screenshot 2024-03-26 at 17 19 15" src="https://github.com/jameswnichols/rythma-game/assets/30716007/eb2c928b-d9c8-46de-af3d-06f9ad7c8750">
<img width="798" alt="Screenshot 2024-03-26 at 17 05 58" src="https://github.com/jameswnichols/rythma-game/assets/30716007/fc8637b6-a937-46be-8e7b-a737ac317175">
<img width="799" alt="Screenshot 2024-03-26 at 17 06 24" src="https://github.com/jameswnichols/rythma-game/assets/30716007/b5408bb0-ddc8-4352-8e0b-8e864efd4648">


