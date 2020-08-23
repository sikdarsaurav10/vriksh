$(window).on("load", function(){
    var city = $('#city').text();
    $.getJSON('https://thevriksh.in/category/items?city='+city+'&category_name=all', function(data){
      allProducts(data, city);
    });
    $.getJSON('https://thevriksh.in/category/items?city='+city+'&category_name=uttarakhand', function(data){
      uttarakhandProducts(data, city);
    });
    $.getJSON('https://thevriksh.in/category/items?city='+city+'&category_name=organic', function(data){
      organicProducts(data, city);
    });
    $.getJSON('https://thevriksh.in/category/items?city='+city+'&category_name=featured', function(data){
      featuredProducts(data, city);
    });
    $.getJSON('https://thevriksh.in/category/items?city='+city+'&category_name=seasonal', function(data){
      seasonalProducts(data, city);
    });
  });
  
  function allProducts(result, city) {
      list = ''
      if (result.success == '1'){
          if (result.Products.length > 0){
            for(var i=0;i<15;i++){
              if (result.Products[i].available == true) {
                let descp = result.Products[i].description
                list += '<div class="item">'
                list += '<div class="tile" style="transform: rotate(0);">'
                list += '<div>'
                list += '<img src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p>'+descp.substr(0,10)+'...</p>'
                list += '<a href="/product/details/'+city+'/'+result.Products[i].product_id+'" class="stretched-link"></a>'
                list += '</div>'
                list += '</div>'
                $('#allProducts').find('.resCarousel-inner').html(list)
              }
              else {
                let descp = result.Products[i].description
                list += '<div class="item">'
                list += '<div class="tile">'
                list += '<div>'
                list += '<img style="filter: grayscale(100%);" src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p style="color: red;">Not Available</p>'
                list += '</div>'
                list += '</div>'
                $('#allProducts').find('.resCarousel-inner').html(list)
              }
            }
          }
          else{
            list += '<div class="alert alert-warning">No Products Available</div>'
            $('#allProducts').find('.resCarousel-inner').html(list)
          }

      }
      else{
          list += 'Some error occured'
          $('#allProducts').find('.resCarousel-inner').html(list)
      }
  }
  
  function uttarakhandProducts(result, city) {
    list = ''
      if (result.success == '1'){
          if (result.Products.length > 0){
            for(var i=0;i<result.Products.length;i++){
              if (result.Products[i].available == true) {
                let descp = result.Products[i].description
                list += '<div class="item">'
                list += '<div class="tile" style="transform: rotate(0);">'
                list += '<div>'
                list += '<img src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p>'+descp.substr(0,10)+'...</p>'
                list += '<a href="/product/details/'+city+'/'+result.Products[i].product_id+'" class="stretched-link"></a>'
                list += '</div>'
                list += '</div>'
                $('#uttarakhandProducts').find('.resCarousel-inner').html(list)
              }
              else {
                let descp = result.Products[i].description
                list += '<div class="item">'
                list += '<div class="tile">'
                list += '<div>'
                list += '<img style="filter: grayscale(100%);" src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p style="color: red;">Not Available</p>'
                list += '</div>'
                list += '</div>'
                $('#uttarakhandProducts').find('.resCarousel-inner').html(list)
              }
            }
          }
          else{
            list += '<div class="alert alert-warning">No Products Available</div>'
            $('#uttarakhandProducts').find('.resCarousel-inner').html(list)
          }

      }
      else{
          list += 'Some error occured'
          $('#uttarakhandProducts').find('.resCarousel-inner').html(list)
      }
  }
  
  function organicProducts(result, city) {
    list = ''
      if (result.success == '1'){
          if (result.Products.length > 0){
            for(var i=0;i<result.Products.length;i++){
              if (result.Products[i].available == true) {
                let descp = result.Products[i].description
                list += '<div class="item">'
                list += '<div class="tile" style="transform: rotate(0);">'
                list += '<div>'
                list += '<img src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p>'+descp.substr(0,10)+'...</p>'
                list += '<a href="/product/details/'+city+'/'+result.Products[i].product_id+'" class="stretched-link"></a>'
                list += '</div>'
                list += '</div>'
                $('#organicProducts').find('.resCarousel-inner').html(list)
              }
              else {
                let descp = result.Products[i].description
                list += '<div class="item">'
                list += '<div class="tile">'
                list += '<div>'
                list += '<img style="filter: grayscale(100%);" src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p style="color: red;">Not Available</p>'
                list += '</div>'
                list += '</div>'
                $('#organicProducts').find('.resCarousel-inner').html(list)
              }
            }
          }
          else{
            list += '<div class="alert alert-warning">No Products Available</div>'
            $('#organicProducts').find('.resCarousel-inner').html(list)
          }

      }
      else{
          list += 'Some error occured'
          $('#organicProducts').find('.resCarousel-inner').html(list)
      }
  }
  
  function featuredProducts(result, city) {
    list = ''
      if (result.success == '1'){
          if (result.Products.length > 0){
            for(var i=0;i<result.Products.length;i++){
              if (result.Products[i].available == true) {
                let descp = result.Products[i].description
                list += '<div class="item">'
                list += '<div class="tile" style="transform: rotate(0);">'
                list += '<div>'
                list += '<img src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p>'+descp.substr(0,10)+'...</p>'
                list += '<a href="/product/details/'+city+'/'+result.Products[i].product_id+'" class="stretched-link"></a>'
                list += '</div>'
                list += '</div>'
                $('#featuredProducts').find('.resCarousel-inner').html(list)
              }
              else {
                let descp = result.Products[i].description
                list += '<div class="item">'
                list += '<div class="tile">'
                list += '<div>'
                list += '<img style="filter: grayscale(100%);" src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p style="color: red;">Not Available</p>'
                list += '</div>'
                list += '</div>'
                $('#featuredProducts').find('.resCarousel-inner').html(list)
              }
            }
          }
          else{
            list += '<div class="alert alert-warning">No Products Available</div>'
            $('#featuredProducts').find('.resCarousel-inner').html(list)
          }

      }
      else{
          list += 'Some error occured'
          $('#featuredProducts').find('.resCarousel-inner').html(list)
      }
  }
  
  function seasonalProducts(result, city) {
    list = ''
      if (result.success == '1'){
          if (result.Products.length > 0){
            for(var i=0;i<result.Products.length;i++){
              if (result.Products[i].available == true) {
                let descp = result.Products[i].description
                list += '<div class="item">'
                list += '<div class="tile" style="transform: rotate(0);">'
                list += '<div>'
                list += '<img src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p>'+descp.substr(0,10)+'...</p>'
                list += '<a href="/product/details/'+city+'/'+result.Products[i].product_id+'" class="stretched-link"></a>'
                list += '</div>'
                list += '</div>'
                $('#seasonalProducts').find('.resCarousel-inner').html(list)
              }
              else {
                let descp = result.Products[i].description
                list += '<div class="item">'
                list += '<div class="tile">'
                list += '<div>'
                list += '<img style="filter: grayscale(100%);" src="'+result.Products[i].prof_img+'" alt="">'
                list += '</div>'
                list += '<h5>'+result.Products[i].product_name+'</h5>'
                list += '<p style="color: red;">Not Available</p>'
                list += '</div>'
                list += '</div>'
                $('#seasonalProducts').find('.resCarousel-inner').html(list)
              }
            }
          }
          else{
            list += '<div class="alert alert-warning">No Products Available</div>'
            $('#seasonalProducts').find('.resCarousel-inner').html(list)
          }

      }
      else{
          list += 'Some error occured'
          $('#seasonalProducts').find('.resCarousel-inner').html(list)
      }
  }
  