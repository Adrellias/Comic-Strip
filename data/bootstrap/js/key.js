
$(document).ready(function(){

  $(window).load(function() {
      key_nav();
  });

  function key_nav(){

      // CLICK NEXT PREV STRIP
      //$('.navStrip.right').click(nextStrip)
      //$('.navStrip.left').click(prevStrip)

      // NEXT COMIC (Should read correct starting posistion)
      //$('.navComic.down').click(nextComic)
      //$('.navComic.up').click(prevComic)

      //MAP THEM KEYS
      $(document).keydown(function(e){

          var keyCode = e.keyCode || e.which,
          arrow = {sleft:37, sright:39, sup:38, sdown:40};

          switch (keyCode) {
          case arrow.sleft:
                 prevStrip();
          break;
          case arrow.sright:
                 nextStrip();
          break;
          case arrow.sup:
                 prevComic();
          break;
          case arrow.sdown:
                 nextComic();
          break;
          };
     });


      // Functions for navigation
      //
      // We need to get the active strip here
      // 
      // We need to get the active comic here
      var activestrip = $('.activeStrip');
      var comicId = $('#comicId').attr("value");
      var inmotion = false;

      function nextStrip() {
             var nextStrip = $('#nextStrip').val();

             if (nextStrip != undefined) {
                 document.location = getAbsolutePath() + '/' + nextStrip;
             } else {
               return false;
             }
      };

      function prevStrip() {
             var prevStrip = $('#prevStrip').val();

             if (prevStrip != undefined) {
                 document.location = getAbsolutePath() + '/' + prevStrip;
             }  else {
                return false;
             }
      };

      function getAbsolutePath() {
              var loc = window.location;
              var pathName = loc.pathname.substring(0, loc.pathname.lastIndexOf('/'));
              return loc.href.substring(0, loc.href.length - ((loc.pathname + loc.search + loc.hash).length - pathName.length));
      };
  };

});
