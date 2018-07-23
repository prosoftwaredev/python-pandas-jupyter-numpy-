from notebooks.agency_performance import AgencyPerformanceLevel2

from chart import ChartBase


class Chart(ChartBase, AgencyPerformanceLevel2):
    key = 'myagency_level2'
    df_key = 'myagency_level2'
