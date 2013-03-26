$(function(){
  
   //defaults
   $.fn.editable.defaults.url = '/post'; 

   /*
    //enable / disable
   $('#enable').click(function() {
       $('#user .editable').editable('toggleDisabled');
   });    
   */ 
    //editables 
    $('#comicname').editable({
           url: '/post',
           type: 'text',
           pk: 1,
           name: 'comicname',
           title: 'Enter username'
    });
});
