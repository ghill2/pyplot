import os
import shutil
from pathlib import Path

from pytower import PACKAGE_ROOT
from pytower.common.util import force_list
from pytower.plot.objects import BarPlot
from pytower.plot.objects import LinePlot
from pytower.plot.util import npm_exists


class PlotFolder:
    def __init__(self, path):
        self.path = path

        is_valid_folder_path = Path(path).suffix == ""
        assert is_valid_folder_path
        # os.makedirs(path, exist_ok=True) #

    def initialized(self) -> bool:
        # Check to see if the template files have been copied before
        return (Path(self.path) / "package.json").exists()

    def initialize(self):
        # copy a new template folder
        print("Copying plot dir...")
        template_dir = os.path.join(
            PACKAGE_ROOT,
            "plot",
            "template",
        )

        shutil.copytree(template_dir, self.path)


class PlotConfig:
    def __init__(
        self,
        bar_plot: BarPlot,
        line_plots: LinePlot = [],
        title="Default Title",
    ):
        self.bar_plot = bar_plot
        self.line_plots = force_list(line_plots)
        self.title = title

    def write(self, path):
        folder = PlotFolder(path)

        if not folder.initialized():
            folder.initialize()

        from pytower.plot.io import PlotIO  # avoid circular import error

        json_file = Path(path) / "data" / "data.json"

        if json_file.exists():
            json_file.unlink()

        os.makedirs(os.path.dirname(json_file), exist_ok=True)

        PlotIO().write(self, str(json_file))

        return self  # returns self for chaining commands

    def open(self):
        if not npm_exists():
            raise RuntimeError("To open the plot, npm needs to exist on path")

        cmd = f'cd "{self.path}"; npm run dev;'
        os.system(cmd)
        #  Start-Process "http://localhost:8080/"

        return self  # returns self for chaining commands

    def kill(self):
        # https://stackoverflow.com/a/32592965
        # Kill processes listening to port the chart uses.
        os.system("kill -9 $(lsof -t -i:8080)")
        return self  # returns self for chaining commands


if __name__ == "__main__":
    pass

    # d['on_chart'] = []
    # d['off_chart'] = []
    # d['colors'] = {
    #     "colorBack": '#fff',
    #     "colorGrid": '#eee',
    #     "colorText": '#333',
    # }
