import subprocess
from pathlib import Path

subprocess.run([str(Path(__file__).parent / "Hash" / "hash.exe")])

