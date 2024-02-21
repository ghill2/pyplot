from datetime import datetime

import pandas as pd
from colour import Color

from pyfutures.core.datetime import NANOSECONDS_IN_MILLISECOND
from pytower.common.util import force_list
from pyfutures.core.datetime import dt_to_unix_nanos_vectorized
from pytower.data.verify import force_datetime_index
from pytower.data.verify import force_multi_index

class Line:
    def __init__(
        self,
        data: pd.Series,
        name: str = "Default Name",
        color: Color or str = "red",
        width: int = 3,
    ):
        assert isinstance(data, pd.Series)
        # assert is_number(data[0])
        # value can't be NaN.

        self.data = data
        self.name = name
        self.width = width
        self.color = color
        # if isinstance(self.color, str):
        #     self.color = Color(self.color)

    def to_dict(self, index) -> dict:
        index: pd.Int64Index = _convert_index(index)

        return {
            "name": self.name,
            "type": "EMA",  # EMA, SMA https://github.com/tvjsx/trading-vue-js/tree/master/docs/overlays#spline
            "data": _zip_index(index, [self.data.tolist()]),
            "settings": {
                "lineWidth": self.width,
                "color": self.color,
                # TODO add upper and lower,
                # "display": True
            },
        }


class Plot:
    def __init__(
        self,
        height: int,
        name: str,
    ):
        self.height = height
        self.name = name


class LinePlot(Plot):
    def __init__(
        self,
        lines: list[Line] = [],
        name: str = "LinePlot",
        height: int = 500,
    ):
        super().__init__(height, name)

        self.lines = force_list(lines)

    def data(self, index) -> list[list]:
        return _zip_index(index, [line.data.tolist() for line in self.lines])

    def to_dict(self, index) -> dict:
        index: pd.Int64Index = _convert_index(index)

        # https://github.com/tvjsx/trading-vue-js/tree/master/docs/overlays#splines
        return {
            "name": self.name,
            "type": "Splines",  # multiple lines
            "data": self.data(index),
            "settings": {
                "lineWidths": [line.width for line in self.lines],
                "colors": [str(line.color) for line in self.lines],
            },
        }


class BarPlot(Plot):
    def __init__(
        self,
        df: pd.DataFrame,
        lines: list[Line] = [],
        name: str = "BarPlot",
        height: int = 835,
        show_volume: bool = False,
    ):
        super().__init__(height, name)
        # TODO Dataframe needs to be bar and multi index

        # assert DataVerify.dataframe(df, DataframeFormat.BAR)
        self.df = df

        self.lines = force_list(lines)
        self.show_volume = show_volume

    @staticmethod
    def _format_dataframe(df):
        df = force_datetime_index(df)

        keys = list(df.columns)
        valid_bars = all(key in keys for key in ("open high low close".split()))
        if not valid_bars:
            df = force_multi_index(df)["bid"]

        if "volume" in keys:
            df = df["open high low close volume".split()]
        else:
            df = df["open high low close".split()]

        return df

    def to_dict(self, index) -> dict:
        index: pd.Int64Index = _convert_index(index)
        df = self._format_dataframe(self.df)

        data = _zip_index(
            index,
            [list(series) for _, series in df.iteritems()],
        )

        return {
            "type": "Candles",
            "indexBased": True,
            "data": data,
            "settings": {
                "priceLine": True,  # default True
                "showVolume": self.show_volume,  # default True
            },
            # "grid": {
            #     log
            # }
        }


class TradeLine(Line):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self, index) -> dict:
        # merge the trade line to the index on the chart
        # merge data into the index
        # assert isinstance(self.data, pd.DataFrame)
        # assert isinstance(self.data.index, pd.DatetimeIndex)
        df = self.data

        if not isinstance(df.index, pd.DatetimeIndex):
            df.set_index("ts_init")

        df = df["side filled_qty".split()]
        side = df.side

        # make SELL quantities negative
        df.filled_qty = df.filled_qty.astype(float)
        mask = side == "SELL"
        df.filled_qty[mask] = df.filled_qty[mask] * -1

        df.filled_qty = df.filled_qty.cumsum()

        side[side == "BUY"] = 1
        side[side == "SELL"] = 0

        # add duplicate indexes together
        new_index = []
        for dt in df.index:
            # pad / ffill: find the PREVIOUS index value if no exact match.
            closest_previous_match: int = index.get_loc(dt, method="ffill")
            closest_previous_match: datetime = index[closest_previous_match]
            new_index.append(closest_previous_match)

        df.index = pd.DatetimeIndex(new_index)

        # remove exit trades where it changes direction
        df = df[~df.index.duplicated(keep="last")]

        df = df.drop_duplicates(keep="first")
        buy_sell: list = list(df.side)
        price: list = list(df.filled_qty)
        # other_index = _convert_index(index)
        # for i in index:
        #     assert i in other_index
        data = _zip_index(index, [buy_sell, price])

        # index: pd.Int64Index = _convert_index(df.index)
        return {
            "name": "TradesIndicator",
            "type": "Trades",
            "data": data,
            "settings": {
                "z-index": 5,
                "markerSize": "50",
            },
        }


def _zip_index(index: list, lists: list[list]) -> list[list]:
    # assert len(index) == len(data)
    list_of_lists = isinstance(lists[0], list)
    assert list_of_lists

    return [[index] + [l[i] for l in lists] for i, index in enumerate(index)]


def _convert_index(index):
    if isinstance(index, pd.Int64Index):
        return index
    return dt_to_unix_nanos_vectorized(index) // NANOSECONDS_IN_MILLISECOND  # unix ms timestamp
