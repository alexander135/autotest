$(document).ready(function(){
    $("body").on("submit", "#comment-form", function(e){
        e.preventDefault();
        $('#comment-form').ajaxSubmit({
            url:  document.getElementById("comment-form").getAttribute("data") +"/editComment",
            success:function(data){
                $('#comment-form').css("display","none");
                $('#edit_form').attr('class', 'fas fa-edit');
                $('#comment').css("display", "inline");
                $("#comment").text(data)
                }
            })
        })
    
    })

