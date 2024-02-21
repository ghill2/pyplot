from pytower.plot.objects import *


class TestObjects:
    __test__ = False

    def __init__(self):
        pass

    #     self.bar_plot = BarPlot(self.df)

    def test_bar_plot_data(self):
        self.bar_plot.data()

    def test_line_to_json(self):
        print(Line(data=self.data, name="MyName", width=5, color="red").to_json(self.index))


if __name__ == "__main__":
    TestObjects().test_line_to_json()
