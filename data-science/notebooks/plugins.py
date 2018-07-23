from mpld3 import plugins, utils
import json


class TickLabelLink(plugins.PluginBase):
    """TickLabelLink plugin"""

    JAVASCRIPT = """
    mpld3.register_plugin("ticklabellink", TickLabelLink);
    TickLabelLink.prototype = Object.create(mpld3.Plugin.prototype);
    TickLabelLink.prototype.constructor = TickLabelLink;
    TickLabelLink.prototype.defaultProps = {urls: null, axis: "x"};
    function TickLabelLink(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    var urls;
    var axis;
    var fig_id;
    var buildLabels = function() {
        var svg = "div#" + fig_id + " svg";
        var labels = d3.selectAll(svg + " g.mpld3-" + axis + "axis g.tick text");
        labels.each(function() {
            var label = d3.select(this);
            label.attr('style', label.attr('style') + ' cursor: pointer;');
            label.on('click', function(){
                var url = urls[label.text()];
                location.href = url;
            });
            var bbox = label[0][0].getBBox();
            var parent = d3.select(this.parentNode);
            parent.insert("rect", "text")
                .style("fill", "#FFF")
                .attr("x", bbox.x)
                .attr("y", bbox.y)
                .attr("width", bbox.width)
                .attr("height", bbox.height);
        })
    }

    TickLabelLink.prototype.draw = function(){
        urls = $.parseJSON(this.props['urls']);
        axis = this.props['axis'];
        fig_id = this.fig.figid;
        buildLabels();

        var zoom =  d3.behavior.zoom()
            .on('zoomend', buildLabels);

        var drag =  d3.behavior.drag()
            .on('dragend', buildLabels);

        d3.select("div#" + fig_id + " svg")
            .call(zoom)
            .on("mousedown.zoom", null)
            .on("touchstart.zoom", null)
            .on("touchmove.zoom", null)
            .on("touchend.zoom", null)
            .on("wheel.zoom", null)
            .call(drag);
    }
    """

    def __init__(self, urls_map, axis='x'):
        # Create the xlabel-to-URL mapping
        urls = json.dumps(urls_map)
        # Build the dictionary of properties to be transmitted to the TickLabelLink prototype
        self.dict_ = {
            "type": "ticklabellink",
            "urls": urls,
            "axis": axis,
        }


class PieWedgeLink(plugins.PluginBase):
    """PieWedgeLink plugin"""

    JAVASCRIPT = """
    mpld3.register_plugin("piewedgelink", PieWedgeLink);
    PieWedgeLink.prototype = Object.create(mpld3.Plugin.prototype);
    PieWedgeLink.prototype.constructor = PieWedgeLink;
    PieWedgeLink.prototype.defaultProps = {labels: null, urls: null, subplot: null};
    function PieWedgeLink(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    var urls;
    var fig_id;
    var labels;
    var insertWedgeLinks = function(ax, subplot) {
        var wedges = ax.selectAll('path.mpld3-path');
        wedges.each(function(item, index) {
            var url = urls[labels[index]];
            var wedge = d3.select(this);
            wedge.attr('style', wedge.attr('style') + 'cursor: pointer;');
            wedge.on('mousedown', function(){
                //console.log(labels[index], url);
                //console.log(labels[index]);
                window.open(url);
            });
        })
    }

    PieWedgeLink.prototype.draw = function(){
        urls = $.parseJSON(this.props['urls']);
        labels = $.parseJSON(this.props['labels']);
        fig_id = this.fig.figid;
        var subplot = this.props['subplot'];
        var clip_path = "#" + fig_id + "_ax" + subplot +  "_clip";
        var ax = d3.select($(clip_path).parent()[0])
        insertWedgeLinks(ax, subplot);
        /*
        var zoom =  d3.behavior.zoom()
            .on('zoomend', insertWedgeLinks(ax, subplot);

        var drag =  d3.behavior.drag()
            .on('dragend', insertWedgeLinks(ax, subplot);

        d3.select("div#" + fig_id + " svg")
            .call(zoom)
            .on("mousedown.zoom", null)
            .on("touchstart.zoom", null)
            .on("touchmove.zoom", null)
            .on("touchend.zoom", null)
            .call(drag);
        */
    }
    """

    def __init__(self, labels, urls_map, subplot):
        # Build the dictionary of properties to be transmitted to the TickLabelLink prototype
        self.dict_ = {
            "type": "piewedgelink",
            "labels": json.dumps(labels),
            "urls": json.dumps(urls_map),
            "subplot": subplot
        }


class XTickFormat(plugins.PluginBase):
    """YTickFormat plugin"""

    JAVASCRIPT = """
    mpld3.register_plugin("ytickformat", YTickFormat);
    YTickFormat.prototype = Object.create(mpld3.Plugin.prototype);
    YTickFormat.prototype.constructor = YTickFormat;
    YTickFormat.prototype.defaultProps = {};
    function YTickFormat(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    YTickFormat.prototype.draw = function(){
        var format_func = function(d) {
            if (d >= 1000 && d < 1000000) {
                return d3.format(",")(d/1000) + 'K';
            } else if (d >= 1000000) {
                return d3.format(",")(d/1000000) + 'M';
            } else {
                return d3.format(",")(d);
            }
        };

        var axes = this.fig.axes;
        for (i = 0; i < axes.length; i++) {
            var ax = axes[i].elements[0];
            ax.axis.tickFormat(format_func);
        }

        //ax.axis.tickFormat(format_func);

        // HACK: use reset to redraw figure
        this.fig.reset();
    }
    """

    def __init__(self):
        self.dict_ = {
            "type": "ytickformat"
        }


class YTickFormat(plugins.PluginBase):
    """YTickFormat plugin"""

    JAVASCRIPT = """
    mpld3.register_plugin("ytickformat", YTickFormat);
    YTickFormat.prototype = Object.create(mpld3.Plugin.prototype);
    YTickFormat.prototype.constructor = YTickFormat;
    YTickFormat.prototype.defaultProps = {formatting: null}
    function YTickFormat(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    YTickFormat.prototype.draw = function(){
        // FIXME: this is a very brittle way to select the y-axis element
        var ax = this.fig.axes[0].elements[1];
        var formatting = this.props['formatting'];
        var format_func = d3.format("d");
        if (formatting == 'dollar thousands') {
            format_func = function(d) {
                if (d >= 1000) {
                    return '$' + d3.format(",")(d/1000) + 'K';
                } else {
                    return '$' + d3.format(",")(d);
                }
            };
        }
        ax.axis.tickFormat(format_func);

        // HACK: use reset to redraw figure
        this.fig.reset();
    }
    """

    def __init__(self, formatting):
        self.dict_ = {
            "type": "ytickformat",
            "formatting": formatting
        }


class HideSuplotAxes(plugins.PluginBase):
    """HideSuplotAxes plugin"""

    JAVASCRIPT = """
    mpld3.register_plugin("hidesubplotaxes", HideSuplotAxes);
    HideSuplotAxes.prototype = Object.create(mpld3.Plugin.prototype);
    HideSuplotAxes.prototype.constructor = HideSuplotAxes;
    HideSuplotAxes.prototype.defaultProps = {subplot: null};
    function HideSuplotAxes(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    HideSuplotAxes.prototype.draw = function(){
        var fig_id = this.fig.figid;
        var subplotClipID = fig_id + '_ax' + this.props.subplot + '_clip';
        $('#' + subplotClipID)
            .parent()
            .children('g.mpld3-xaxis, g.mpld3-yaxis')
            .css('display', 'none');
        $('#' + subplotClipID + ' rect').attr('y', 10);
    }
    """

    def __init__(self, subplot):
        self.dict_ = {
            "type": "hidesubplotaxes",
            "subplot": subplot
        }


class FixHBarGraph(plugins.PluginBase):

    JAVASCRIPT = """
    mpld3.register_plugin("fixhbargraph", FixHBarGraph);
    FixHBarGraph.prototype = Object.create(mpld3.Plugin.prototype);
    FixHBarGraph.prototype.constructor = FixHBarGraph;
    FixHBarGraph.prototype.defaultProps = {};
    function FixHBarGraph(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    FixHBarGraph.prototype.draw = function(){
        $('.tick line').hide()
        $('.mpld3-axes line').show()
        $('.domain').hide()
    }
    """

    def __init__(self):
        self.dict_ = {
            "type": "fixhbargraph"
        }


class FixTwinAxes(plugins.PluginBase):

    JAVASCRIPT = """
    mpld3.register_plugin("fixtwinaxes", FixTwinAxes);
    FixTwinAxes.prototype = Object.create(mpld3.Plugin.prototype);
    FixTwinAxes.prototype.constructor = FixTwinAxes;
    FixTwinAxes.prototype.defaultProps = {};
    function FixTwinAxes(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    FixTwinAxes.prototype.draw = function(){
        $('.mpld3-axesbg').remove()
        $('svg').on('mouseover', function(){
            $('.mpld3-toolbar').hide()
        })
    }
    """

    def __init__(self):
        self.dict_ = {
            "type": "fixtwinaxes"
        }