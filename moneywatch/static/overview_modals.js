$(function() {
    $('div.modal').modal({
      dismissible: true,
    });
});

var chart;


function generateChartData(res, regular, month_names)
{
    var labels = []
    var data = []
    var pointBackgroundColors = [];
    var links = [];
    
    
    $.each(res, function(index, item) 
    {
        var label = generateLabel(item.day, item.month, item.year, regular, month_names);
        
        if(labels.includes(label))
        {
            var index = labels.indexOf(label);
            
            data[index] += item.valuta;
 
            pointBackgroundColors[index] = (item.reference ? "#ff0000" : "#000000");
        }
        else
        {
            labels.push(label);
            data.push(item.valuta);
            
            links.push("/"+item.year+"/"+item.month+"/");
            
            if(item.reference)
            {
                pointBackgroundColors.push("#ff0000");
            }
            else
            {
               pointBackgroundColors.push("#000000");
            }
        }          
    });
    
    return {labels: labels, data: data, pointBackgroundColors: pointBackgroundColors, links: links};
}


function generateLabel(day, month, year, regular, month_names)
{
    var date = new Date(year, month, day);
    
    switch(regular)
    {
        case 1:
            return month_names[month - 1] + " " + year;        
        case 3:
            return "Q" + Math.ceil(month/3) + " " + year;
        case 6:
            return "H" + Math.ceil(month/6) + " " + year;
        case 12:
            return year;
    }
}


function modalChart(url)
{
    showInitModal();
    
    $.ajax({
        url: $SCRIPT_ROOT + url,
        async: true,
        dataType: 'json',
        type: "get",
    }).done(function (res) {

        var backgroundColor = (res.type == "in" ? "rgba(0,255,0,0.1)" : "rgba(255,0,0,0.1)");
        
        var items = generateChartData(res.data, res.regular, res.month_names)
        var ctx = $("div.modal canvas")[0].getContext('2d');
       
        $("div.modal h4#caption").html(res.description);
        
        
       
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: items.labels,
                datasets: [
                            { 
                                label: res.description,
                                data: items.data,
                                links: items.links,
                                pointBackgroundColor: items.pointBackgroundColors,
                                backgroundColor: backgroundColor,
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
                            fontColor: (res.type == "in" ? "#006d14" : "#ff0000")
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
                
                }
            }
            
      
        });
        
        $("div.modal canvas").on('click', function(evt){
            var activePoint = chart.getElementAtEvent(evt);
            if(activePoint[0])
            {
                var URL = chart.data.datasets[activePoint[0]._datasetIndex].links[activePoint[0]._index];
                window.location.href = $SCRIPT_ROOT + URL;
            }
        });
        
        $("div.modal canvas").show();
        
        $("div.modal div.progress").hide();
    }).fail(function () {
        $('div.modal').modal("close");
    });
    
}

function getLang()
{
    if (navigator.languages != undefined) 
    return navigator.languages[0]; 
    else 
    return navigator.language;
}

function showInitModal()
{
    
    $("div.modal h4#caption").html("");
    $("div.modal div.progress").fadeIn();
    $("div.modal canvas").off("click").hide();
    $("div.modal ul").remove();
    
    if(chart)
        chart.destroy();
    
    var canvas = $("div.modal canvas")[0];
    var context = canvas.getContext('2d');
    
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.beginPath();
    
    $('div.modal').modal("open");
}



function modalTransactionDetails(url)
{
    $.ajax({
        url: $SCRIPT_ROOT + url,
        async: true,
        dataType: 'html',
        type: "get",
    }).done(function (res) {
        
       
        showInitModal();
        $("div.modal div.progress").hide();
          
        $("div.modal div.modal-content").append(res);
        $('div.modal .num').each(function () { formatNumberEl(this); });
    });
}
