$(document).ready(function(){
    $("body").on('click',"#edit_form",function(e){

            if ($(this).css("display") == none){
                $(this).css("display","inline");
            }
            else{
                $(this).css("display", "none");
                }
        })
    })
