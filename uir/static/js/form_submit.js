$(document).ready(function(){
    $("body").on("submit", "#comment-form", function(e){
        e.preventDefault();
        $(this).ajaxSubmit({
            url: "editComment",
            success:function(data,statusText,xhr){
                $(this).css("display","none");
                $("comment").text(data)
                }
            })
        })
    
    })

