from notebooks.agency_performance import AgencyCostCategoryBreakdown

from chart import ChartBase


class Chart(ChartBase, AgencyCostCategoryBreakdown):
    key = 'myagency_level2_cost'
    df_key = 'myagency_level2_cost'
