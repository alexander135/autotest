function display_login_form_errors(errors, $form) {
            for (var k in errors) {
                $("body").find('#'+ k).after('<span class="form_error" id = "form_error">' + errors[k] + '</span>');
}
};


$(document).ready(function(){
    $("body").on('click', "#login_but", function(e){
        $("#login_div").load('/login');
    });
    $("#login_div").on("click", "#submit", function(e){
        e.preventDefault();
        $("#login_form").ajaxSubmit({
            url: "/login",
            success: function(data){
                $("#login_form").find('.form_error').remove();
                data = JSON.parse(data); 
                if (data['status']) {
                    window.location = "/";
                }
                else{
                 display_login_form_errors(data['errors'], $("#login_form"));
                }
            }
        })
    })
    })
