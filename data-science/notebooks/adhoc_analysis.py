from matplotlib.ticker import FuncFormatter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.figure import figaspect
import matplotlib.pyplot as plt

plt.switch_backend('agg')

try:
    from notebooks.styles import colors
    from notebooks.base import ChartBase
except ImportError:
    from styles import colors
    from base import ChartBase

import pandas as pd


class AdHocAnalysisTool1Mixins(object):
    
    def adhoc_analysis_plot(self, df):
        pass


class AdHocAnalysisTool1(AdHocAnalysisTool1Mixins, ChartBase):
    
    def generate_dataframe(self, df):
        pass
        
    def generate_graph(self, df):
        pass