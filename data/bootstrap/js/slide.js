function slideAjax(elementid, url, data){

       /*
       $.ajax({
         url: url,
         cache: false
       }).done(function( html ) {
         $("#results").append(html);
       });
      */

        //$('#'+elementid).hide(); //make sure the div we are loading into is hidden
        $.ajax({
            url: url,
            type: 'GET',
        }).done(function(data) {
            $(data).contents().appendTo("body");
           // $('body').load("url")
            //$('#'+elementid).html(data).show('slide',{direction: 'right'}, 200); //slide in
        });
 }
