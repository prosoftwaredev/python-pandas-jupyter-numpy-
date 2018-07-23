from notebooks.wog_overview import WOGLevel1

from chart import ChartBase


class Chart(ChartBase, WOGLevel1):
    key = 'wog_level1'
    df_key = 'wog_level1'
    plot_type = 'service_classification_plot'
    is_interactive = True
