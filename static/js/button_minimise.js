$(document).ready( function() {

$(".btn-minimise").click(function(){
    $(this).toggleClass("glyphicon-minus glyphicon-plus");
    $(this).parents('div').eq(0).nextAll().slice(0, 2).slideToggle();
    console.log($(this).parents('div').eq(0).nextAll().slice(0, 2)); 
      })
	
});







    
