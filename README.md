# Legilimens
Legilimens is a tool to help you find your last few missing collectibles in Hogwarts Legacy and finally get that 100% completion. All you need to do is run Legilimens with your save file, and it will analyze and return a list of every collectible that you're missing, including a link to a Youtube video with a timestamp showing its location. Legilimens does **not** edit your save file, it only reads the databases contained within it.

Legilimens has now been rewritten in C++ to allow for use as a completely standalone executable! It also has filters, automatic save file detection, and much better formatting. Check it out [here](https://github.com/Malin001/Legilimens-Hogwarts-Legacy-cpp).

You can also find this tool on [Nexus](https://www.nexusmods.com/hogwartslegacy/mods/556).

#### What Legilimens can find:
- Field Guide Pages
- Collection Chests
- Demiguise Statues
- Vivarium Chests
- Butterfly Chests
- Daedalian Keys
- Merlin Trials
- Balloon Sets
- Landing Platforms
- Ancient Magic Hotspots
- Infamous Foes
- "Finishing Touch" achievement enemies (EXPERIMENTAL, LIKELY BROKEN)

#### What it *can't* find:
- Items that you are *required* to get during a quest. For example, there are two field guide pages that you are forced to pick up during the History of Magic class quest
- Collectible items that can be bought from vendors
- Collectible items that are rewards for completing quests

## Usage
Legilimens is available both as an executable file for convenience, and as a Python script for those wary of viruses so that you can actually see the code that you're running. Note that you can likely find your save files in `C:/Users/<user>/AppData/Local/HogwartsLegacy/Saved/SaveGames/<user_id>/`

#### How to use the executable:
1. Download and extract the latest [Legilimens executable release](https://github.com/Malin001/Legilimens-Hogwarts-Legacy-Collectible-Finder/releases/latest).
2. Either drag your `.sav` file onto `legilimens.exe`, or just run `legilimens.exe` and input the path to your `.sav` file when prompted.
![preview](images/exe1.gif)
![preview](images/exe2.gif)

#### How to use the Python script:
1. Install any version of [Python 3](https://www.python.org/downloads/). I've only tested it with Python 3.10, but it should work with earlier/later versions as well.
2. Download and extract the latest [Legilimens Python release](https://github.com/Malin001/Legilimens-Hogwarts-Legacy-Collectible-Finder/releases/latest). You should end up with `legilimens.py` and `collectibles.json` in the same folder.
3. Either drag your `.sav` file onto `legilimens.py`, or run the script with `python "<path>/<to>/legilimens.py" "<path>/<to>/<your>/<save>/<file>.sav"`, or just run `python "<path>/<to>/legilimens.py"` and input the path to your `.sav` file when prompted.
![preview](images/python1.gif)

#### How to output to a text file
1. First, open the command prompt and navigate to the folder containing `Legilimens.exe` or `legilimens.py` by running `cd path/to/legilimens/folder`
2. Then, you can run `Legilimens.exe path/to/your/save/file.sav > output.txt` or `python legilimens.py path/to/your/save/file.sav > output.txt`
3. Legilimens will write to the file `output.txt` instead. Remember to hit enter for the "Press enter to close this window..." even though it doesn't appear on screen

## FAQ
#### Legilimens says I'm missing Butterfly Chest #1, but there aren't any butterflies there and I've already done the "Follow the Butterflies" quest?
- This is a known bug with Hogwarts Legacy, where following any of the other 14 butterflies allows you to complete the quest, which then prevents the intended quest butterflies from ever appearing. Legilimens doesn't have a fix for this, but I believe there are some save editors which can reactivate the quest and allow you to get the last butterflies.
#### I'm missing a single conjuration exploration collectible, but Legilimens doesn't detect anything?
- This is almost certainly another [bug in the game](https://hogwartslegacy.bugs.wbgames.com/bug/HL-3868). I don't know what causes it. I don't know how to fix it. I've spent hours looking at my code and at saves that people have sent me with this problem, and I haven't found anything that indicates it's a problem with Legilimens. If this bug happens to you and you manage to find where the last conjuration is, *please* let me know so I can update this tool.
#### I have 33/34 Field Guide Pages in The Bell Tower Wing, but Legilimens says I've completed them all. Where is it?
- This is a known bug in Hogwarts Legacy that has since been patched, where a certain Bell Tower Wing [flying page](https://youtu.be/KnHZ5gVb_qk&t=104) doesn't count towards your total.
#### Legilimens says that I'm missing something that I've already collected, or doesn't detect all of my missing collectibles, or links to the wrong Youtube video/timestamp, or any other error.
- It's likely an error in my code, so open an [issue](https://github.com/Malin001/Legilimens-Hogwarts-Legacy-Collectible-Finder/issues) on GitHub, and attach your `.sav` file. I'll do my best to figure out what went wrong and fix it as soon as possible. If you don't have a GitHub account, you can also email your save file to me at Malin4750@gmail.com, or post the output of Legilimens on [Nexus](https://www.nexusmods.com/hogwartslegacy/mods/556). ***If you don't send me either the save file or output, I won't be able to fix the problem for everyone else.***
#### I'm getting the error "SQLite was unable to read parts of the database", which is preventing me from finishing certain collectibles. How can I fix this?
- For some reason, it's possible for parts of your save file to be corrupted and unreadable by SQLite. Unfortunately, I haven't been able to figure out a fix or workaround yet. Sorry.

## Building your own executable
If you want the convenience of the executable release, while still knowing exactly what code it contains, you easily build it yourself:
1. [Download](https://github.com/Malin001/Legilimens-Hogwarts-Legacy-Collectible-Finder/archive/refs/heads/main.zip) the GitHub repository
2. Run `pip install cx_Freeze`
3. Run `python setup.py build`
4. The folder containing the executable and dependencies should now be located in `build/`

## Credit
- Thanks to [100% Guides](https://www.youtube.com/@100Guides), [Game Guides Channel](https://www.youtube.com/@GameGuideslolz), [ZaFrostPet](https://www.youtube.com/@ZaFrostPet), and [Lukinator 2321](https://www.youtube.com/@lukinator2321) on Youtube for making the videos that Legilimens links to.
- Also thanks to [ekaomk](https://github.com/ekaomk/Hogwarts-Legacy-Save-Editor), whose Hogwarts Legacy Save Editor code I looked at to learn how to read the save files.
- Thanks to [lillaka](https://www.nexusmods.com/users/2211740) for not only giving me ideas to improve the mod, but actually implementing those ideas and giving me the code
