$(window).ready(function(){
    $('.toast').toast('show');

    $('#adminForm').on("submit", function(e){
        e.preventDefault();
        var email = $('#InputEmail1').val();
        var name = $('#InputName').val();
        var pwd = $("#InputPassword1").val();

        var data_admin = JSON.stringify({
            "email": email,
            "name": name,
            "password": pwd
        });
        $.ajax({
            url: "/admin/new/create",
            type: "POST",
            contentType: "application/json",
            data: data_admin
        }).done(function(data){
            list = ''
            if (data.success == "1"){
                list += "<div class='alert alert-success' role='alert'>Admin Created Successfully</div>"
            }
            else if (data.success == "2"){
                list += "<div class='alert alert-warning' role='alert'>Admin already exist!!</div>"
            }
            else{
                list += "<div class='alert alert-danger' role='alert'>There was some problem encountered</div>"
            }
            $('#msg').html(list)
        });
    });
});