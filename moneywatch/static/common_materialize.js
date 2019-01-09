
// materialize: initialize JS addons
$(document).ready(function(){
    M.AutoInit();
});
  
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
    $('.num').each(function () {
        item = $(this);
        
        if (Number(item.attr("num")) < 0)
        {
            item.addClass('negative');
        } 
        else
        {
            item.addClass('positive');
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
});
 