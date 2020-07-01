var sel_dates = {}
var analysis_chart = null;


function formatYearMonth(date) {
    return date.getFullYear() + "-" + ("0" + (date.getMonth() + 1)).slice(-2)
}

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


function showAllAccountOption()
{
     var select_el = $("ul.criteria-container select#account");
     var allaccounts_el = select_el.children("option.all_accounts");
     allaccounts_el.removeAttr("disabled");
     allaccounts_el.show();
     
     select_el.formSelect();
}

function hideAllAccountOption()
{
    var select_el = $("ul.criteria-container select#account");
    var allaccounts_el = select_el.children("option.all_accounts");
    
    if( allaccounts_el.is(':checked') ) {
        allaccounts_el.attr("disabled", true);
        select_el.children("option:first").prop("selected", "selected");
    }
    allaccounts_el.hide();
    
    select_el.formSelect();
    

    
    
}

function createRequestDataObject() {
    
    var selected_type_el = $('ul.criteria-container input:radio[name="type"]:checked');
    
    var selected_type_value = selected_type_el.attr("value");
    
    var selected_subtype_el = $('ul.criteria-container input:radio[name="subtype_'+selected_type_value+'"]:checked');
    var selected_subtype_value = selected_subtype_el.attr("value");
    
    var selected_account_el = $("ul.criteria-container select#account option:checked:not([disabled])");
    
    var selected_rule_el = $("ul.criteria-container select#rule option:checked:not([disabled])");
    
    var selected_category_el = $("ul.criteria-container select#category option:checked:not([disabled])");
    
    var timing_start_el = $("ul.criteria-container input#start:visible");
    var timing_end_el = $("ul.criteria-container input#end:visible");
    
    var timing_interval_el = $('ul.criteria-container input:radio[name="interval"]:checked');
    

    
    var result = {};
    var complete = true;
    
    result["type"] = selected_type_value;
    
    
    if(selected_subtype_el.length && (selected_type_value == "in" || selected_type_value == "out")) {
        
        result["subtype"] = selected_subtype_value;
        
         if(selected_subtype_value == "rule") {
            if( selected_rule_el.length) {
                result["rule"]= selected_rule_el.attr("value");
            } else {
                complete = false;
            }
         }
         
         
        if(selected_subtype_value == "category") {
            
            if(selected_category_el.length) {
                result["category"]= selected_category_el.attr("value");
            } else {
                complete = false;
            }
        }
    
    }
    
    if(selected_account_el.length) {
       result["account_id"] =  selected_account_el.attr("value");
    } else {
        complete = false;
    }
          

    if(timing_start_el.length && timing_start_el.val() != "") {
      result["start"] = timing_start_el.val();
    } else {
       complete = false;
    }
    
    if(timing_end_el.length && timing_end_el.val() != "") {
      result["end"] = timing_end_el.val();
    } else {
       complete = false;
    }
    
    
    if(timing_interval_el.length) {
       result["interval"] =  timing_interval_el.attr("value");
    } else {
        complete = false;
    }    


    if(complete) {
        return result;
    }
    
    return undefined;
    
}



function subtypeChangeHandler() {
    
    var selected_type_el = $('ul.criteria-container input:radio[name="type"]:checked');
    var selected_type_value = selected_type_el.attr("value");
    
    var selected_subtype_el = $('ul.criteria-container input:radio[name="subtype_'+selected_type_value+'"]:checked');
    var selected_subtype_value = selected_subtype_el.attr("value");
    
    var selected_account_el = $("ul.criteria-container select#account option:checked:not([disabled])");
    
    var selected_rule_el = $("ul.criteria-container select#rule option:checked:not([disabled])");
    
    var selected_category_el = $("ul.criteria-container select#category option:checked:not([disabled])");
    
    
    if(selected_type_el.length) {
        
        $("ul.criteria-container > li#account").slideDown();
    
        if(selected_type_el.is('#balance_absolute') || selected_type_el.is('#balance_relative')) {
                
            $("ul.criteria-container > li#subtype").slideUp();
            $("ul.criteria-container > li#rule").slideUp();
            $("ul.criteria-container > li#category").slideUp();
            $("ul.criteria-container  ul#subtype-menu-in").slideUp();
            $("ul.criteria-container  ul#subtype-menu-out").slideUp();
            
            showAllAccountOption();
        }
        else if(selected_type_el.is('#in')) {
            $("ul.criteria-container  ul#subtype-menu-in").slideDown();
            $("ul.criteria-container  ul#subtype-menu-out").slideUp();
            $("ul.criteria-container > li#account option.all_accounts").hide();
            hideAllAccountOption();
        }
        else if(selected_type_el.is('#out')) {
            $("ul.criteria-container  ul#subtype-menu-in").slideUp();
            $("ul.criteria-container  ul#subtype-menu-out").slideDown();
            $("ul.criteria-container > li#account option.all_accounts").hide();
            hideAllAccountOption();

        }
    }       
            
    
    if(selected_account_el.length && (selected_type_el.is("#in") || selected_type_el.is("#out") ) ) {
        
        var account_start = selected_account_el.data("start");
        var account_end = selected_account_el.data("end");
                    
        if(selected_subtype_el.length) {
            
            if(selected_subtype_el.is("#rule")) {
                // hide category selection and show the rule selection
                $("ul.criteria-container > li#category").slideUp();  
                showRuleSelect(selected_account_el.attr("value"), selected_type_el.attr("value"));
                
                if(selected_rule_el.length) {
                    var start = new Date(account_start);
                    var end = new Date(account_end);
                    
                    var rule_start = selected_rule_el.data("start");
                    var rule_end = selected_rule_el.data("end");
                    
                    if(rule_start != undefined) {
                        rule_start = new Date(rule_start);
                        
                        if(rule_start > start) {
                            start = rule_start
                        }
                    }
                    
                    if(rule_end != undefined) {
                        rule_end = new Date(rule_end);
                        if(rule_end < end) {
                            end = rule_end
                        }
                    }
                    
                    $("ul.criteria-container > li#timing input#start").attr("min", formatYearMonth(start));
                    $("ul.criteria-container > li#timing input#start").attr("max", formatYearMonth(end));
                    $("ul.criteria-container > li#timing input#end").attr("min", formatYearMonth(start));
                    $("ul.criteria-container > li#timing input#end").attr("max", formatYearMonth(end));
                    
                    $("ul.criteria-container > li#timing").slideDown();
                }
                
                
            } else if(selected_subtype_el.is("#category")) {
                // hide rule selection and show the category selection
                $("ul.criteria-container > li#rule").slideUp();  
                showCategorySelect(selected_account_el.attr("value"), selected_type_el.attr("value"));
                
                if(selected_category_el.length) {
                    var start = account_start;
                    var end = account_end;
                    
                    $("ul.criteria-container > li#timing input#start").attr("min", start);
                    $("ul.criteria-container > li#timing input#start").attr("max", end);
                    $("ul.criteria-container > li#timing input#end").attr("min", start);
                    $("ul.criteria-container > li#timing input#end").attr("max", end);
                    
                    $("ul.criteria-container > li#timing").slideDown();
                }
                
            } else {
              $("ul.criteria-container > li#rule").slideUp();  
              $("ul.criteria-container > li#category").slideUp();  
            }
        } else {
          $("ul.criteria-container > li#rule").slideUp();  
          $("ul.criteria-container > li#category").slideUp();  
        }
        
    } else {
         $("ul.criteria-container > li#rule").slideUp();  
         $("ul.criteria-container > li#category").slideUp();  
    }
    
    
    if(selected_account_el.length && (selected_type_el.is("#balance_absolute") || selected_type_el.is("#balance_relative") ) ) {
        
        var start = selected_account_el.data("start");
        var end = selected_account_el.data("end");
        
        $("ul.criteria-container > li#timing input#start").attr("min", start);
        $("ul.criteria-container > li#timing input#start").attr("max", end);
        $("ul.criteria-container > li#timing input#end").attr("min", start);
        $("ul.criteria-container > li#timing input#end").attr("max", end);
        
        $("ul.criteria-container > li#timing").slideDown();
    }
    
    
    // check for completeness and enable the submit button
    if(createRequestDataObject() !== undefined) {
        $("ul.criteria-container button#submit").removeClass("disabled");
    } else {
       $("ul.criteria-container button#submit").addClass("disabled"); 
    } 
    
}

// generate the rule select dropdown menu by request the data via AJAX
function showRuleSelect(account_id, type) {

    var select_el = $("ul.criteria-container > li#rule select#rule");
    var select_container = select_el.parents(".input-field");
      
    var spinner_el = $("ul.criteria-container > li#rule div.circle-spinner");
    
    
    var current_account_id = select_el.data("account_id");
    var current_type = select_el.data("type");
    
    
    if(current_account_id != account_id || current_type != type) {
        
        spinner_el.show()
        select_container.hide();
        
        $("ul.criteria-container > li#rule").slideDown();
        
        $.getJSON($SCRIPT_ROOT + "/analysis/rules/" + account_id + "/" + type + "/", function (data, textStatus) {
           
           if(Array.isArray(data)) {           
                 select_el.children("option:not([disabled])").remove();
                 
               $.each(data, function(index, item) {
                  var new_el = $("<option></option>");

                  new_el.attr("value", item.id);
                  
                  if(item.disabled) {
                    new_el.prop("disabled", true);
                  }
                  else {
                    new_el.data("start", item.start);
                    new_el.data("end", item.end);
                  }
                  new_el.html(item.name);
                  
                  select_el.append(new_el);
               });
               
               select_el.data("account_id", account_id);
               select_el.data("type", type);
               
               select_el.formSelect();   
               spinner_el.hide();
               select_container.show();
           
           }
        });
    
    } else {
        $("ul.criteria-container > li#rule").slideDown();
    }
}


// generate the category select dropdown menu by request the data via AJAX
function showCategorySelect(account_id, type) {

    var select_el = $("ul.criteria-container > li#category select#category");
    var select_container = select_el.parents(".input-field");
      
    var spinner_el = $("ul.criteria-container > li#category div.circle-spinner");
    
    var current_account_id = select_el.data("account_id");
    var current_type = select_el.data("type");
    
    
    if(current_account_id != account_id || current_type != type) {
        
        spinner_el.show()
        select_container.hide();
        
        $("ul.criteria-container > li#category").slideDown();
        
        $.getJSON($SCRIPT_ROOT + "/analysis/categories/" + account_id + "/" + type + "/", function (data, textStatus) {
           
           if(Array.isArray(data)) {           
                select_el.children("option:not([disabled])").remove();
                 
               $.each(data, function(index, item) {
                  var new_el = $("<option></option>");

                  new_el.attr("value", item.id);
                  new_el.html(item.path);
                  
                  select_el.append(new_el);
               });
               
               select_el.data("account_id", account_id);
               select_el.data("type", type);
               
               select_el.formSelect();   
               spinner_el.hide();
               select_container.show();
           
           }
        });
 
    } else {
        $("ul.criteria-container > li#category").slideDown();
    }
    

}


$(function () {


    $('ul.criteria-container input:radio[name="type"]').change(function(){
        subtypeChangeHandler();
    });

   
    $('ul.criteria-container select#account').change(function(){
       subtypeChangeHandler(); 
    });
    
    $('ul.criteria-container select#rule').change(function(){
       subtypeChangeHandler(); 
    });
    
    $('ul.criteria-container select#category').change(function(){
       subtypeChangeHandler(); 
    });
    
    $('ul.criteria-container input.subtype:radio').change(function(){
       subtypeChangeHandler(); 
    });
    
    $('ul.criteria-container input.interval').change(function(){
       subtypeChangeHandler(); 
    });
    
    $('ul.criteria-container input#start').change(function(){
       subtypeChangeHandler(); 
    });
    
    $('ul.criteria-container input#end').change(function(){
       subtypeChangeHandler(); 
    });
    
    $('ul.criteria-container button#submit').click(function () {
        
        var params = createRequestDataObject();
        
        if(params !== undefined) {            
            
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
                console.log("chart data response", res);
                var data = generateAnalysisChartData(res);
                console.log("generated chart data", data);
                createAnalysisChart(res);
            });
        
        }
    });    
});
