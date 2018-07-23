from django.conf.urls import url

from benchmark.chart import views


urlpatterns = [
    url(
        r'^whole-government/level1/$',
        views.WholeGovernmentLevel1.as_view(),
        kwargs={'level': 'level1'},
        name='chart-whole-government-level1'
    ),
    url(
        r'^whole-government/level2/$',
        views.WholeGovernmentLevel2.as_view(),
        kwargs={'level': 'level2'},
        name='chart-whole-government-level2'
    ),
    url(
        r'^whole-government/level2-benchmark/$',
        views.WholeGovernmentLevel2Benchmark.as_view(),
        kwargs={'level': 'level2-benchmark'},
        name='chart-whole-government-level2-benchmark'
    ),
    url(
        r'^whole-government/level2-trend/$',
        views.WholeGovernment.as_view(),
        kwargs={'level': 'level2-trend'},
        name='chart-whole-government-level2-trend'
    ),

    url(
        r'^my-agency/level1/$',
        views.MyAgencyLevel1.as_view(),
        kwargs={'level': 'level1'},
        name='chart-my-agency-level1'
    ),
    url(
        r'^my-agency/level2/$',
        views.MyAgency.as_view(),
        kwargs={'level': 'level2'},
        name='chart-my-agency-level2'
    ),
    url(
        r'^my-agency/level2-cost-category/$',
        views.MyAgencyCostCategoryBreakdown.as_view(),
        kwargs={'level': 'level2-cost-category'},
        name='chart-my-agency-level2-cost-category'
    ),

    url(
        r'^whole-government/(?P<level>.+)/filters/$',
        views.FiltersPage.as_view(),
        {'chart_type': 'wog'},
        name='chart-whole-government-filters'
    ),

    url(
        r'^my-agency/(?P<level>.+)/filters/$',
        views.FiltersPage.as_view(),
        {'chart_type': 'myagency'},
        name='chart-my-agency-filters'
    ),
]
