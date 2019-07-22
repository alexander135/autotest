function display_form_errors(errors, $form) {
        for (var k in errors) {
            $("body").find('i#edit_form').after('<div class="form_error" id = "form_error">' + errors[k] + '</div>');
                    }
};

$(document).ready(function(){
    $("body").on("submit", "#comment-form", function(e){
        e.preventDefault();
        $('#comment-form').ajaxSubmit({
            url:  document.getElementById("comment-form").getAttribute("data") +"/editComment",
            success:function(data){
                $("div").find('#form_error').remove();
                var data = JSON.parse(data);
                if (data['status']){
                $('#comment-form').css("display","none");
                $('#edit_form').attr('class', 'fas fa-edit');
                $('#comment').css("display", "inline");
                $("#comment").text(data["comment"])
                    }
                else{
                    display_form_errors(data['errors'], $("#comment-form"))    
                }
                }
            })
        })
    
    })

