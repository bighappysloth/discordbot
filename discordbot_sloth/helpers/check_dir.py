from pathlib import Path

def check_dir(dirname):
    if not Path(dirname):
        Path.mkdir(dirname)