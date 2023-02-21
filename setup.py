from cx_Freeze import setup, Executable


options = {
    'build_exe': {
        'excludes': ['tkinter', 'asyncio', 'concurrent', 'ctypes', 'disutils', 'email', 'html', 'http', 'lib2to3',
                     'logging', 'multiprocessing', 'pydoc_data', 'test', 'unittest', 'urllib', 'xml', 'xmlrpc',
                     'bz2', 'decimal', 'hashlib', 'lzma', 'socket', 'select'],
        'packages': ['typing', 'argparse', 'types', 'tempfile', 'traceback', 'sqlite3', 'json', 'os'],
        'include_files': ['collectibles.json', 'README.md']
    }
}


setup(
    name='Legilimens',
    version='1.0',
    description='A tool to help you find those pesky missing collectibles in Hogwarts Legacy',
    author='Malin',
    options=options,
    executables=[Executable('legilimens.py')]
)
