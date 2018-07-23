import matplotlib
from matplotlib.ticker import FuncFormatter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.pyplot as plt, mpld3

try:
    from notebooks.styles import colors
    from notebooks.base import ChartBase
    from notebooks.plugins import *
except ImportError:
    from styles import colors
    from base import ChartBase
    from plugins import *

import pandas as pd


plt.switch_backend('agg')


class WOGLevel1Mixins(object):

    def _get_lefts(self, n, ntotal, bar_width, xticks):
        lefts = []
        spacer = 0.05
        if ntotal == 1 and len(xticks) == 1:
            lefts.append(0)
        else:
            for x in range(len(xticks)):
                adjustment = (bar_width + spacer) * n
                left = x - adjustment + ((bar_width + spacer)/2)
                lefts.append(left)
        return lefts

    def service_classification_plot(self, agency_count_df, df, urls_map=None, interactive=True, asl=False):
        self.interactive = interactive
        fig, ax = plt.subplots(nrows=1, ncols=1)
        years = list(df['Financial Year'].unique())
        service_classes = list(df['Service classification'].unique())
        width = 0.25
        bars_list = []
        # Draw the bar graphs
        for i, year in enumerate(years):
            group_df = df[df['Financial Year'] == year]
            group = group_df['Sum of ASL'] if asl else group_df['Sum of Total']
            pos = [service_classes.index(x) for x in group_df['Service classification'].values]
            bar_lefts = self._get_lefts(i, len(years), width, pos)
            bars = ax.bar(bar_lefts, group, color=_set_periods_colors(year), width=width, linewidth=4,
                          edgecolor=_set_periods_colors(year), zorder=2)
            bars_list.append({'values': group, 'bars': bars})

        # Set chart properties and formatting
        fig.set_size_inches(12,6)
        ax.yaxis.set_major_formatter(FuncFormatter(self.format_amount))
        ax.tick_params(axis='y', which='major', labelsize=14, labelcolor='#2F2F31', length=0)
        ax.tick_params(axis='x', which='major', labelsize=14, labelcolor='#2F2F31', length=0)
        xlabels = df['Service classification'].unique()
        ax.set_xticks([p for p in range(len(xlabels))])
        if interactive:
            labels = ax.set_xticklabels(xlabels)
        else:
            rotation = 0
            halign = 'center'
            # Adjust alignment and rotation if there are more than 4 labels
            if len(xlabels) > 4:
                rotation = 45
                halign = 'right'
            labels = ax.set_xticklabels(xlabels, fontweight='semibold', rotation=rotation, position=(0,-0.04))
            for label in labels:
                label.set_horizontalalignment(halign)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.yaxis.grid(color='lightgray', linewidth=2)
        yaxis_label = 'ASL' if asl else 'Dollars'
        ax.set_ylabel(yaxis_label, fontsize=14)

        # Draw the legend
        handles = []
        for i, year in enumerate(years):
            patch = mpatches.Patch(color=_set_periods_colors(year), label=year, linewidth=4)
            handles.append(patch)
        if interactive:
            ax.legend(handles=handles, frameon=False, loc='best')
        else:
            ax.legend(handles=handles, frameon=False, loc='center right', bbox_to_anchor=(1.15, 0.5))

        # Prepare the agency counts table
        agency_count_df.fillna(0, inplace=True)

        # Data table
        df1 = pd.DataFrame([], columns=service_classes)
        def get_value(df, x):
            try:
                if asl:
                    value = df.loc[x]['Sum of ASL']
                else:
                    value = df.loc[x]['Sum of Total']

                return value
            except KeyError:
                return 0
        for i, year in enumerate(years, 1):
            year_df = df[df['Financial Year'] == year]
            year_df.set_index('Service classification', inplace=True)
            df1.loc[year] = [get_value(year_df,x) for x in service_classes]
        if asl:
            for year in years:
                df1.loc[year] = df1.loc[year].apply('{:.2f}'.format)
        else:
            for year in years:
                df1.loc[year] = df1.loc[year].apply('{:.2f}'.format)

        if interactive:
            # Create tooltips for bars
            for bars_group in bars_list:
                for i, bar in enumerate(bars_group['bars'].get_children()):
                    value = list(bars_group['values'])[i]
                    if asl:
                        formatted_value = '{:.2f} ASL'.format(value)
                    else:
                        formatted_value = '${:,.0f}'.format(value)
                    label = "<div style='background: white; padding: 2px; border: solid 1px black;'>%s</div>" % formatted_value
                    tooltip = mpld3.plugins.LineHTMLTooltip(bar, label=label, hoffset=15, voffset=-5)
                    mpld3.plugins.connect(fig, tooltip)
            # Create links in x-axis labels
            mpld3.plugins.connect(fig, TickLabelLink(urls_map))
            # Format the y-axis values

            mpld3.plugins.connect(fig, YTickFormat('dollar thousands'))
            # Create the agency counts table
            html = mpld3.fig_to_html(fig)
            agency_count_table_json = agency_count_df.to_dict('split')
            table_json = df1.to_dict('split')
            return html, agency_count_table_json, table_json
        else:
            ax.table(
                cellText=agency_count_df.as_matrix(),
                rowLabels=agency_count_df.index,
                colLabels=agency_count_df.columns,
                bbox=[0, 1.1, 0.5, 0.7],
                loc='top'
            )
            fig.tight_layout()
            return fig


class WOGLevel1(ChartBase, WOGLevel1Mixins):
    excluded_service_type_list = ['Other Corporate Services', 'Other Financial Services', 'Other HR Services']

    def filter_dataframe(self, df):
        colmap = {'Level 1 Service': 'Service classification'}
        for k,v in self.filter_params.items():
            excluded = ['Agency name', 'Level 2 Service', 'ASL']
            if k not in excluded and len(v):
                mapped_k = colmap.get(k, k)
                df = df[df[mapped_k].isin(v)]
        df = df[~df['Service name'].isin(self.excluded_service_type_list)]
        return df

    def get_agency_counts(self, df):
        sdf = self.filter_dataframe(df)
        def agency_count(series):
            return len(series.unique())
        if self.filter_params['Agency name']:
            sdf = sdf.loc[sdf['Agency name'].isin(self.filter_params['Agency name'])]

        sdf = sdf.groupby(['Agency size', 'Financial Year']).agg({'Agency name': agency_count})
        sizes, years = sdf.index.levels
        pdf = pd.DataFrame(columns=list(years))
        for size in sizes:
            row = []
            for year in years:
                try:
                    value = int(sdf.loc[size, year])
                except KeyError:
                    value = 0
                row.append(value)
            pdf.loc[size] = row
        pdf = pdf.reindex(['Extra Large agencies', 'Large agencies', 'Medium agencies', 'Small agencies', 'Extra Small agencies', 'Micro'])
        pdf = pdf.rename(index={pdf.index[5]: 'Micro agencies'})
        pdf.loc['Total agencies'] = [pdf[year].sum() for year in pdf.columns]
        return pdf

    def generate_dataframe(self, df):
        df = self.filter_dataframe(df)
        if len(df):
            # Generate the agency counts dataframe
            sdf = self.get_agency_counts(df)
            # Proceed to generate the dataframe needed by main chart
            if self.filter_params['Agency name']:
                df = df[df['Agency name'].isin(self.filter_params['Agency name'])]
            del df['Agency name']

            df = df.groupby(['Financial Year', 'Service classification']).aggregate({'Sum of Total': 'sum', 'Sum of ASL': 'sum'})
            df.reset_index(inplace=True)
        return (sdf, df)

    def generate_graph(self, dfs, interactive=True, base_url=None, **kwargs):
        agency_count_df, df = dfs
        # Generate the appropriate graph
        results = {'success': False, 'errors': [], 'image': None}
        if len(df):
            # if not base_url:
            #     base_url = 'https://www-integration.benchmarking.fin.gosource.com.au'
            # url = base_url.rstrip('/') + '/chart/whole-government/level2/'
            url = '/chart/whole-government/level2/'
            urls_map = self.create_url_mapping(
                df['Service classification'].unique(),
                self.filter_params,
                'service_level1',
                url)
            asl = 'ASL' in self.filter_params and self.filter_params['ASL'] or False
            fig, agency_count_table_json, table_json = self.service_classification_plot(agency_count_df, df, urls_map=urls_map, interactive=interactive, asl=asl)
            b64_string = self.convert_figure_to_base64(fig)
        else:
            results['errors'].append('The selected filter combination did not yield any data points')
        if not results['errors']:
            results['image'] = b64_string
            results['agency_count_table_json'] = agency_count_table_json
            results['table_json'] = table_json
            results['success'] = True
        return results


class WOGLevel2Mixins(object):

    def _get_lefts(self, n, ntotal, bar_width, xticks):
        lefts = []
        spacer = 0.05
        for x in range(len(xticks)):
            adjustment = (bar_width + spacer) * n
            left = x - adjustment + ((bar_width + spacer)/2)
            lefts.append(left)
        return lefts

    def service_type_plot(self, df, urls_map=None, interactive=True, asl=False):
        fig, ax = plt.subplots(nrows=1, ncols=1)
        years = list(df['Financial Year'].unique())
        service_types = list(df['Service type'].unique())
        width = 0.25
        bars_list = []
        # Draw the bar graphs
        for i, year in enumerate(years):
            group_df = df[df['Financial Year'] == year]
            group = group_df['Sum of ASL'] if asl else group_df['Sum of Total']
            pos = [service_types.index(x) for x in group_df['Service type'].values]
            bar_lefts = self._get_lefts(i, len(years), width, pos)
            bars = ax.bar(bar_lefts, group, color=_set_periods_colors(year), width=width, linewidth=4,
                          edgecolor=_set_periods_colors(year), zorder=2)
            bars_list.append({'bars': bars, 'values': group})

        # Set chart properties and formatting
        fig.set_size_inches(12,6)
        ax.yaxis.set_major_formatter(FuncFormatter(self.format_amount))
        ax.tick_params(axis='y', which='major', labelsize=14, labelcolor='#2F2F31', length=0)

        if interactive:
            ax.tick_params(axis='x', which='major', labelsize=14, length=0)
            xlabels = [x.title() for x in service_types]
            ax.set_xticks(range(len(xlabels)))
            ax.set_xticklabels(xlabels)
        else:
            ax.tick_params(axis='x', which='major', labelsize=9.5, length=0)
            xlabels = [x.replace(' ', '\n') for x in service_types]
            ax.set_xticklabels([], position=(0,-0.04), clip_on=True)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.yaxis.grid(color='lightgray', linewidth=2)
        yaxis_label = 'ASL' if asl else 'Dollars'
        ax.set_ylabel(yaxis_label, fontsize=14)

        # Draw the legend
        handles = []
        for i, year in enumerate(years):
            patch = mpatches.Patch(color=_set_periods_colors(year), label=year, linewidth=4)
            handles.append(patch)
        if interactive:
            ax.legend(handles=handles, loc='best')
        else:
            ax.legend(handles=handles, frameon=False, loc='center right', bbox_to_anchor=(1.15, 0.5))

        # Data table
        df2 = pd.DataFrame([], columns=service_types)
        def get_value(df, x):
            try:
                if asl:
                    value = df.loc[x]['Sum of ASL']
                else:
                    value = df.loc[x]['Sum of Total']

                return value
            except KeyError:
                return 0
        for i, year in enumerate(years, 1):
            year_df = df[df['Financial Year'] == year]
            year_df.set_index('Service type', inplace=True)
            df2.loc[year] = [get_value(year_df,x) for x in service_types]
        df2['Total Cost'] = [df2.loc[year].sum() for year in df2.index.values]
        if asl:
            for year in years:
                df2.loc[year] = df2.loc[year].apply('{:.2f}'.format)
        else:
            for year in years:
                df2.loc[year] = df2.loc[year].apply('{:.2f}'.format)

        if interactive:
            # Create tooltips for bars
            for bars_group in bars_list:
                for i, bar in enumerate(bars_group['bars'].get_children()):
                    value = list(bars_group['values'])[i]
                    if asl:
                        formatted_value = '{:.2f} ASL'.format(value)
                    else:
                        formatted_value = '${:,.0f}'.format(value)
                    label = "<div style='background: white; padding: 2px; border: solid 1px black;'>%s</div>" % formatted_value
                    tooltip = mpld3.plugins.LineHTMLTooltip(bar, label=label, hoffset=15, voffset=-5)
                    mpld3.plugins.connect(fig, tooltip)
            # Create links in x-axis labels
            mpld3.plugins.connect(fig, TickLabelLink(urls_map))
            # Format the y-axis values
            mpld3.plugins.connect(fig, YTickFormat('dollar thousands'))
            # Create the agency counts table
            html = mpld3.fig_to_html(fig)
            table_json = df2.to_dict('split')
            return html, table_json
        else:
            data_table = ax.table(cellText=df2.as_matrix(), colLabels=xlabels, rowLabels=years, loc='bottom')
            data_table.auto_set_font_size(False)
            data_table.set_fontsize(9.5)

            # Adjust cell heights
            data_table.scale(1,2)
            cells = data_table.get_celld()
            for x,y in cells:
                cell = cells[(x,y)]
                if x == 0:
                    cell.set_height(0.2)
                cell.set_linewidth(0.5)
                cell.set_linestyle('dashed')

            fig.tight_layout()
            return fig


class WOGLevel2(ChartBase, WOGLevel2Mixins):
    service_2_list = []
    excluded_service_type_list = ['Other Corporate Services', 'Other Financial Services', 'Other HR Services']

    def filter_dataframe(self, df):
        colmap = {
            'Level 1 Service': 'Service classification',
            'Level 2 Service': 'Service type'
        }
        for k,v in self.filter_params.items():
            excluded = ['Agency name', 'ASL']
            if k not in excluded and len(v):
                mapped_k = colmap.get(k, k)
                df = df[df[mapped_k].isin(v)]
        if len(self.filter_params['Level 2 Service']) == 0:
            gp = df[['Service type', 'Financial Year']].groupby('Financial Year')
            service_2_lists = gp['Service type'].unique().values
            if len(service_2_lists) != 0:
                self.service_2_list = set(service_2_lists[0]).intersection(*service_2_lists)
            else:
                self.service_2_list = []
            df = df[df['Service type'].isin(self.service_2_list)]
        df = df[~df['Service type'].isin(self.excluded_service_type_list)]
        return df

    def generate_dataframe(self, df):
        df = self.filter_dataframe(df)
        if len(df):
            if self.filter_params['Agency name']:
                df = df[df['Agency name'].isin(self.filter_params['Agency name'])]
            del df['Agency name']
            # Pre-process the dataframe
            df = df.groupby(['Financial Year', 'Service type']).aggregate({'Sum of Total': 'sum', 'Sum of ASL': 'sum'})
            df.reset_index(inplace=True)
        return df

    def generate_graph(self, df, interactive=True, base_url=None, **kwargs):
        # Generate the appropriate graph
        results = {'success': False, 'errors': [], 'image': None}
        if len(df):
            url = '/chart/whole-government/level2-benchmark/'
            urls_map = self.create_url_mapping(
                df['Service type'].unique(),
                self.filter_params,
                'service_level2',
                url)
            asl = 'ASL' in self.filter_params and self.filter_params['ASL'] or False
            fig, table_json = self.service_type_plot(df, urls_map=urls_map, interactive=interactive, asl=asl)
            b64_string = self.convert_figure_to_base64(fig)
        else:
            results['errors'].append('The selected filter combination did not yield any data points')
        if not results['errors']:
            results['image'] = b64_string
            results['table_json'] = table_json
            results['success'] = True
            results['service_2_list'] = self.service_2_list
        return results


class WOGLevel2BenchmarkMixins(object):

    def service_profile_plot(self, service_name, df1, df2, deidentified=False, browser='edge', asl=False, selected_agency_name=''):
        # Initialize list that should contain the subplots
        subplots = []
        #---------------------------------------------------
        # Initialize the figure and axes for the scatterplot
        #---------------------------------------------------
        fig = plt.figure(figsize=(7,5))
        gs = gridspec.GridSpec(2, 1, height_ratios=[6,1.5])

        unit_type = df1.columns[1]
        ax1 = fig.add_subplot(gs[0, 0])
        profiles = df1[df1['Type'] == 'WofG Agencies']
        dot_size = 100
        if browser == 'edge':
            dot_size = 30
        scatter1 = ax1.scatter(profiles[unit_type],
            profiles['Unit Rates'], c=colors[0], s=dot_size, zorder=2)
        selected_orgs = df1[df1['Type'] == selected_agency_name]
        scatter2 = None
        if len(selected_orgs):
            scatter2 = ax1.scatter(selected_orgs[unit_type],
                selected_orgs['Unit Rates'], c="#ec4a41", s=dot_size, zorder=2)

        ax1.set_ylabel('Unit Rates', fontsize=12)
        ax1.set_xlabel(unit_type, fontsize=12)

        # Grid and labels formatting
        ax1.yaxis.grid(color='lightgray', linewidth=2, zorder=1)
        ax1.xaxis.grid(color='lightgray', linewidth=2, zorder=1)
        ax1.set_title(service_name, position=(0.5,1.12), fontsize=18)
        ax1.text(0.5, 1.1, '(Unit Type = %s)' % unit_type,
            transform=ax1.transAxes, ha='center', va='center', fontsize=14)

        for axis in ['top','bottom','left','right']:
            ax1.spines[axis].set_linewidth(3)

        # Draw the tooltip for each point
        def format_label(agency, unit_type, x,y):
            style = 'style="background: white; border: 1px solid black; padding: 5px;"'
            if agency:
                label = '<div {}><strong>{}</strong><br>'.format(style, agency)
            else:
                label = '<div {}>'.format(style)
            label += '{}: {:,.0f}<br>Unit Rate: {:,.2f}</div>'.format(unit_type, x,y)
            return label
        for sdf, points in [(profiles, scatter1), (selected_orgs, scatter2)]:
            if points:
                labels = zip(sdf['Agency name'], sdf[unit_type], sdf['Unit Rates'])
                labels = [format_label(agency, unit_type, x,y) for agency,x,y in labels]
                tooltip = mpld3.plugins.PointHTMLTooltip(points,  labels=labels,
                    hoffset=15, voffset=-5)

                mpld3.plugins.connect(fig, tooltip)

        # Draw and format the legend
        ax2 = fig.add_subplot(gs[1, 0])
        handles = []
        for label, color in [('WofG Agencies', colors[0]), (selected_agency_name, '#ec4a41')]:
            circle = mlines.Line2D(
                range(1),
                range(1),
                marker='o',
                color='white',
                markerfacecolor=color,
                markeredgecolor=color,
                markersize=9,
                label=label)
            handles.append(circle)
        legend = ax2.legend(handles=handles, ncol=2, loc='lower center')
        frame = legend.get_frame()
        frame.set_facecolor('white')
        frame.set_linewidth(2)
        frame.set_edgecolor('black')
        mpld3.plugins.connect(fig, HideSuplotAxes(2))

        html = mpld3.fig_to_html(fig)
        # We can eventually remove the code above
        # but for now, we'll just stop providing it to the template.
        # This is deprecated by a template-driven JS charting library.
        # subplots.append(html)

        #---------------------------------------------------------
        # Initialize the figure and axes for the stacked bar graph
        #---------------------------------------------------------
        fig = plt.figure(figsize=(7,5))
        gs = gridspec.GridSpec(2, 1, height_ratios=[6,1.5])
        ax1 = fig.add_subplot(gs[0, 0])

        # Create a color mapping in tuples
        cost_types = list(df2['Cost Type'].dropna().values)
        cost_types.sort()
        cost_type_colors = zip(cost_types, colors[0:len(df2)])
        colors_dict = dict(cost_type_colors)

        df2['Order'] = df2['Cost Type'].dropna().apply(lambda x: cost_types.index(x))
        df2['Color'] = df2['Cost Type'].dropna().apply(lambda x: colors_dict[x])
        df2 = df2.dropna(subset=['Cost Type']).sort_values('Order', ascending=False)

        def create_stacked_bar(pos, values, colors, cost_types):
            width = 0.5
            lastx = 0
            bars_list = []
            for x,color,cost_type in list(zip(values, colors, cost_types)):
                bar = ax1.bar(pos, x, width, bottom=lastx, color=color)
                lastx += x
                bars_list.append({'bar': bar, 'value': x, 'name': cost_type})
            return bars_list
        bar_groups = {
            1: {'name': service_name},
            2: {'name': 'WofG Agencies - %s' % service_name}
        }
        df2.sort_values('Cost Type', inplace=True)
        for bg in bar_groups:
            bars = create_stacked_bar(bg, df2[bar_groups[bg]['name']], df2['Color'], df2['Cost Type'])
            #if interactive:
            for bar in bars:
                style = 'style="background: white; border: 1px solid black; padding: 2px;"'
                label = '<div {}><strong>{}</strong><br>Percentage: {:,.2f}%</div>'
                label = label.format(style, bar['name'], bar['value'])
                tooltip = mpld3.plugins.LineHTMLTooltip(
                    bar['bar'].get_children()[0], label=label,
                    hoffset=15, voffset=-5)
                mpld3.plugins.connect(fig, tooltip)
        ax1.set_title('Compare Your Cost Categories', position=(0.5,1.05), fontsize=18)
        percentage_by = 'ASL' if asl else 'Dollars'
        ax1.set_ylabel('Percentage - {}'.format(percentage_by), fontsize=12)

        def draw_subplot2_legend(ax):
            # Draw the legend
            handles = []
            for cost_type, color in colors_dict.items():
                if cost_type != 'Unknown':
                    patch = mpatches.Patch(color=color, label=cost_type)
                    handles.append(patch)
            legend = ax.legend(handles=handles, loc='lower center', ncol=3)
            frame = legend.get_frame()
            frame.set_linewidth(2)
            frame.set_facecolor('#f0f3ee')
            frame.set_edgecolor('#dbe0d5')
            return legend

        ax1.xaxis.set_label_coords(0.5, -0.1)
        ax1.yaxis.set_label_coords(-0.1, 0.5)
        ax1.set_xlim(0,3)
        ax1.set_xticks([1, 2])
        ax1.set_xticklabels([service_name, 'WofG Agencies - %s' % service_name])

        ax2 = fig.add_subplot(gs[1, 0])
        draw_subplot2_legend(ax2)
        mpld3.plugins.connect(fig, HideSuplotAxes(2))

        html = mpld3.fig_to_html(fig)
        subplots.append(html)

        return {'subplots': subplots, 'data': {'profiles': profiles.to_dict(), 'agency': selected_orgs.to_dict()}}

class WOGLevel2Benchmark(ChartBase, WOGLevel2BenchmarkMixins):

    selected_agency_name = ''
    excluded_service_type_list = ['Other Corporate Services', 'Other Financial Services', 'Other HR Services']

    def filter_dataframe(self, df):
        colmap = {'Level 1 Service': 'Service classification'}
        for k,v in self.filter_params.items():
            excluded = ['Agency size', 'Agency name', 'Level 2 Service', 'ASL']
            if k not in excluded and len(v):
                mapped_k = colmap.get(k, k)
                df = df[df[mapped_k].isin(v)]
        df = df[~df['Service name'].isin(self.excluded_service_type_list)]
        return df

    def generate_dataframe(self, df):
        df = self.filter_dataframe(df)
        fin_years = self.filter_params['Financial Year']
        agencies = self.filter_params['Agency name']
        level2_params = self.filter_params['Level 2 Service']
        unit_type = level2_params.get('Primary unit of measure', '')
        service_name = level2_params['Service name']
        asl = self.filter_params['ASL']

        if self.filter_params['Agency size']:
            # Select the selected agency (or agencies) and those of the same size(s) as the
            # selected sizes
            org_sizes = self.filter_params['Agency size']
            xdf1 = df[df['Agency name'].isin(agencies)]
            xdf2 = df[df['Agency size'].isin(org_sizes)]
            df = pd.concat([xdf1, xdf2])
        else:
            # Select the set agency (or agencies) and those of their size(s)
            org_sizes = df[df['Agency name'].isin(self.filter_params['Agency name'])]['Agency size'].unique()
            df = df[df['Agency size'].isin(list(org_sizes))]
        # Start with empty dataframes by default
        sdf1 = pd.DataFrame()
        sdf2 = pd.DataFrame()
        if len(df):
            if not unit_type:
                unit_type = self.get_unit_type_options(df)[service_name][0]
            # Build the dataframes
            sdf1 = df[(df['Service name'] == service_name) & (df['Primary unit of measure'] == unit_type)]
            #check_df = sdf1[sdf1['Agency name'].isin(agencies)]
            #if len(sdf1) and len(check_df):
            if len(sdf1):
                sdf1 = sdf1.groupby('Agency name').agg({'Primary service volume': 'mean', 'Primary unit rate': 'mean'})
                sdf1.reset_index(inplace=True)

                self.selected_agency_name = agencies[0] if agencies else ''

                def categorize_agency(row):
                    if row['Agency name'] in agencies:
                        return self.selected_agency_name
                    else:
                        return 'WofG Agencies'

                sdf1['Type'] = sdf1.apply(lambda x: categorize_agency(x), axis=1)
                #del sdf1['Agency name']
                sdf1 = sdf1.rename(columns={'Primary unit rate': 'Unit Rates', 'Primary service volume': unit_type})

                # Only include these pre-determined cost categories
                cost_categories = df['Cost category'].unique()
                sdf2 = pd.DataFrame([], columns=['WofG Agencies - %s' % service_name, service_name, 'Cost Type'])
                sdf2['Cost Type'] = cost_categories

                def get_cost_type_sum(cost_type, profile=False):
                    if profile:
                        ddf = df[~df['Agency name'].isin(agencies) & (df['Cost category'] == cost_type) & (df['Service name'] == service_name)]
                    else:
                        ddf = df[df['Agency name'].isin(agencies) & (df['Cost category'] == cost_type) & (df['Service name'] == service_name)]
                    ddf = ddf[ddf['Primary unit of measure'] == unit_type]
                    cost_type_sum = ddf['Total ASL'].sum() if asl else ddf['Total cost'].sum()
                    return round(cost_type_sum, 2)

                for colname in ['WofG Agencies - %s' % service_name, service_name]:
                    profile = False
                    if 'WofG Agencies -' in colname:
                        profile = True
                    sdf2[colname] = sdf2.apply(lambda x: get_cost_type_sum(x['Cost Type'], profile=profile), axis=1)
                    # Compute the percentage
                    sdf2[colname] = (sdf2[colname]/sdf2[colname].sum()) * 100
                    sdf2[colname] = sdf2[colname].fillna(0)
        return (sdf1, sdf2, df)

    def deidentify(self, name):
        if name not in self.filter_params['Agency name']:
            name = ''
        return name

    def generate_graph(self, dfs, deidentified=False, browser=None, **kwargs):
        # Get the dataframes
        df1, df2, test_df = dfs
        asl = self.filter_params['ASL']
        # Generate the appropriate graph
        results = {'success': False, 'errors': [], 'image': {None}}
        if self.filter_params['Agency name']:
            service_name = self.filter_params['Level 2 Service']['Service name']
            if service_name:
                if len(df1) > 0 and len(df2) > 0:
                    if deidentified:
                        df1['Agency name'] = df1['Agency name'].apply(self.deidentify)
                    fig = self.service_profile_plot(
                        service_name, df1, df2,
                        deidentified=deidentified,
                        browser=browser,
                        asl=asl,
                        selected_agency_name=self.selected_agency_name,
                    )
                    subplots = [self.convert_figure_to_base64(html) for html in fig['subplots']]
                    data = fig['data']
                else:
                    results['errors'].append('The selected filter combination did not yield any data points')
            else:
                results['errors'].append('A specific service name is required')
        else:
            results['errors'].append('This graph type needs at least one agency to be selected')
        if not results['errors']:
            results['image'] = {'subplots': subplots}
            results['data'] = data
            del df2['Order']
            results['table_json'] = df2.set_index('Cost Type').to_dict('split')

            # Some hackish code to mash data into chartjs data
            def chartjs_dataset(data):
                ignore_keys = ['Agency name', 'Unit rates']
                key_x = next(iter([k for k in data['profiles'] if k not in ignore_keys]))
                key_y = 'Unit Rates'

                def build_dataset(dataset):
                    if len(dataset['Agency name'].keys()) == 0:
                        return []
                    data_list = {
                        'type': list(dataset['Type'].values())[0],
                        'plots': []
                    }

                    for k, v in dataset['Agency name'].items():
                        new_plot = {
                            'agency_name': v if v else 'WofG Agencies',
                            'coord': {
                                'x': dataset[key_x][k],
                                'y': dataset[key_y][k]
                            }
                        }

                        if new_plot['coord']['x'] > 1 and new_plot['coord']['y'] > 1:
                            for axis in ['x', 'y']:
                                pass
                                new_plot['coord'][axis] = round(new_plot['coord'][axis], 2)

                        data_list['plots'] += [new_plot]
                    return data_list

                profile_dataset = build_dataset(data['profiles'])
                selected_dataset = build_dataset(data['agency'])

                return (
                    key_x,
                    key_y,
                    [selected_dataset, profile_dataset]
                )

            x_label, y_label, plot_groups = chartjs_dataset(data)

            results['chartjs'] = {
                'x_label': x_label,
                'y_label': y_label,
                'plot_groups': plot_groups
            }

            results['success'] = True

        return results


class WOGLevel2TrendMixins(object):

    def trend_plot(self, service_name, unit_type, df):
        # Initialize figure and axes
        fig, ax = plt.subplots(nrows=1, ncols=1)
        ax.plot(df['WoG Average'], c='#2F2F31', zorder=2, marker=".", markersize=15, linewidth=3)
        ax.plot(df['Selected Agency'], c='#9ACBCB', zorder=2, marker=".", markersize=15, linewidth=3)
        ax.yaxis.set_major_formatter(FuncFormatter(self.format_amount))
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df['Financial Year'].values)
        ax.yaxis.grid(color='lightgray', linewidth=2)
        ax.tick_params(axis='y', which='major', labelsize=14, labelcolor='#2F2F31', length=0)
        ax.tick_params(axis='x', which='major', labelsize=14, labelcolor='#2F2F31', length=0)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.yaxis.grid(color='lightgray', linewidth=1)
        # fig.set_size_inches(8,5)
        ax.set_title(service_name, position=(0.5,1.11), fontsize=18)
        ax.text(0.5, 1.08, '(Unit Type = %s)' % unit_type, transform=ax.transAxes,
            ha='center', va='center', fontsize=14)

        ax.set_ylabel('Dollars')

        # Draw and format the legend
        handles, labels = ax.get_legend_handles_labels()
        legend = ax.legend(handles, ['WoG Average', 'Selected Agency'],
            ncol=1, bbox_to_anchor=(1.35, 0.5), loc='right', borderpad=1)
        frame = legend.get_frame()
        frame.set_linewidth(0)
        return fig


class WOGLevel2Trend(ChartBase, WOGLevel2TrendMixins):
    excluded_service_type_list = ['Other Corporate Services', 'Other Financial Services', 'Other HR Services']

    def filter_dataframe(self, df):
        colmap = {'Level 1 Service': 'Service classification'}
        for k,v in self.filter_params.items():
            excluded = ['Agency size', 'Agency name', 'Level 2 Service']
            if k not in excluded and len(v):
                mapped_k = colmap.get(k, k)
                df = df[df[mapped_k].isin(v)]
        df = df[~df['Service name'].isin(self.excluded_service_type_list)]
        return df

    def generate_dataframe(self, df):
        df = self.filter_dataframe(df)
        level2_params = self.filter_params['Level 2 Service']
        unit_type = level2_params['Primary unit of measure']
        fin_years = self.filter_params['Financial Year']
        service_name = self.filter_params['Level 2 Service']['Service name']
        agencies = self.filter_params['Agency name']
        # Build the dataframes
        df = df[(df['Service name'] == service_name) & (df['Primary unit of measure'] == unit_type)]
        sdf = pd.DataFrame()
        df2 = pd.DataFrame(columns=['Financial Year', 'WoG Average', 'Selected Agency'])
        if self.filter_params['Agency size']:
            # Select the selected agency (or agencies) and those of the same size(s) as the
            # selected sizes
            org_sizes = self.filter_params['Agency size']
            xdf1 = df[df['Agency name'].isin(agencies)]
            xdf2 = df[df['Agency size'].isin(org_sizes)]
            df = pd.concat([xdf1, xdf2])
        else:
            # Select the set agency (or agencies) and those of their size(s)
            org_sizes = df[df['Agency name'].isin(self.filter_params['Agency name'])]['Agency size'].unique()
            df = df[df['Agency size'].isin(list(org_sizes))]
        if len(df):
            agg_funcs = {'Total cost': 'sum', 'Primary unit rate': 'mean'}
            groups = df.groupby(['Agency name', 'Financial Year'])
            sdf = groups.agg(agg_funcs)
            sdf.reset_index(inplace=True)

            def categorize_agency(row):
                if row['Agency name'] in agencies:
                    return 'Selected Organization'
                else:
                    return 'Profile'

            sdf = sdf.rename(columns={'Primary unit rate': 'Unit Rates', 'Total cost': unit_type})
            sdf['Type'] = sdf.apply(lambda x: categorize_agency(x), axis=1)
            groups = sdf.groupby(['Type', 'Financial Year'])
            sdf = groups.agg({'Unit Rates': 'sum'})
            sdf['Count'] = groups.count()['Agency name']
            sdf['Average'] = sdf.apply(lambda x: x['Unit Rates']/x['Count'], axis=1)
            del sdf['Count']
            del sdf['Unit Rates']
            sdf.reset_index(inplace=True)

            df2 = pd.DataFrame(columns=['Financial Year', 'WoG Average', 'Selected Agency'])
            years = sdf['Financial Year'].unique()
            for i, year in enumerate(years):
                wog_ave = sdf[(sdf['Financial Year'] == year) & (sdf['Type'] == 'Profile')]
                if len(wog_ave):
                    wog_ave = wog_ave.iloc[0].Average
                else:
                    wog_ave = None
                agency_ave = sdf[(sdf['Financial Year'] == year) & (sdf['Type'] == 'Selected Organization')]
                if len(agency_ave):
                    agency_ave = agency_ave.iloc[0].Average
                else:
                    agency_ave = None
                df2.loc[i] = [year, wog_ave, agency_ave]
        return df2

    def generate_graph(self, df, **kwargs):
        # Generate the appropriate graph
        results = {'success': False, 'errors': [], 'image': None}
        if len(df):
            service_name = self.filter_params['Level 2 Service']['Service name']
            unit_type = self.filter_params['Level 2 Service']['Primary unit of measure']
            fig = self.trend_plot(service_name, unit_type, df)
            b64_string = f'<div>{self.convert_figure_to_base64(fig)}</div>'
        else:
            results['errors'].append('The selected filter combination did not yield any data points')
        if not results['errors']:
            results['image'] = b64_string
            results['success'] = True
        return results


def _set_periods_colors(year):
    periods_colors = {'2014-15': '#9ACBCB',
                      '2015-16': '#2F2F31',
                      '2016-17': '#B8A7D6',
                      '2017-18': '#FFF39D',
                      '2018-19': '#3296FF'
                      }
    try:
        return periods_colors.get(year)
    except KeyError:
        print('The colour for chosen period is not set')
