$(document).ready(function() {
    $("#sidebarCollapse").on("click", function() {
      $("#sidebar").addClass("active");
    });
  
    $("#sidebarCollapseX").on("click", function() {
      $("#sidebar").removeClass("active");
    });
  
    $("#sidebarCollapse").on("click", function() {
      if ($("#sidebar").hasClass("active")) {
        $(".overlay").addClass("visible");
      }
    });
  
    $("#sidebarCollapseX").on("click", function() {
      $(".overlay").removeClass("visible");
    });
  });


function locationBox() {
  list = ''
  $.getJSON('https://thevriksh.in/city', function(data){
    list = ''
    list += '<div class="card locCard">'
    list += '<div class="card-body">'
    list +='<h5 class="card-title">Choose City</h5>'
    list += '<hr>'
    list += '<form id="locForm" action="/getcity" method="POST">'
    $.each(data.cities, function(i, city){
      list += '<div class="form-check">'
      list += '<input class="form-check-input" type="radio" name="city" id="Radios'+i+'" value="'+city+'">'
      list += '<label class="form-check-label" for="Radios'+i+'">'+city.toUpperCase()+'</label>'
      list += '</div>'
    });
    list += '<div class="text-right">'
    list += '<button type="submit" class="btn btn-primary mt-2">Submit</button>'
    list += '</div>'
    list += '</form>'
    list += '</div>'
    list += '</div>'
    $('.locBox').html(list)
  });
}
