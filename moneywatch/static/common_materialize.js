
// materialize: initialize JS addons
$(document).ready(function(){
    M.AutoInit();
    
    // custom initialization of tooltips due to specific options for tooltip appearance
    var elems = document.querySelectorAll('.tooltipped');
    var instances = M.Tooltip.init(elems, {"enterDelay": 500});
    
});
  
  
function formatNumberEl(el) {
    item = $(el);
    
    if (Number(item.data("num")) < 0)
    {
        item.addClass('negative').removeClass("positive");
    } 
    else
    {
        item.addClass('positive').removeClass("negative");
    }
}
  
function copyToClipboard(value) {
    var $temp = $("<input>");

    $("body").append($temp);
    $temp.val(value).select();
    document.execCommand("copy");
    $temp.remove();
}

$(function() {
    
    // general: initialize dropdown menus
    $('.dropdown-trigger').dropdown({
        coverTrigger: false
    });
    
    // general: initialize dropdown menus with special for nav menu dropdown
    $('.dropdown-trigger-hover').dropdown({
        coverTrigger: false,
        hover: true,
        alignment: 'right',
    });
    
    // ruleset: hide/show additional inputs at ruleset add/change views
    $("select[name='regular']").on("change", function() {

        if($("option:selected", this).val() != "0") 
        {
            $('div#regular_form_fields:hidden').slideDown();
            $('div#regular_form_fields input').prop("required", true);
        }
        else
        {
            $('div#regular_form_fields:visible').slideUp();
            $('div#regular_form_fields input').prop("required", false);
        }
    });
    
    // general: colorize all numeric values 
    $('.num').each(function () { formatNumberEl(this); });
    
    $('.copy-clipboard').on("click", function () {
        var val = $(this).data("copy-value");
        copyToClipboard(val);
    });

    // overview: switch between current values and current incl. pending transactions
    $('table.profit th.current[data-enable-switch=1]')
       .css("cursor", "pointer")
       .click(function() {
           
           if($(this).hasClass("with_planned"))
           {
                $('table.profit td.current').hide(100, function() {
                   
                    $('table.profit td.current').each(function () {
                        $(this).data("num", $(this).data("without-planned-num"));
                        $(this).html($(this).data("without-planned-formatted"));
                        formatNumberEl(this);
                    }).show(100);
                    
                    $('table.profit th.current').removeClass("with_planned");
                    $('div.with_planned_info').slideUp(200);
               });
           }
           else
           {
                $('table.profit td.current').hide(100, function() {
                    $('table.profit td.current').each(function () {
                        $(this).data("num", $(this).data("with-planned-num"));
                        $(this).html($(this).data("with-planned-formatted"));
                        formatNumberEl(this);
                    }).show(100);
                    
                    $('table.profit th.current').addClass("with_planned");
                    $('div.with_planned_info').slideDown(200);
                });
           }
       });
       
    
    // overview: minimize categories that have no subcategories
    $('div.category_container.no_subcategories').each(function() {
        $(this).children(".category_content").hide();
    });
    

    // overview: enable collapse functionality of category container
    $('div.category_container:not(.overview)').each(function () {
        $(this).children("div.category_header")
            .css("cursor", "pointer")
            .click(function() {
                $(this).next(".category_content").slideToggle(200);
            })
        ;
    });
   
    // overview: add click handler for transaction charts modal popup
    $('div.overview i.transaction_chart[data-transaction-id]')
       .css("cursor", "pointer")
       .click(function() {
           modalChart("/ajax/transaction_chart/"+$(this).attr("data-transaction-id")+"/");
    }); 
   
   
    // import: multiple rule match - preset description and category if rule get's changed
    $('select.rule-select').change(function() {  
        var selItem = $("select.rule-select option:selected");
        var description = selItem.attr("data-description");
        var category_id = selItem.attr("data-category-id");
        var desc_no_replace = $("ul.collection input[name='description']").attr("data-rule-no-replace");
        var cat_no_empty = $("ul.collection select[name='category_id']").attr("data-rule-no-empty");
        
        if(desc_no_replace != "1")
        {
            if( typeof(description) != "undefined") 
            {
                $("ul.collection input[name='description']").val(description);
            }
            else
            {
                $("ul.collection input[name='description']").val(null);
            }
        }
        
        if( typeof(category_id) != "undefined") 
        {
            $("ul.collection select[name='category_id']").val(category_id);
        }
        else if(cat_no_empty != "1")
        {
            $("ul.collection select[name='category_id']").val(null);
        }   
    });
    
    // overview: show edit link if available when hovering a transaction
    $("div.overview div.transaction").hover(function(e) {
       var id = $(this).attr("data-id");;
       
       $(this).find("span.edit").show();
    },
    function(e) {
        $(this).find("span.edit").hide();
    });   
    
    // transactions: show transaction edit link when hovering a transaction in transactions overview
    //               must be done via on() function as dynamic elements can show up, when opening transaction details modal
    $("body").on({  "mouseover": function(e) {
                                   $(this).find("span.edit").show();
                                 },
                    "mouseleave": function(e) {
                                    $(this).find("span.edit").hide();  
                                  }
    },"ul.transactions_overview table.transactions");
    
    // overview: show edit link if available when hovering a transaction
    $("div.overview div.transaction span.description").click(function() {
        modalTransactionDetails("/transactions/single/"+$(this).attr("data-transaction-id")+"/");
    });
    
    // overview: show transaction messages for current month
    $("span.message-modal").click(function() {
        modalTransactionDetails("/" + $(this).attr("data-account-id") + "/transactions/messages/" + $(this).attr("data-year") + "/" + $(this).attr("data-month") + "/" + $(this).attr("data-month-count") + "/");
    });
    
    
    // overview: show edit icon when hovering an account item
    $("div.account_overview table.account_detail").hover(function(e) {
       $(this).find("span.settings-icon").show();
    },
    function(e) {
       $(this).find("span.settings-icon").hide();
    });  
});
 
 
