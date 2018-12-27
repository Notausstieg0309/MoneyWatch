

  $(document).ready(function(){
     M.AutoInit();
  });
  
 $(function() {
     
      $("select[name='regular']").on("change", function() {
       var optionSelected = $("option:selected", this);

       if(optionSelected.val() != "0") 
       {
        $('div#regular_form_fields:hidden').slideDown();
        $('div#regular_form_fields input').prop("required", true);
       }
       else
       {
            console.log("u")
            $('div#regular_form_fields:visible').slideUp();
            $('div#regular_form_fields input').prop("required", false);
       }
    });
    
    $('.num').each(function () {
        var item = $(this).attr("num");

        if (Number(item) < 0) {
            $(this).addClass('negative');
        }else{
            $(this).addClass('positive');
        }
    });
    
        $('div.category_container.no_subcategories').each(function() {
        $(this).children(".category_content").hide();
    });
    
    
    
    $('div.category_container:not(.overview)').each(function () {
        
         var item = $(this)
         
         caption = $(item.children("div.category_header"));
         
         caption.click(function() {
             
            var item = $($(this).next(".category_content"));

            item.slideToggle(200);
        });
        
        caption.css("cursor", "pointer");
    });
 });
 