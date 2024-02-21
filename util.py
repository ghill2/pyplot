import os
import subprocess


def open_plot(path):
    # path = os.path.join(
    #         PACKAGE_ROOT,
    #         "plot",
    #         "template"
    #     )
    cmd = f'cd "{path}"; npm run dev;'
    os.system(cmd)
    #  Start-Process "http://localhost:8080/"


def npm_exists() -> bool:
    result = subprocess.run(
        ["command", "-v", "npm"],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def _open_plot(path):
    cmd = f'cd "{path}"; npm run dev; Start-Process "http://localhost:8080/"'
    os.system(cmd)
