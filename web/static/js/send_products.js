$(window).ready(function(){

      $('.add').on("click", function() {
        var $n = $(this)
            .parent()
            .parent(".item-quantity")
            .find(".item");
        var value = $n.text();
        var quantity =  parseInt(value, 10);
        quantity = quantity + 1;
        $n.html(quantity);
    });

    $('.delete').on("click", function() {
        var $n = $(this)
            .parent()
            .parent(".item-quantity")
            .find(".item");
        var value = $n.text();
        var quantity =  parseInt(value, 10);
        if (quantity > 0 ){
            quantity = quantity - 1;
            $n.html(quantity);
        }
    });

    var arry1 = [];
    $('#sendItem').on("click", function () {
        var vendor_id = $('#vendor_id').text();
        arry1.push({ vendor_id: vendor_id});
        $('#sendProductsTable tr').each(function (a, b) {
            var id = $('.product_id', b).text();
            var name = $('.name', b).text();
            var $value = $('.quantity', b);
            var q = $value.find('.item').text();
            var quant = parseInt(q, 10);
            if (quant > 0){
                arry1.push({ product_id: id, quantity: q});
            }
        });
        $.ajax({
            url: "/admin/vendor/products/new",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(arry1),
        }).done(function(data){
            list = ''
            list += "<div class='alert alert-success'>Product sended to vendor</div>"
            $('#sendMsg').html(list);
        });
    });

});