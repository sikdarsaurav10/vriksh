$(window).on("load", function(){
    var city = $('#cityName').text();
    var cat = $('#catName').text();
    $.getJSON('https://thevriksh.in/category/items?city='+city+'&category_name='+cat+'', function(data){
      Products(data, city);
    });
  });

function Products(result, city){
    list = ''
      if (result.success == '1'){
          if (result.Products.length > 0){
            for(var i=0;i<result.Products.length;i++){
              if (result.Products[i].available == true) {
                list += '<div class="item">'
                list += '<div class="tile" style="transform: rotate(0);">'
                list += '<div>'
                list += '<img src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p>'+result.Products[i].description.substr(0,10)+'...</p>'
                list += '<a href="/product/details/'+city+'/'+result.Products[i].product_id+'" class="stretched-link"></a>'
                list += '</div>'
                list += '</div>'
                $('#moreProducts').find('.resCarousel-inner').html(list)
              }
              else {
                list += '<div class="item">'
                list += '<div class="tile">'
                list += '<div>'
                list += '<img style="filter: grayscale(100%);" src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p style="color: red;">Not Available</p>'
                list += '</div>'
                list += '</div>'
                $('#moreProducts').find('.resCarousel-inner').html(list)
              }
            }
          }
          else{
            list += '<div class="alert alert-warning">No Products Available</div>'
            $('#moreProducts').find('.resCarousel-inner').html(list)
          }

      }
      else{
          list += 'Some error occured'
          $('#moreProducts').find('.resCarousel-inner').html(list)
      }
}