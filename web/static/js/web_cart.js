$(window).on("load", function(){
    getBillDeatils();
  });
  $(window).ready(function(){
    $('.increase').on("click", function(){
      var $n = $(this).parent().find(".quant");
      var p_id = $(this).parent().find(".pr_id").text();
      var $a = $(this).parent().parent().find(".productItemAmt");
      var $b = $(this).parent().parent().find(".productItemPrice")
      $.ajax({
        url: "/customer/web/cart/increase",
        type: "PUT",
        contentType: "application/json",
        data: JSON.stringify({"product_id": p_id}),
      }).done(function(data){
        if (data.success == '1') {
          $n.html(data.quantity);
          $.getJSON('https://thevriksh.in/cart/item/amount/'+p_id, function(data){
            $a.html(data.amt);
            $b.html(data.original_amt);
          })
          getBillDeatils();
        }
        else {
          alert("some error ocuured")
        }
      });
    })
    $('.deacrease').on("click", function(){
      var $n = $(this).parent().find(".quant");
      var p_id = $(this).parent().find(".pr_id").text();
      var $a = $(this).parent().parent().find(".productItemAmt");
      var $b = $(this).parent().parent().find(".productItemPrice")
      $.ajax({
        url: "/customer/web/cart/decrease",
        type: "PUT",
        contentType: "application/json",
        data: JSON.stringify({"product_id": p_id}),
      }).done(function(data){
        if (data.success == '1') {
          $n.html(data.quantity);
          $.getJSON('https://thevriksh.in/cart/item/amount/'+p_id, function(data){
            $a.html(data.amt);
            $b.html(data.original_amt);
          })
          getBillDeatils();
        }
        else if (data.success == '2') {
          location.reload(true);
          getBillDeatils();
        }
      });
    })
  });
  function getBillDeatils() {
    $.getJSON('https://thevriksh.in/customer/web/cart/amt', function(data){
      getAmt(data);
    });
  }

  function getAmt(result){
    if (result.success == '1') {
      $('#totalAmt').html("₹ "+result.amt);
      $('#totalSave').html("<strike>₹ "+result.price+"</strike>");
      $('#totalDiscount').html(result.offer+"%");
      $('#totalBill').html(result.bill);
      $('#charge').html(result.charge);
    }
  }

  $('#proceedToCheckOut').on("click", function(){
    var totalBill = $('#totalBill').text();
    var arr = [];
    var amtDetail = {
      "total_amount": totalBill,
      "delivery_method": "default"
    }
    arr.push(amtDetail);
    $('.ProductCol').each(function(){
      var item_id = $(this).find('.pr_id').text();
      var item_quantity = $(this).find('.quant').text();
      var item_price = $(this).find(".productItemAmt").text();
      product_details = {
        "product_id": item_id,
        "quantity": item_quantity,
        "total_price": item_price
      }
      arr.push(product_details);
    });

    $.ajax({
      url: "/customer/web/cart/place",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify(arr),
    }).done(function(data){
      if (data.success == '1'){
        $('#spinner').html('<div class="spinner-border" role="status"><span class="sr-only">Loading...</span></div>')
        window.location.replace("/customer/web/order/ongoing");
      }
      else if (data.success == '0'){
        $('#toast').css("display", "block");
        $('.toast-body').html('<p style="color: red">'+data.message+'</p>')
        $('.toast').toast('show');
      }
    });
  });
  $('#dismiss').on("click", function(){
    $('#toast').css("display", "none");
  });