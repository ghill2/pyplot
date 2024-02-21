from pathlib import Path

import simplejson

from pytower.plot.config import PlotConfig


class PlotIO:
    def write(self, config: PlotConfig, path: str) -> None:
        json_txt = self._create_json(config)

        self._write_json(json_txt, path)

    def _create_json(self, config: PlotConfig) -> dict:
        bar_plot = config.bar_plot
        line_plots = config.line_plots
        index = bar_plot.df.index

        # https://github.com/tvjsx/trading-vue-js/tree/master/docs/api#data-structure
        json_data = {}
        json_data["chart"] = bar_plot.to_dict(index)

        bar_lines = bar_plot.lines

        if bar_lines:
            json_data["onchart"] = [line.to_dict(index) for line in bar_lines]

        if line_plots:
            json_data["offchart"] = [line_plot.to_dict(index) for line_plot in line_plots]

        return json_data

    def _write_json(self, data: dict, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        simplejson.dump(
            data,
            open(path, "w"),
            indent=4,
            ignore_nan=True,
        )  # use simple json to properly convert NaN to null
        print(f"Written {path}...")

        # # replace the data file in the target folder
        # data_file = os.path.join(
        #     self.path,
        #     "data",
        #     "data.json"
        # )
        # also write the data file in the repo incase running live server
