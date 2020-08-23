//resCarousel
$(document).ready(function() { ResCarouselOnInit(); });

$(window).resize(function() {
    var r = new Date();
    setTimeout(function() {
        ResCarouselResize(r);
    }, 200);
});

function ResCarouselOnInit() {
    ResCarouselSize();
    $(document).on('click', '.leftRs, .rightRs', function() {
        ResCarousel(this);
    });
    $(document).on("mouseenter", ".ResHover", function() {
        $(this).addClass("ResHovered");
    });

    $(document).on("mouseleave", ".ResHover", function() {
        $(this).removeClass("ResHovered");
    });
}

// Rescarousel Auto Slide
function ResCarouselSlide(e) {
    var thiss = $(e).find(".rightRs");
    var dataInterval = $(e).attr('data-interval');
    !isNaN(dataInterval) && $(e).addClass("ResHover") && setInterval(function() {
        !(thiss.parent().hasClass("ResHovered")) && ResCarousel(thiss);
    }, +(dataInterval));
}

function ResCarouselResize() {
    function myfunction() {
        $('.resCarousel').each(function() {
            var divValue = $(this).attr('data-value');
            var itemWidth = $(this).find('.item').width();
            $(this).find(".resCarousel-inner").scrollLeft(divValue * itemWidth);
        });
    }
    myfunction();
}

//this function define the size of the items
function ResCarouselSize() {
    var t0 = performance.now();

    $('.resCarousel').each(function(index) {
        var itemsSplit = $(this).attr("data-items").split('-');
        $(this).addClass("ResSlid" + index);

        for (var i = 0; i < 4; i++) {
            if (i == 0) {
                var styleCollector0 = ".ResSlid" + index + " .item {width: " + 100 / itemsSplit[i] + "%}";
            } else if (i == 1) {
                var styleCollector1 = ".ResSlid" + index + " .item {width: " + 100 / itemsSplit[i] + "%}";
            } else if (i == 2) {
                var styleCollector2 = ".ResSlid" + index + " .item {width: " + 100 / itemsSplit[i] + "%}";
            } else if (i == 3) {
                var styleCollector3 = ".ResSlid" + index + " .item {width: " + 100 / itemsSplit[i] + "%}";
            }
        }

        $(this).attr("data-value", "0");

        var styleCollector = "@media (max-width:767px){" + styleCollector0 + "}" +
            "@media (min-width:768px){" + styleCollector1 + "}" +
            "@media (min-width:992px){" + styleCollector2 + "}" +
            "@media (min-width:1200px){" + styleCollector3 + "}";
        $(this).find("style").remove();
        $(this).append("<style>" + styleCollector + "</style>");
        ResCarouselSlide(this);

    });
    var t1 = performance.now();
    console.log('Took', (t1 - t0).toFixed(4), 'milliseconds to Size');
}

//this function used to move the items
function ResCarousel(Btn) {
    var parent = $(Btn).parent(),
        slide = +parent.attr("data-slide"),
        itemsDiv = parent.find('.resCarousel-inner'),
        itemSpeed = +parent.attr("data-speed"),
        itemLoad = +parent.attr("data-load"),
        translateXval = '',
        currentSlide = "",
        itemLenght = itemsDiv.find(".item").length,
        itemWidth = itemsDiv.find('.item').outerWidth(),
        dataItm = +Math.round(itemsDiv.outerWidth() / itemWidth),
        cond = $(Btn).hasClass("leftRs"),
        divValue = Math.round(itemsDiv.scrollLeft() / itemWidth);
    itemSpeed = !isNaN(itemSpeed) ? itemSpeed : 400;
    slide = slide < dataItm ? slide : dataItm;

    if (cond) {
        currentSlide = divValue - slide;
        translateXval = currentSlide * itemWidth;
        var MoveSlide = currentSlide + slide;
        if (divValue == 0) {
            currentSlide = itemLenght - slide;
            translateXval = currentSlide * itemWidth;
            currentSlide = itemLenght - dataItm;
            itemSpeed = 400;
        } else if (slide >= MoveSlide) {
            currentSlide = translateXval = 0;
        }
    } else {
        currentSlide = divValue + slide;
        translateXval = currentSlide * itemWidth;
        var MoveSlide = currentSlide + slide;

        if (divValue + dataItm == itemLenght) {
            currentSlide = translateXval = 0;
            itemSpeed = 400;
        } else if (itemLenght <= (MoveSlide - slide + dataItm)) {
            currentSlide = itemLenght - slide;
            translateXval = currentSlide * itemWidth;
            currentSlide = itemLenght - dataItm;
        }
    }

    parent.attr("data-animator") == "lazy" && resCarouselAnimator(itemsDiv, cond ? 0 : 1, currentSlide + 1, currentSlide + dataItm, itemSpeed, (slide * itemWidth));

    if (!isNaN(itemLoad)) {
        itemLoad = itemLoad >= slide ? itemLoad : slide;
        (itemLenght - itemLoad) <= (currentSlide + dataItm) && ResCarouselLoad1(itemsDiv);
    }
    itemsDiv.animate({ scrollLeft: translateXval }, itemSpeed);
    parent.attr("data-value", currentSlide);
}


function ResCarouselLoad1(e) {
    $("#" + e.attr("id")).trigger("ResCarouselLoad");
}

function resCarouselAnimator(parent, direction, start, end, speed, length) {
    var val = 5;
    if (direction == 0) {
        for (var i = start - 1; i < end + 1; i++) {
            val = val * 2;
        }
        val = -val;
    }
    for (var i = start - 1; i < end; i++) {
        val = direction == 0 ? val / 2 : val * 2;
        parent.find(".item").eq(i).css("transform", "translateX(" + val + "px)");
    }
    setTimeout(function() {
        parent.find(".item").attr("style", "");
    }, speed - 70);
}