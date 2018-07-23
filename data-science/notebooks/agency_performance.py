from matplotlib.ticker import FuncFormatter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.figure import figaspect
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt, mpld3
from collections import ChainMap

plt.switch_backend('agg')

try:
    from notebooks.styles import colors
    from notebooks.base import ChartBase
    from notebooks.plugins import *
except ImportError:
    from styles import colors
    from base import ChartBase
    from plugins import *

import pandas as pd


class AgencyPerformanceLevel1Mixins(object):

    def shorten_ytick_labels(self, labels):
        trans_map = {'Management': 'Mgmt.'}
        shorts = []
        for label in labels:
            short = label
            if len(label) > 15:
                short = [trans_map.get(x, x) for x in label.split()]
                short = ' '.join(short)
            shorts.append(short)
        return shorts

    def performance_level1_plot(self, df, urls_map=None, asl=False):
        """
        # Initialize figure and axes
        if interactive:
            fig = plt.figure(figsize=(14,13))
            gs = gridspec.GridSpec(2, 3, height_ratios=[2, 4])
            ax1 = fig.add_subplot(gs[0, 0])
            ax2 = fig.add_subplot(gs[0, 1])
            ax3 = fig.add_subplot(gs[0, 2])
            ax4 = fig.add_subplot(gs[1, :])
        else:
            fig = plt.figure(figsize=(10,18))
            gs = gridspec.GridSpec(2, 5, width_ratios=[6,4,6,1,3])
            ax1 = fig.add_subplot(gs[0, 0:1])
            ax2 = fig.add_subplot(gs[1, 0:1])
            ax3 = fig.add_subplot(gs[0, 2])
            ax4 = fig.add_subplot(gs[1, 2:])

        def draw_bar_graphs(group, sdf, ax, order):
            # Draw the pie graph only
            patches = []
            texts = []
            bars = ax.barh(range(len(sdf)), sdf['Amount'], color=sdf['Color'], height=0.5, zorder=2)
            ax.set_yticks(range(len(sdf)))
            labels = ax.set_yticklabels(self.shorten_ytick_labels(df['Category']))
            for label in labels:
                label.set_horizontalalignment('left')
            ax.xaxis.grid(color='lightgray', linewidth=2)
            ax.tick_params(axis='x', which='major', labelsize=11, length=0)
            ax.tick_params(axis='y', which='major', labelsize=11, length=0)

            pos1 = ax.get_position() # get the original position
            if order == 0:
                pos1_x0 = pos1.x0 + 0.04
            else:
                pos1_x0 = pos1.x0 + (0.05 * order)
            pos2 = [pos1_x0, pos1.y0,  pos1.width * 0.7, pos1.height]
            ax.set_position(pos2) # set a new position

            xmin, xmax = ax.get_xlim()
            xmin = xmax * 0.01 * -1
            ax.set_xlim(xmin, xmax)

            ax.set_title(group + '\n', fontsize=14)
            ax.title.set_position([0, 1])
            ax.title.set_horizontalalignment('left')

            # Create the tooltips for the bar graph
            for i, bar in enumerate(bars.get_children()):
                style = 'style="background: white; border: 1px solid black; padding: 2px;"'
                fargs = (style, sdf['Category'].iloc[i], sdf['Formatted Amount'].iloc[i])
                label = '<div {}><strong>{}</strong><br>{}</div>'.format(*fargs)
                tooltip = mpld3.plugins.LineHTMLTooltip(bar, label=label, hoffset=15, voffset=-5)
                mpld3.plugins.connect(fig, tooltip)
            return patches, texts

        pie_graphs = []
        groups = ['Corporate Services Functions', 'Human Resource Services Functions', 'Financial Services Functions']
        df = df[df['Group'].isin(groups)]
        axes = [ax1, ax2, ax3]
        counter = 0
        for ax, group in zip(axes, groups):
            sdf = df[df['Group'] == group]
            sdf = sdf.sort_values('Amount', ascending=True)
            patches, texts = draw_bar_graphs(group, sdf, ax, counter)
            pie_graphs.append({
                'patches': patches,
                'ax': ax,
                'df': sdf
            })
            counter += 1
        """
        fig, ax = plt.subplots(nrows=1, ncols=1)
        fig.set_size_inches(10,12)

        bars = ax.barh(range(len(df)), df['Total ASL'], color=df['Color'], height=0.5, zorder=2) if asl else ax.barh(range(len(df)), df['Amount'], color=df['Color'], height=0.5, zorder=2)
        # ax.set_title('\nTotal Service Price\n\n', fontsize=14)
        ax.title.set_position([0, 1])
        ax.title.set_horizontalalignment('left')
        ax.set_title('Level 2 Services', rotation='vertical', x=-0.3, y=0.5, fontsize=14)

        ax.set_yticks(range(len(df)))
        labels = ax.set_yticklabels(self.shorten_ytick_labels(df['Category']))
        for label in labels:
            label.set_horizontalalignment('left')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.xaxis.grid(color='lightgray', linewidth=2)
        ax.tick_params(axis='x', which='major', labelsize=12, length=0)
        ax.tick_params(axis='y', which='major', labelsize=12, length=0)

        pos1 = ax.get_position() # get the original position
        pos2 = [pos1.x0 + 0.15, pos1.y0 + 0.1,  pos1.width, pos1.height]
        ax.set_position(pos2) # set a new position

        xmin, xmax = ax.get_xlim()
        xmin = xmax * 0.002 * -1
        ax.set_xlim(xmin, xmax)
        xaxis_label = 'ASL' if asl else 'Dollars'
        ax.set_xlabel(xaxis_label, fontsize=14)
        ax.yaxis.set_label_coords(0, 1)

        # Create the tooltips for the bar graph
        for i, bar in enumerate(bars.get_children()):
            style = 'style="background: white; border: 1px solid black; padding: 2px;"'
            fargs = (style, df['Category'].iloc[i], df['Formatted Amount'].iloc[i])
            label = '<div {}><strong>{}</strong><br>{}</div>'.format(*fargs)
            tooltip = mpld3.plugins.LineHTMLTooltip(bar, label=label, hoffset=15, voffset=-5)
            mpld3.plugins.connect(fig, tooltip)
        # Create links in x-axis labels
        xlabellinks = TickLabelLink(urls_map, axis='y')
        mpld3.plugins.connect(fig, xlabellinks)
        # Format the x-axis values
        mpld3.plugins.connect(fig, XTickFormat())
        # Fix hbar graph to make it look better
        mpld3.plugins.connect(fig, FixHBarGraph())
        html = mpld3.fig_to_html(fig)
        return html


class AgencyPerformanceLevel1(AgencyPerformanceLevel1Mixins, ChartBase):

    def filter_dataframe(self, df):
        for k,v in self.filter_params.items():
            excluded = ['ASL']
            if k not in excluded and len(v):
                df = df[df[k].isin(v)]
        return df

    def generate_dataframe(self, df):
        self.level2_opts = self.get_level2_service_options(df)
        # Prepare the dataframe needed by the graph
        df = self.filter_dataframe(df)
        if len(df):
            # Remove rows with NaN in Service Classification column
            df = df.dropna(subset=['Service classification'])
            # Strip leading and trailing spaces in values of Service Classification column
            df['Service classification'] = df['Service classification'].str.strip()
            df = df.groupby(['Service classification', 'Service name']).agg({'Total cost': 'sum', 'Total ASL': 'sum'})
            df.reset_index(inplace=True)
            df.rename(columns={'Total cost': 'Amount', 'Service classification': 'Group', 'Service name': 'Category'}, inplace=True)
            asl = 'ASL' in self.filter_params and self.filter_params['ASL'] or False
            if asl:
                df['Formatted Amount'] = df['Total ASL'].apply('{:.2f}'.format)
            else:
                df['Formatted Amount'] = df['Amount'].apply('{:.2f}'.format)
            categories = list(df['Group'].unique())
            color_map = {x:colors[i] for i,x in enumerate(df['Group'].unique())}
            df['Color'] = df.apply(lambda x: color_map[x.Group], axis=1)
        else:
            df = pd.DataFrame()
        df['Formatted Amount'] = df['Formatted Amount'].astype(float)

        return df.sort_values(by=['Group', 'Category'], ascending=True)

    def generate_graph(self, df, base_url=None, **kwargs):
        # Generate the appropriate graph
        results = {'success': False, 'errors': [], 'image': None}
        if len(df):
            # if not base_url:
            #     base_url = 'https://www-integration.benchmarking.fin.gosource.com.au'
            # url = base_url.rstrip('/') + '/chart/my-agency/level2/'
            url = '/chart/my-agency/level2/'
            # Generate the level2-to-level1 mapping needed later
            level2_opts_ = [dict(zip(y, [x] * len(y))) for x,y in self.level2_opts.items()]
            l2tol1_map = dict(ChainMap(*level2_opts_))
            urls_map = self.create_url_mapping(
                df['Category'],
                self.filter_params,
                'service_level2',
                url,
                l2tol1_map=l2tol1_map)
            asl = 'ASL' in self.filter_params and self.filter_params['ASL'] or False
            fig = self.performance_level1_plot(df, urls_map=urls_map, asl=asl)
            b64_string = self.convert_figure_to_base64(fig)
        else:
            results['errors'].append('The selected filter combination did not yield any data points')
        if not results['errors']:
            results['image'] = b64_string
            results['table_json'] = df.set_index('Category').T.to_dict('split')
            results['success'] = True
        return results


class AgencyPerformanceLevel2Mixins(object):

    def _draw_tooltips(self, fig, bars, name, values):
        style = 'style="background: white; border: 1px solid black; padding: 2px;"'
        for i, bar in enumerate(bars):
            label = '<div {}><strong>{}</strong><br>Total cost: ${:,.2f}</div>'
            label = label.format(style, name, values[i])
            tooltip = mpld3.plugins.LineHTMLTooltip(bar, label=label,
                hoffset=15, voffset=-5)
            mpld3.plugins.connect(fig, tooltip)

    def _create_graph(self, title, sdf, fig, ax):
        # Draw the bars
        d1 = sdf[sdf['Data Type'] == 'Agency Unit Cost']
        bars = ax.bar([x - 0.15 for x in range(len(d1))], d1['Value'].values,
            width=0.3, color=colors[1], zorder=2)
        self._draw_tooltips(fig, bars, 'Agency Unit Cost', d1['Value'].values)

        d2 = sdf[sdf['Data Type'] == 'WoG Average Unit Cost']
        bars = ax.bar([x + 0.15 for x in range(len(d2))], d2['Value'].values,
            width=0.3, color=colors[0], zorder=2)
        self._draw_tooltips(fig, bars, 'WoG Average Unit Cost', d2['Value'].values)

        ax.set_xticks(range(len(d2)))
        ax.set_xticklabels(d2['Financial Year'].values)
        #ax.yaxis.set_major_formatter(FuncFormatter(lambda x,pos: '${:,.2f}'.format(x)))
        ax.yaxis.grid(color='#e6e6e6', linewidth=1)
        ax.set_title('\n' + title + '\n', fontsize=17)
        ax.set_ylabel('Total Cost')
        # Draw the line plot
        # d3 = sdf[sdf['Data Type'] == 'Agency Volume']
        # axt = ax.twinx()
        # axt.plot(d3['Value'].values, color='#a5a5a5', zorder=2)
        # axt.patch.set_alpha(0.0)
        # ymin, ymax = axt.get_ylim()
        # axt.set_ylim(0, ymax)
        # axt.set_ylabel('Volume')
        # for x in [ax, axt]:
        #     x.spines['top'].set_visible(False)
        #     x.spines['right'].set_visible(False)
        #     x.spines['left'].set_visible(False)
        #     x.spines['bottom'].set_edgecolor('lightgray')
        #     x.spines['bottom'].set_linewidth(1)
        #     x.tick_params(top='off', bottom='off', left='off', right='off')

    def performance_level2_plot(self, df, selected_sizes=[]):
        # Draw the legend
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 1))
        if len(selected_sizes) == 1:
            size = selected_sizes[0]
            label = 'WoG Ave. Unit Cost - %s Agencies' % size
        else:
            label = 'WoG Ave. Unit Cost for selected agency sizes'
        handles = [
            mpatches.Patch(color=colors[1], label='Agency Unit Cost'),
            # Line2D([], [], color='#a5a5a5', linewidth=2, label='Agency Volume'),
            mpatches.Patch(color=colors[0], label=label)
        ]
        legend = ax.legend(handles=handles, ncol=2, loc='lower left')
        frame = legend.get_frame()
        frame.set_linewidth(0)
        mpld3.plugins.connect(fig, HideSuplotAxes(1))
        legend = mpld3.fig_to_html(fig)

        # Draw the subplots
        subplots = []
        categories = list(df['Category'].unique())
        for i, category in enumerate(categories):
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(5.7, 4))
            sdf = df[df['Category'] == category]
            self._create_graph(category, sdf, fig, ax)
            mpld3.plugins.connect(fig, FixTwinAxes())
            html = mpld3.fig_to_html(fig)
            subplots.append(html)

        return {'legend': legend, 'subplots': subplots}


class AgencyPerformanceLevel2(AgencyPerformanceLevel2Mixins, ChartBase):

    def filter_dataframe(self, df):
        colmap = {
            'Level 1 Service': 'Service classification',
            'Level 2 Service': 'Service name'
        }
        for k,v in self.filter_params.items():
            excluded = ['Agency name']
            if k not in excluded and len(v):
                mapped_k = colmap.get(k, k)
                if k == 'Agency size':
                    df1 = df[df['Agency name'].isin(self.filter_params['Agency name'])]
                    df2 = df[~df['Agency name'].isin(self.filter_params['Agency name'])]
                    df2 = df2[df2['Agency size'].isin(v)]
                    df = pd.concat([df1, df2])
                else:
                    df = df[df[mapped_k].isin(v)]
        if len(self.filter_params['Level 2 Service']) == 0:
            gp = df[['Service name', 'Financial Year']].groupby('Financial Year')
            service_2_lists = gp['Service name'].unique().values
            service_2_list = set(service_2_lists[0]).intersection(*service_2_lists)
            df = df[df['Service name'].isin(service_2_list)]
        return df

    def _categorize_agency(self, agency):
        if agency in self.filter_params['Agency name']:
            return 'Selected'
        else:
            return 'Profile'

    def generate_dataframe(self, df):
        df = self.filter_dataframe(df)
        df['Group'] = df.apply(lambda x: self._categorize_agency(x['Agency name']), axis=1)
        agg_funcs = {'Primary unit rate': 'sum', 'Primary service volume': 'sum', 'Agency name': 'count'}
        sdf = df.groupby(['Service name', 'Group', 'Financial Year']).agg(agg_funcs)
        ndf = pd.DataFrame(columns=['Financial Year', 'Category', 'Data Type', 'Value'])
        agency_check = df[df['Agency name'].isin(self.filter_params['Agency name'])]
        if len(agency_check):
            for i, row in sdf.iterrows():
                category, group, year = row.name
                ave_unit_cost = row['Primary unit rate'] / row['Agency name']
                if group == 'Selected':
                    agency_volume = row['Primary service volume']
                    ndf.loc[len(ndf) + 1] = [year, category, 'Agency Volume', agency_volume]
                    ndf.loc[len(ndf) + 1] = [year, category, 'Agency Unit Cost', ave_unit_cost]
                else:
                    ndf.loc[len(ndf) + 1] = [year, category, 'WoG Average Unit Cost', ave_unit_cost]
        return ndf

    def generate_graph(self, df, **kwargs):
        # Generate the appropriate graph
        results = {'success': False, 'errors': [], 'image': None}
        if len(df):
            images = self.performance_level2_plot(df, selected_sizes=self.filter_params['Agency size'])
            images['legend'] = self.convert_figure_to_base64(images['legend'])
            images['subplots'] = [self.convert_figure_to_base64(fig) for fig in images['subplots']]
        else:
            results['errors'].append('The selected filter combination did not yield any data points')
        if not results['errors']:
            results['image'] = images
            results['success'] = True
        return results


class AgencyCostCategoryBreakdownMixins(object):

    def category_breakdown_plot(self, df):
        # Initialize figure and axes
        fig, ax = plt.subplots(nrows=1, ncols=1)
        fig.set_size_inches(12,6)

        categories = [x for x in df['Cost category'].unique() if x != '*Volumes*']
        years = sorted(df['Financial Year'].unique())

        df2 = pd.DataFrame(columns=categories)

        for year in years:
            points = []
            for category in categories:
                row = df[(df['Financial Year'] == year) & (df['Cost category'] == category)]
                if not row.empty:
                    points.append(row['Total Cost'].iloc[0])
                else:
                    points.append(0)
            df2.loc[year] = points

        color_map = {x:colors[i] for i,x in enumerate(df2.columns)}
        cumulative_points = []
        for colname in df2.columns:
            points = list(df2[colname])
            if cumulative_points:
                bottom = [sum(i) for i in zip(*cumulative_points)]
                bars = ax.bar(range(len(years)), points, bottom=bottom,
                    label=colname, width=0.35, zorder=2, color=color_map[colname])
            else:
                bars = ax.bar(range(len(years)), points, width=0.35, label=colname,
                    zorder=2, color=color_map[colname])
            for i, bar in enumerate(bars):
                style = 'style="background: white; border: 1px solid black; padding: 2px;"'
                label = '<div {}><strong>{}</strong><br>Total cost: {:,.2f}</div>'
                label = label.format(style, colname, points[i])
                tooltip = mpld3.plugins.LineHTMLTooltip(bar, label=label,
                    hoffset=15, voffset=-5)
                mpld3.plugins.connect(fig, tooltip)
            cumulative_points.append(points)

        df2['Total Cost'] = [df2.loc[year].sum() for year in df2.index.values]

        ax.legend(loc='best')

        ax.set_ylabel('Total Cost', fontsize=14)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.yaxis.grid(color='lightgray', linewidth=2)
        #ax.yaxis.set_major_formatter(FuncFormatter(lambda x,pos: '${:,.0f}'.format(x)))
        ax.tick_params(axis='y', which='major', labelsize=14, labelcolor='#2F2F31', length=0)
        ax.tick_params(axis='x', which='major', length=0)
        ax.set_xticks(range(len(years)))
        ax.set_xticklabels(years)

        axt = ax.twinx()
        axt.patch.set_alpha(0.0)
        #axt.yaxis.set_major_formatter(FuncFormatter(lambda x,pos: '{:,.0f}'.format(x)))
        volumes = df[df['Cost category'] == '*Volumes*']
        axt.plot(volumes['Total Cost'].values, color='gray', linewidth=3)
        axt.set_ylabel('\nVolume', fontsize=14)

        axt.spines['top'].set_visible(False)
        axt.spines['right'].set_visible(False)
        axt.spines['left'].set_visible(False)
        axt.spines['bottom'].set_visible(False)
        axt.tick_params(axis='y', which='major', labelsize=14, labelcolor='#2F2F31', length=0)

        # Fix hbar graph to make it look better
        mpld3.plugins.connect(fig, FixTwinAxes())

        table = df2.T
        for year in years:
            table[year] = table[year].apply('{:.2f}'.format)
        table_json = table.to_dict('split')
        html = mpld3.fig_to_html(fig)
        return html, table_json


class AgencyCostCategoryBreakdown(AgencyCostCategoryBreakdownMixins, ChartBase):

    def filter_dataframe(self, df):
        colmap = {
            'Level 1 Service': 'Service classification',
            'Level 2 Service': 'Service name'
        }
        for k,v in self.filter_params.items():
            excluded = ['Agency name']
            if k not in excluded and len(v):
                mapped_k = colmap.get(k, k)
                if k == 'Agency size':
                    df1 = df[df['Agency name'].isin(self.filter_params['Agency name'])]
                    df2 = df[~df['Agency name'].isin(self.filter_params['Agency name'])]
                    df2 = df2[df2['Agency size'].isin(v)]
                    df = pd.concat([df1, df2])
                else:
                    df = df[df[mapped_k].isin(v)]
        return df

    def generate_dataframe(self, df):
        df = self.filter_dataframe(df)
        cdf = pd.DataFrame()
        if len(df):
            xdf = df.groupby(['Cost category', 'Financial Year']).agg({'Total cost': 'sum', 'Agency name': 'count'})
            ydf = df.groupby(['Financial Year']).agg({'Total cost': 'sum', 'Agency name': 'count'})
            xdf.reset_index(inplace=True)
            ydf.reset_index(inplace=True)
            ydf['Cost category'] = ['*Volumes*'] * len(ydf)
            cdf = pd.concat([xdf, ydf])
            del cdf['Agency name']
            cdf = cdf.rename(columns={'Total cost': 'Total Cost'})
        return cdf

    def generate_graph(self, df, **kwargs):
        # Generate the appropriate graph
        results = {'success': False, 'errors': [], 'image': None}
        if len(df):
            fig, table_json = self.category_breakdown_plot(df)
            b64_string = self.convert_figure_to_base64(fig)
        else:
            results['errors'].append('The selected filter combination did not yield any data points')
        if not results['errors']:
            results['image'] = b64_string
            results['table_json'] = table_json
            results['success'] = True
        return results