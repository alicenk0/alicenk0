$('.grid,.about')
    .click(function(){
        $('#viewspace .info.viewer').empty();
        var selectedGrid = $(this).find('.info')[0].innerHTML;
        $('#viewspace .info.viewer').append(selectedGrid);
        $('.close').fadeIn('slow');
        $('#viewspace').show();
        $('#viewspace .info.viewer').slideDown("slow", function(){
		  $('#viewspace .info.viewer').css({display:"block"});
        });
        $("html, body").animate({scrollTop: 0}, "fast");
    });

$('.close')
    .click(function(){
        $('.info').fadeOut();
        $('.close').fadeOut();
        $('#viewspace').slideUp("slow");
        $('.grid:hover').css({opacity: 0.5},1000, function(){});
    });

$('.next')
    //.click(function(){
    .on('keydown click', function(e) {
        var next = $(".info[style*='block']").parent().next().attr('class').split(' ')[0];
        console.log(e.keyCode);
        //$('#viewspace').empty();
        $('.info').fadeOut();
        $('.'+next).find('.info').fadeIn('slow');
        $('.'+next).find('.info').css('top','80px');
    });

 $('.prev')
    .click(function(){
        var prev = $(".info[style*='block']").parent().prev().attr('class').split(' ')[0];
        console.log('.'+prev);
        //$('#viewspace').empty();
        $('.info').fadeOut();
        $('.'+prev).find('.info').fadeIn('slow');
        $('.'+prev).find('.info').css('top','80px');
    });

$('#filterList li')
    .click(function()
       {var filter = this.id;
       console.log(filter);
       $('#filterList li').removeClass('selectedFilter');
       $('.' + filter).fadeIn(800,function(){});
        $('.grid').not('.' + filter).hide(1000,function(){});
        $('.grid').not('.' + filter).find('.info').hide(1000,function(){});
        $(this).addClass('selectedFilter');
    });

$.preloadImages = function() {
    for (var i = 0; i < arguments.length; i++) {
        $("<img />").attr("src", arguments[i]);
    }
}
    $.preloadImages("images/memorygif2.gif");



//video rescale with window
var $allVideos = $("iframe[src^='//player.vimeo.com'], iframe[src^='//www.youtube.com']"),
    // The element that is fluid width
    $fluidEl = $("body");

// Figure out and save aspect ratio for each video
$allVideos.each(function() {
  $(this)
    .data('aspectRatio', this.height / this.width)
    // and remove the hard coded width/height
    .removeAttr('height')
    .removeAttr('width');
});

// When the window is resized
$(window).resize(function() {
  var newWidth = $fluidEl.width();
  // Resize all videos according to their own aspect ratio
  $allVideos.each(function() {
    var $el = $(this);
    $el
      .width(newWidth)
      .height(newWidth * $el.data('aspectRatio'));
  });
// Kick off one resize to fix all videos on page load
}).resize();
