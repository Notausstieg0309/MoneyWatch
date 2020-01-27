var sel_dates = {}
var analysis_chart = null;



function generateAnalysisChartLabel(item, res)
{
    switch(res.interval)
    {
        case "1":
            return res.month_names[item.month - 1] + " " + item.year;        
        case "3":
            return item.quarter_formatted;
        case "12":
            return item.year;
    }
}

function generateAnalysisChartData(res)
{
    var labels = []
    var data = []
    var links = [];
    
    
    $.each(res.data, function(index, item) 
    {
        var label = generateAnalysisChartLabel(item, res);
        
        labels.push(label);
        data.push(item.valuta);
            
    });
    
    return {labels: labels, data: data};
}


function createAnalysisChart(res) 
{   
        var canvas = $("canvas#analysis_chart")[0]
        var ctx = canvas.getContext('2d');

        var items = generateAnalysisChartData(res);

        if( analysis_chart != null) 
        {
            analysis_chart.destroy();
        }
        

        analysis_chart = new Chart(ctx, {
/*
			plugins: [{
				        beforeRender: function (c, options) {
										var dataset = c.data.datasets[0];
									    var yScale = c.scales['y-axis-0'];
										var yPos = yScale.getPixelForValue(0);

									    var gradientFill = c.ctx.createLinearGradient(0, 0, 0, c.height);
									    gradientFill.addColorStop(0, 'green');
									    gradientFill.addColorStop(yPos / c.height - 0.01, 'green');
									    gradientFill.addColorStop(yPos / c.height + 0.01, 'red');
									    gradientFill.addColorStop(1, 'red');

					                    var model = c.data.datasets[0]._meta[Object.keys(dataset._meta)[0]].$filler.el._model;
									    model.backgroundColor = gradientFill;
																																				        }
				    }],
*/
			type: 'line',
            data: {
                labels: items.labels,
                datasets: [
                            { 
                                label: res.description,
                                data: items.data,
                                //links: items.links,
                                //pointBackgroundColor: items.pointBackgroundColors,
                                //backgroundColor: backgroundColor,
                                pointRadius: 5,
                                pointHoverRadius: 10,
								cubicInterpolationMode: 'monotone',
                            }
                          ]
            },
            options: {
                scales : {
                    yAxes : [{
                        ticks : {
                            beginAtZero : true,
                            callback: function(value, index, values) {
                                        return value + ' €';
                                      },
                            //fontColor: (res.type == "in" ? "#006d14" : "#ff0000")
                        }   
                    }],
                    xAxes: [{ 
                        ticks: {
                          fontColor: "#000",
                        },
                    }],
                },
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem, chart){
                          
                            return new Intl.NumberFormat(getLang(), { style: 'currency', currency: 'EUR' } ).format(tooltipItem.yLabel);
                        }
                    },
                    displayColors: false
                },
                legend: {
                    display: false
                },
                hover: {
                    onHover: function(e) {
                        var point = this.getElementAtEvent(e);
                        if (point.length) e.target.style.cursor = 'pointer';
                        else e.target.style.cursor = 'default';
                    }
                },
				color: function(context) {
				    var index = context.dataIndex;
					    var value = context.dataset.data[index];
						    return value < 0 ? 'red' :  // draw negative values in red
							        index % 2 ? 'blue' :    // else, alternate values in blue and green
									        'green';
				}
            }
        });
}

$(function () {

    $('ul.criteria-container input.datepicker').each(function () {
        var date_options = {
            firstDay: 1,
            autoClose: true,
            yearRange: [ $(this).data("years-start"), $(this).data("years-end")],
            onSelect: function(date) { sel_dates[$(this.el).attr("id")] = dateToString(date) },
        };

        if($(this).data("min-date")) {
            date_options["minDate"] =  new Date($(this).data("min-date"))
        }
        
         if($(this).data("format")) {
            date_options["format"] = $(this).data("format");
        }

        if($(this).data("max-date")) {
            date_options["maxDate"] =  new Date($(this).data("max-date"))
        }
        
        console.log(date_options);
        
        var instances = M.Datepicker.init(this, date_options);
    });

    $('ul.criteria-container input:radio[name="type"]').change(function(){

        var el = $(this);
        
        if(el.is(':checked')){
            if(el.is('#balance')) {
            
                $("ul.criteria-container > li#subtype").fadeOut();
                $("ul.criteria-container > li#rule").fadeOut();
                $("ul.criteria-container > li#category").fadeOut();
            }
            else if(el.is('#in') || el.is('#out')) {
            
                $("ul.criteria-container > li#subtype").fadeIn();
                $("ul.criteria-container > li.rules").fadeOut();
                $("ul.criteria-container > li.categories").fadeOut();
            }
        }

    });

    $('ul.criteria-container input:radio[name="subtype"]').change(function(){
        var el = $(this);
       
        if(el.is(':checked')){
            
            var type_val = $('ul.criteria-container input:radio[name="type"]:checked').attr("id");
            var opposite_val = (type_val == "in" ? "out" : "in");
            
            if(el.is('#overall')) {
            
                $("ul.criteria-container > li.rules").fadeOut();
                $("ul.criteria-container > li.categories").fadeOut();
            }
            else if(el.is('#rule')) {
                $("ul.criteria-container > li#rules_" + type_val).show();
                $("ul.criteria-container > li#rules_" + opposite_val).hide();
                $("ul.criteria-container > li.categories").hide();
            }
            else if(el.is('#category')) {
                $("ul.criteria-container > li#categories_" + type_val).show();
                $("ul.criteria-container > li#categories_" + opposite_val).hide();
                $("ul.criteria-container > li.rules").hide();
            }
        }
    });
    
    $('ul.criteria-container button#submit').click(function () {
        
        var params = {}
        params["type"] = $('ul.criteria-container input:radio[name="type"]:checked').attr("id");
        
        $("ul.criteria-container > li#subtype:visible").each(function () {
            params["subtype"] = $('ul.criteria-container input:radio[name="subtype"]:checked').attr("id");
        });
        
        $("ul.criteria-container > li.rules:visible").each(function () {
            params["rule"] = $(this).find("select option:selected").val()
        });
        
        $("ul.criteria-container > li.categories:visible").each(function () {
            params["category"] = $(this).find("select option:selected").val()
        });
                
        params["start"] = sel_dates["start"];
        params["end"] = sel_dates["end"];
        params["interval"] = $('ul.criteria-container input:radio[name="interval"]:checked').attr("id");
        
        var canvas = $("canvas#analysis_chart")[0]
        var ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        $.ajax({
            url: $SCRIPT_ROOT + "/analysis/data/",
            async: true,
            dataType: 'json',
            type: "post",
            data: params
        }).done(function (res) {
            console.log("res", res);
            var data = generateAnalysisChartData(res);
            console.log("chart data", data);
            createAnalysisChart(res);
        });
    });    
});

function dateToString(date)
{
        
    var year = date.getFullYear();
    var month = date.getMonth()+1;
    var day = date.getDate();

    if (day < 10) {
      day = '0' + day;
    }
    if (month < 10) {
      month = '0' + month;
    }

    return  year + '-' + month + '-' + day;
}
