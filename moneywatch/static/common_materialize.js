
var tooltip_options = {"enterDelay": 300};

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

// importer: check if all transactions are complete and ready for saving
function checkTransactionsImport() {
    var complete = true;

    $("form#import_check .item_container").each(function () {
        var item = $(this);
        if(item.hasClass("in") || item.hasClass("out")) {
            var text = $(item).find("input[name='description']").val();
            var category = $(item).find("select[name='category'] option:checked:not([disabled])").val();
            if(text && category) {
                item.removeClass("incomplete");
                item.addClass("complete");
            } else {
                item.removeClass("complete");
                item.addClass("incomplete");
                complete = false;
            }
        }
        else if(item.hasClass("message")) {
            var noted = $(item).find("input[name='noted']").is(":checked");
            console.log(item, noted);
            if(noted) {
                item.removeClass("incomplete");
                item.addClass("complete");
            } else {
                item.removeClass("complete");
                item.addClass("incomplete");
                complete = false;
            }
        }
    });

    $("form#import_check button[type='submit']").prop("disabled", !complete);
}

$(function() {

    // initialize materialize
    M.AutoInit();

    // general: initialize dropdown menus
    $('.dropdown-trigger').dropdown({
        coverTrigger: false
    });

    // general: initialize tooltips
    $(".tooltipped").tooltip(tooltip_options);

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


    // overview: minimize categories that have no subcategories and no higlighted items
    $('div.category_container.no_subcategories').each(function() {
        if($(this).find(".category_content .highlighted").length == 0) {
            $(this).children(".category_content").hide();
        }
    });

    // overview: highlight category container for highlighted transactions as well
    $('div.category_container .category_content .highlighted').each(function() {
       $(this).closest(".category_container").addClass("highlighted");
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
    $('div.overview i.transaction_chart[data-chart-data-url]')
       .css("cursor", "pointer")
       .click(function() {
           modalChart($(this).data("chart-data-url"));
    });


    // import: multiple rule match - preset description and category if rule get's changed
    $('select.rule-select').change(function() {
        var selItem = $("select.rule-select option:selected");
        var description = selItem.attr("data-description");
        var category_id = selItem.attr("data-category-id");

        if( typeof(description) != "undefined")
        {
            $("div.multiple-rule-transaction input[name='description']").val(description);
        }
        else
        {
            $("div.multiple-rule-transaction input[name='description']").val(null);
        }

        if( typeof(category_id) != "undefined")
        {
            var select_el = $("div.multiple-rule-transaction select[name='category_id']");

            select_el.val(category_id);
            select_el.formSelect();
        }
        else
        {
            var select_el = $("div.multiple-rule-transaction select[name='category_id']");

            select_el.val(null);
            select_el.formSelect();
        }
    });

    // overview: show edit link if available when hovering a transaction
    $("div.overview div.transaction").hover(function(e) {
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
    },"div.transaction");

    // overview: show transaction details modal when clicking on transaction description
    $("div.overview div.transaction span.description").click(function() {
        modalTransactionDetails($(this).data("details-url"));
    });

    // overview: show transaction messages for current month
    $("span.message-modal").click(function() {
        modalTransactionDetails($(this).data("messages-url"));
    });


    // overview: show edit icon when hovering an account item
    $("div.account_overview table.account_detail").hover(function(e) {
       $(this).find("span.settings-icon").show();
    },
    function(e) {
       $(this).find("span.settings-icon").hide();
    });

    // importer: add index values to form elements before submitting
    $("form#import_check").submit(function (e) {
        $("form#import_check .item_container").each(function() {
            var el = $(this);
            var index = el.data("index");

            el.find("input,select").each(function() {
                var item = $(this);
                item.attr("name", index + "_" + item.attr("name"));
            });
        });
    });

    // importer: check transaction items (in/out) for completeness
    $("form#import_check .item_container").on("change", "select,input[type='checkbox']", function(event) {
        checkTransactionsImport();
    });

    // importer: check transaction items (in/out) for completeness
    $("form#import_check .item_container").on("input", "input[type='text']", function(event) {
        checkTransactionsImport();
    });

    // ruleset: enable check button, if "check historical transactions" is active
    $("input[name='check_historical']").change(function() {
        var checked = $(this).prop('checked');

        $("button.btn[value='check']").prop("disabled", !checked);
        $("button.btn.inital[value='save']").prop("disabled", checked);

        if(checked) {
            $("div.matched_transactions").slideDown();
        } else {
            $("div.matched_transactions").slideUp();
        }
    });
});


