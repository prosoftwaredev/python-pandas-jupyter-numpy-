from notebooks.agency_performance import AgencyPerformanceLevel1

from chart import ChartBase


class Chart(ChartBase, AgencyPerformanceLevel1):
    key = 'myagency_level1'
    df_key = 'myagency_level1'
