
// materialize: initialize JS addons
$(document).ready(function(){
    M.AutoInit();
});
  
  
function formatNumberEl(el) {
    item = $(el);
    
    if (Number(item.attr("data-num")) < 0)
    {
        item.addClass('negative').removeClass("positive");
    } 
    else
    {
        item.addClass('positive').removeClass("negative");
    }
}
  
$(function() {
    
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
    
    // overview: switch between current values and current incl. pending transactions
    $('table.balance th.current[data-enable-switch=1]')
       .css("cursor", "pointer")
       .click(function() {
           
           if($(this).hasClass("with_planned"))
           {
                $('table.balance td.current').hide(100, function() {
                   
                    $('table.balance td.current').each(function () {
                        $(this).attr("data-num", $(this).attr("data-without-planned-num"));
                        $(this).html($(this).attr("data-without-planned-formatted"));
                        formatNumberEl(this);
                    }).show(100);
                    
                    $('table.balance th.current').removeClass("with_planned");
                    $('div.with_planned_info').slideUp(200);
               });
           }
           else
           {
                $('table.balance td.current').hide(100, function() {
                    $('table.balance td.current').each(function () {
                        $(this).attr("data-num", $(this).attr("data-with-planned-num"));
                        $(this).html($(this).attr("data-with-planned-formatted"));
                        formatNumberEl(this);
                    }).show(100);
                    
                    $('table.balance th.current').addClass("with_planned");
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
    $('select.multiple-rule-select').change(function() {  
        var selItem = $("select.multiple-rule-select option:selected");
        var description = selItem.attr("data-description");
        var category_id = selItem.attr("data-category-id");
        
        if( typeof(description) != "undefined") 
        {
            $("table.multiple-rule-transaction input[name='description']").val($("select.multiple-rule-select option:selected" ).attr("data-description"));
        }
        else
        {
            $("table.multiple-rule-transaction input[name='description']").val(null);
        }
        
        if( typeof(category_id) != "undefined") 
        {
            $("table.multiple-rule-transaction select[name='category_id']").val(category_id );
        }
        else
        {
            $("table.multiple-rule-transaction select[name='category_id']").val(null);
        }
    });
});
 
 
