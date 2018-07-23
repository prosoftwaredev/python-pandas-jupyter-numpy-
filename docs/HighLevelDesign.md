# High-level design

The system will have three logically distinct facets:

1. skeleton web-application with administration and CSV upload mechanism
2. data-mart management and smart routing between the blue-green data-mart setup
3. charting and visualisation

## Application

### Backend

We will use Python and the Django web framework to build a web application which will provide a means of local authentication,
authorization (user / role management), and facilities to manage the CSV upload and release process.

The MVP will utilise [**matplotlib**](https://matplotlib.org/) (a python 2D plotting library)to produce static, non-interactive visualisations of the data. Processing the data will be done with [**pandas**](http://pandas.pydata.org/) (a data analysis library).

### Frontend

We will utilise HTML5 and CSS as the primary frontend technologies for the web application.

## Data mart

A key component to the system is processing the flat-file CSV into a data structure which better aligns with the kinds of visualisations that need to be generated.  For this reason, this may be one of the final components to be delivered, after the range of visualisations are well understood and the required data structure is clear.

There are several aspects to this:

1. processing new data
2. doing the necessary calculations and building the data mart
3. managing continuity of service for the existing data while this process is underway

