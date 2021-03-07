// Infinite Scroll based on (https://github.com/brianmario/jquery-infinite-scroll)
(function($) {
    $.fn.infinitescroll = function(options) {
        return $(this).each(function() {
            var el = $(this);
            var settings = $.extend({
                    url: null,
                    triggerAt: 500,
                    nextPage: 1,
                    appendTo: '.list tbody',
                    container: $(document)
                }, options);
            var req = null;
            var maxReached = false;


            var infinityRunner = function() {
                if (settings.url !== null) {
                    if  (settings.force || (settings.triggerAt >= (settings.container.height() - el.height() - el.scrollTop()))) {
                        settings.force = false;
                        // if the request is in progress, exit and wait for it to finish
                        if (req && req.readyState < 4 && req.readyState > 0) {
                            return;
                        }
                        // clear the container in case we start all over again
                        if (settings.nextPage == 1) {
                            $(settings.appendTo).html("");
                        }

                        $(settings.appendTo).trigger('infinitescroll.beforesend');
                        var params = $.extend($(settings.appendTo).data("params"), {page: settings.nextPage});

                        req = $.get({
                            url: settings.url,
                            data: params,
                            dataType: "html",
                            success: function(data) {
                                if (data !== '') {
                                    $(settings.appendTo).append(data);
                                    settings.nextPage++;
                                    $(settings.appendTo).trigger('infinitescroll.finish');
                                    // run the function again, in case the screen is not filled up enough, it will load another round
                                    infinityRunner();
                                } else {
                                    maxReached = true;
                                    if(settings.nextPage == 1) {
                                        $(settings.appendTo).trigger('infinitescroll.nodata');
                                    } else {
                                        $(settings.appendTo).trigger('infinitescroll.maxreached');
                                    }
                                }
                            },
                        });
                    }
                }
            };

            el.bind('infinitescroll.scrollpage', function(e, page) {
                settings.nextPage = page;
                settings.force = true;
                infinityRunner();
            });

            el.scroll(function(e) {
                if (!maxReached) {
                    infinityRunner();
                }
            });

            // Test initial page layout for trigger
            infinityRunner();
        });
    };
})(jQuery);