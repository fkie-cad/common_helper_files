import subprocess


def get_version_string_from_git(directory_name: str) -> str:
    return subprocess.check_output(['git', 'describe', '--always'], cwd=directory_name).strip().decode('utf-8')
