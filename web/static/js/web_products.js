$(window).ready(function(){
    $('.addToBtn button').on("click", function(){
        pr_id = this.value;
        $.ajax({
          url: "/customer/web/cart/add/new",
          type: "POST",
          contentType: "application/json",
          data: JSON.stringify({"product_id": pr_id}),
        }).done(function(data){
          if (data.success == "1"){
            $('#toast').css("display", "block");
            $('.toast-body').html('<p style="color: green">'+data.message+'</p>')
            $('.toast').toast('show');
          }
          else if (data.success == "0"){
            $('#toast').css("display", "block");
            $('.toast-body').html('<p style="color: red">'+data.message+'</p>')
            $('.toast').toast('show');
          }
      });
      });
      $('#dismiss').on("click", function(){
      $('#toast').css("display", "none");
      });
});