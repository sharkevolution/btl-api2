
 $(document).ready(function(){

  //Check to see if the window is top if not then display button
  $(window).scroll(function(){
    if ($(this).scrollTop() > 100) {
      $("#scroller").fadeIn();
    } else {
      $("#scroller").fadeOut();
    }
  });

  //Click event to scroll to top
  $("#scroller").click(function(){
    $("html, body").animate({scrollTop : 0},400);
    return false;
  });

 });
