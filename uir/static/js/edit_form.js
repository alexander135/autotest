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
        $(this).children("#active-button").attr("disabled", true)
        });
    $("body").on('click', '.optbut', function(e){
        if ($(this).next().css('display') == 'none'){
            $(this).next().css('display', "block");
        }
        else{
            $(this).next().css('display', "none")
            
        }
    })
    })
