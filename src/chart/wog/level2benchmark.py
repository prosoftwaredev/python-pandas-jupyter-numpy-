from notebooks.wog_overview import WOGLevel2Benchmark

from chart import ChartBase


class Chart(ChartBase, WOGLevel2Benchmark):
    key = 'wog_level2benchmark'
    df_key = 'wog_level2'
