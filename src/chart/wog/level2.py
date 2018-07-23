from notebooks.wog_overview import WOGLevel2

from chart import ChartBase


class Chart(ChartBase, WOGLevel2):
    key = 'wog_level2'
    df_key = 'wog_level1'
    plot_type = 'service_name_plot'
    is_interactive = True
