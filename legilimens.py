from typing import Optional, IO, List, Dict, Any, Type
from argparse import ArgumentParser
from types import TracebackType
from tempfile import TemporaryDirectory
import traceback
import sqlite3
import json
import os
import sys

MAGIC_HEADER = b'GVAS'
DB_IMAGE_STR = b'RawDatabaseImage'
QUERIES = {'CollectionDynamic': "SELECT ItemID FROM CollectionDynamic WHERE ItemState='Obtained';",
           'SphinxPuzzleDynamic': "SELECT SphinxPuzzleGUID FROM SphinxPuzzleDynamic WHERE EInteractiveState=34;",
           'LootDropComponentDynamic': "SELECT LootGroup FROM LootDropComponentDynamic;",
           'EconomicExpiryDynamic': "SELECT UniqueID FROM EconomicExpiryDynamic;",
           'MiscDataDynamic': "SELECT DataName FROM MiscDataDynamic WHERE DataValue='1';",
           'MapLocationDataDynamic': "SELECT MapLocationID FROM MapLocationDataDynamic WHERE State=11;",
           'AchievementDynamic': "SELECT OneOfEach FROM AchievementDynamic WHERE AchievementID='PFA_43';",
           'PlayerStatsDynamic': "SELECT ActivityName FROM PlayerStatsDynamic WHERE ActivityValue='Complete';",
           'CollectionDynamic2': "SELECT ItemID FROM CollectionDynamic WHERE ItemState='Obtained' AND SubcategoryID='Exploration' AND CategoryID='Conjurations';"}
AFFECTED_TYPES = {'CollectionDynamic': ['Revelio field guide pages'],
                  'SphinxPuzzleDynamic': ['Merlin trials'],
                  'LootDropComponentDynamic': ['Vivarium chests'],
                  'EconomicExpiryDynamic': ['Butterfly chests'],
                  'MiscDataDynamic': ['Brazier/Moth/Statue field guide pages', 'Daedalian Keys'],
                  'MapLocationDataDynamic': ["Flying field guide pages", "Collection Chests", "Demiguise Moons", "Balloon Sets", "Landing Platforms", "Astronomy Tables", "Ancient Magic Hotspots", "Infamous Foes"],
                  'AchievementDynamic': ['Finishing Touches enemies'],
                  'PlayerStatsDynamic': ['Butterfly quest bug detector'],
                  'CollectionDynamic2': ['Conjuration bug detector']}
TABLES = {'Revelio': 'CollectionDynamic',
          'Merlin': 'SphinxPuzzleDynamic',
          'VivariumChest': 'LootDropComponentDynamic',
          'ButterflyChest': 'EconomicExpiryDynamic',
          'Moth': 'MiscDataDynamic',
          'Brazier': 'MiscDataDynamic',
          'Statue': 'MiscDataDynamic',
          'DaedalianKey': 'MiscDataDynamic',
          'Flying': 'MapLocationDataDynamic',
          'ArithmancyChest': 'MapLocationDataDynamic',
          'MiscConjChest': 'MapLocationDataDynamic',
          'MiscWandChest': 'MapLocationDataDynamic',
          'DungeonChest': 'MapLocationDataDynamic',
          'CampChest': 'MapLocationDataDynamic',
          'Demiguise': 'MapLocationDataDynamic',
          'Astronomy': 'MapLocationDataDynamic',
          'Landing': 'MapLocationDataDynamic',
          'Balloon': 'MapLocationDataDynamic',
          'AncientMagic': 'MapLocationDataDynamic',
          'Foe': 'MapLocationDataDynamic',
          'FinishingTouchEnemy': 'AchievementDynamic'}
NAMES = {'Revelio': ('Field guide page', 'Revelio'),
         'Merlin': ('Merlin Trial', ''),
         'VivariumChest': ('Collection Chest', 'Vivarium'),
         'ButterflyChest': ('Butterfly Chest', ''),
         'Moth': ('Field guide page', 'Moth painting'),
         'Brazier': ('Field guide page', 'Confringo brazier'),
         'Statue': ('Field guide page', 'Levioso statue'),
         'Flying': ('Field guide page', 'Flying'),
         'ArithmancyChest': ('Collection Chest', 'Arithmancy door'),
         'MiscConjChest': ('Collection Chest', ''),
         'MiscWandChest': ('Collection Chest', ''),
         'DungeonChest': ('Collection Chest', 'Dungeon'),
         'CampChest': ('Collection Chest', 'Bandit camp'),
         'Demiguise': ('Demiguise Moon', ''),
         'Astronomy': ('Astronomy Table', ''),
         'Landing': ('Landing Platform', ''),
         'Balloon': ('Balloon Set', ''),
         'AncientMagic': ('Ancient Magic Hotspot', ''),
         'Foe': ('Infamous Foe', ''),
         'DaedalianKey': ('Daedalian Key', ''),
         'FinishingTouchEnemy': ('Finishing Touch Enemy', '')}
REGIONS = {'The Library Annex': 'Hogwarts',
           'The Astronomy Wing': 'Hogwarts',
           'The Bell Tower Wing': 'Hogwarts',
           'The South Wing': 'Hogwarts',
           'The Great Hall': 'Hogwarts',
           'The Grand Staircase': 'Hogwarts',
           'Hogsmeade': '',
           'North Ford Bog': 'The Highlands',
           'Forbidden Forest': 'The Highlands',
           'North Hogwarts Region': 'The Highlands',
           'Hogsmeade Valley': 'The Highlands',
           'South Hogwarts Region': 'The Highlands',
           'Hogwarts Valley': 'The Highlands',
           'Feldcroft Region': 'The Highlands',
           'South Sea Bog': 'The Highlands',
           'Coastal Cavern': 'The Highlands',
           'Poidsear Coast': 'The Highlands',
           'Marunweem Lake': 'The Highlands',
           'Manor Cape': 'The Highlands',
           'Cragcroftshire': 'The Highlands',
           'Clagmar Coast': 'The Highlands',
           'Vivariums': 'Hogwarts',
           'Butterflies': '',
           'Daedalian Keys': '',
           'Finishing Touches': 'Achievements'}
DIR_NAME = os.path.dirname(sys.argv[0])
TITLE = r"""
  _                _ _ _                          
 | |              (_) (_)                         
 | |     ___  __ _ _| |_ _ __ ___   ___ _ __  ___ 
 | |    / _ \/ _` | | | | '_ ` _ \ / _ \ '_ \/ __|
 | |___|  __/ (_| | | | | | | | | |  __/ | | \__ \
 |______\___|\__, |_|_|_|_| |_| |_|\___|_| |_|___/
              __/ |                               
             |___/                                

A Hogwarts Legacy tool to find your missing collectibles
https://github.com/Malin001/Legilimens-Hogwarts-Legacy-Collectible-Finder
"""


class SaveReader:
    def __init__(self, file: str):
        self._file: str = os.path.abspath(file)
        self._conn: Optional[sqlite3.Connection] = None
        self._cur: Optional[sqlite3.Cursor] = None
        self._temp_dir: Optional[TemporaryDirectory]
        self._db_file: Optional[IO] = None

    def __enter__(self) -> 'SaveReader':
        # Read file
        save_data = open(self._file, 'rb').read()
        assert save_data.startswith(MAGIC_HEADER), 'Magic header not found'
        # Extract SQL database bytes
        db_start_idx = save_data.index(DB_IMAGE_STR) + 65
        db_size = int.from_bytes(save_data[db_start_idx-4:db_start_idx], byteorder='little')
        db_data = save_data[db_start_idx:db_start_idx+db_size]
        # Create a temporary SQL database file
        self._temp_dir = TemporaryDirectory()
        db_file = os.path.join(self._temp_dir.name, 'temp.db')
        open(db_file, 'wb+').write(db_data)
        # Connect with sqlite3
        self._conn = sqlite3.connect(db_file)
        self._cur = self._conn.cursor()
        # Check that we can execute queries
        self._cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        _ = list(self._cur.fetchall())
        # tables = set(map(lambda x: x[0], self._cur.fetchall()))
        # assert tables.issuperset(QUERIES.keys()), 'Necessary tables not found'
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> bool:
        if self._cur is not None:
            self._cur.close()
        if self._conn is not None:
            self._conn.close()
        if self._temp_dir is not None:
            self._temp_dir.cleanup()
        return False

    def execute_query(self, sql_query: str) -> List[List[Any]]:
        self._cur.execute(sql_query)
        return self._cur.fetchall()


class Legilimens:
    def __init__(self):
        self._collectibles: List[Dict[str, str | int]] = json.load(open(os.path.join(DIR_NAME, 'collectibles.json')))
        self._bugs = {'butterfly': False, 'conjuration': False}

    # Gets the path to save file either as a command line argument or as user input
    @staticmethod
    def _get_save_file() -> str:
        # Get file from the command line
        parser = ArgumentParser(description='Legilimens: TODO')
        parser.add_argument('file', nargs='?', type=str, default='', help='The Hogwarts Legacy .sav file to examine')
        file = parser.parse_args().file
        # If no file was given, prompt the user to input it instead
        if not file:
            file = input('.sav file path: ').strip()
            if file and file[0] == '"' and file[-1] == '"':
                file = file[1:-1]
        return file

    # Checks whether each collectible has been found. Returns the error if one occurs
    def _read_save(self) -> str:
        save_file = ''
        try:
            # Read sql tables
            save_file = self._get_save_file()
            sql_data = dict()
            errors = list()
            with SaveReader(save_file) as save:
                for table, query in QUERIES.items():
                    try:
                        sql_data[table] = set(map(lambda x: x[0], save.execute_query(query)))
                        if table == 'AchievementDynamic':
                            sql_data[table] = {k for row in sql_data[table] for k in row.split(',')}
                            sql_data[table].discard('')
                    except sqlite3.DatabaseError:
                        errors += AFFECTED_TYPES[table]
            if len(sql_data) == 0:
                return f'Legilimens was unable to read the database in your save file'
            if errors:
                print('SQLite was unable to read parts of the database')
                print("The following collectible types were affected and won't work correctly:")
                print(', '.join(errors))
            # Find collectibles
            for collectible in self._collectibles:
                if TABLES[collectible['type']] in sql_data:
                    collectible['collected'] = (collectible['key'] in sql_data[TABLES[collectible['type']]])
                else:
                    collectible['collected'] = False
            # Check for butterfly bug
            if all(table in sql_data for table in ('EconomicExpiryDynamic', 'PlayerStatsDynamic')):
                if 'PlayerStatsDynamic' in sql_data and 'COM_11' in sql_data['PlayerStatsDynamic'] and any(c['type'] == 'ButterflyChest' and c['index'] == 1 and not c['collected'] for c in self._collectibles):
                    self._bugs['butterfly'] = True
            # Check for conjuration bug
            if all(table in sql_data for table in ('CollectionDynamic2', 'LootDropComponentDynamic', 'EconomicExpiryDynamic', 'MapLocationDataDynamic')):
                chests_opened = sum(1 for c in self._collectibles if c['collected'] and c['type'] in ('MiscConjChest', 'ArithmancyChest', 'DungeonChest', 'ButterflyChest', 'VivariumChest'))
                if 'CollectionDynamic2' in sql_data and chests_opened > len(sql_data['CollectionDynamic2']):
                    self._bugs['conjuration'] = True
            return ''
        except FileNotFoundError:
            return f'The file "{save_file}" couldn\'t be found'
        except (ValueError, AssertionError, TypeError, sqlite3.DatabaseError):
            return f'Legilimens was unable to read the save file "{save_file}"'

    # Converts a collectible dict into a string
    @staticmethod
    def _collectible_str(collectible: Dict[str, str | int]) -> str:
        s, name2 = '', ''
        if collectible['type'] != 'FinishingTouchEnemy':
            name1, name2 = NAMES[collectible['type']]
            s += f'{name1} #'
        s += f'{collectible["index"]}'
        if name2:
            s += f' ({name2})'
        if collectible["video"]:
            s += f' - https://youtu.be/{collectible["video"]}&t={collectible["time"]}'
        else:
            s += ' - No video yet'
        return s

    # Converts the missing collectibles in the given region to a string
    def _print_region(self, region: str) -> None:
        missing = [collectible for collectible in self._collectibles if collectible['region'] == region]
        if not missing:
            return
        videos = [f'https://youtu.be/{video_id}' for video_id in sorted(set(map(lambda c: c['video'], missing))) if video_id]
        if REGIONS[region]:
            print(f'\n{REGIONS[region]} - {region} ({", ".join(videos)})')
        else:
            print(f'\n{region} ({", ".join(videos)})')
        missing.sort(key=lambda c: f"{c['video']} {str(c['time']).zfill(4)} {c['type']} {c['index']}")
        for collectible in missing:
            print(f'\t{self._collectible_str(collectible)}')

    def _print_bug_output(self):
        if self._bugs['butterfly']:
            print("\nYour save seems to be affected by the butterfly quest bug. If you're unable to collect Butterfly Chest #1,\nconsider using https://hogwarts-legacy-save-editor.vercel.app or https://www.nexusmods.com/hogwartslegacy/mods/778 to fix it.")
        if self._bugs['conjuration']:
            print("\nYour save seems to be affected by the 139/140 conjuration bug. If you can't find your last\nexploration conjuration, consider using https://www.nexusmods.com/hogwartslegacy/mods/832 to fix it.")

    def run(self) -> None:
        # Read save file
        error = self._read_save()
        if error:
            print(error)
            return
        self._collectibles = [c for c in self._collectibles if not c['collected']]
        regions = sorted(set(map(lambda c: c['region'], self._collectibles)))
        if not regions:
            print("Congratulations! You've gotten every collectible that Legilimens can detect")
            self._print_bug_output()
            print('\nIf you expected Legilimens to detect something, you can create an issue on GitHub with your save file attached:')
            print('https://github.com/Malin001/Legilimens-Hogwarts-Legacy-Collectible-Finder/issues')
            return
        regions.sort(key=lambda r: REGIONS[r])
        [self._print_region(region) for region in regions]
        self._print_bug_output()


# Main functions
def main():
    print(TITLE)
    try:
        Legilimens().run()
    except Exception:
        print(f'Legilimens encountered an unexpected error')
        traceback.print_exc()
        print('If the problem persists, you can create an issue on GitHub with your save file attached:')
        print('https://github.com/Malin001/Legilimens-Hogwarts-Legacy-Collectible-Finder/issues')
    finally:
        input('\nPress enter to close this window...')


if __name__ == '__main__':
    main()
