$(document).ready(function(){
    $("body").on('click',"#edit_form",function(e){

            if ($("#comment-form").css("display") == "none"){
                $('#comment-form').css("display","inline");
                $("#comment").css("display", 'none')
                $(this).attr("class", "fas fa-arrow-left");
            }
            else{
                $("#comment-form").css("display", "none");
                $("#comment").css("display", 'inline');
                $(this).attr("class", "fas fa-edit");
                }
        });
    $("body").on('submit', '#active-form', function(e){
        $("#active-button").attr("disabled", true)
        e
        })
    })
