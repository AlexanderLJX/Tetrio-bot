# Tetrio-bot

color matching and brute forcing best combinations and rotations for any tetris game tetr.io/jstris (change color in python file)

## Demo

https://user-images.githubusercontent.com/83382087/240593118-c6c66916-ae01-4e73-a2ca-e79132c9c7b1.mp4

## Installation

Clone repo

```
git clone https://github.com/AlexanderLJX/Tetrio-bot.git
cd Tetrio-bot
```

Download and install Anaconda from [anaconda.com/download](https://www.anaconda.com/download/) and add it to your environment path.

```
conda create -n tetrio python=3.10
conda activate tetrio
pip install -r requirements.txt
```

## Usage

1. Run python script

```
conda activate tetrio
python test.py
```

2. Set the coordinates of first and second block while waiting for the countdown in tetrio


![screenshot](https://github.com/AlexanderLJX/Tetrio-bot/assets/83382087/c6b4ab6c-05e6-4eb1-b8b3-eb86a21980ce)

- Hover your cursor over somewhere below the middle of the first block and press `[`
- Hover your cursor over somewhere below the middle of the last block and press `]`
- Hover your cursor over the top left of the tetris board and press `-`
- Hover your cursor over the bottom right of the tetris board and press `=`
- Press spacebar while the game is counting down to start
- Hold down esc to stop the script

*Alternatively you can set the coordinates directly in the script, other settings are also in the script

Configure additional settings directly in the script

## Tetrio settings
- ARR 0ms
- DAS 40ms
- Set Graphics Minimal for optimum performance
- Default Guideline Controls
- Make sure tetris pieces are default color

## Advisory

Using the bot may get your IP and Account banned, advised not to break the world record.

![Capture](https://github.com/AlexanderLJX/Tetrio-bot/assets/83382087/8ea50bc0-ffd8-49b6-8a26-23fe7e1b21f1)


## To-do
- T-spins
- cython version