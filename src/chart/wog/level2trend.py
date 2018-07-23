from notebooks.wog_overview import WOGLevel2Trend

from chart import ChartBase


class Chart(ChartBase, WOGLevel2Trend):
    key = 'wog_level2trend'
    df_key = 'wog_level2'
