$(document).ready(function() {                      
    $("button").click(function(e) 
    {                 
             e.preventDefault();     
             console.log($('#moviename').val()) ;                                           
             $.ajax({                     
             type: "POST",                     
             url: 'https://vs3v3ahw4b.execute-api.us-east-2.amazonaws.com/Testing/recommend_movie',
             contentType: 'application/json',
             crossDomain: "true",   
             data: {
                 "body-json" : $('#moviename').val(),    
                 "context" : 
                     {
                         "http-method" : "POST",
                         "resource-path" : "/recommend_movie"
                     }

             },                     
             success: function(res){                 
                $('#output').empty();   
                $('#form-response').empty();
                 var movie = JSON.parse(res['body']);
            
                 for (var i =0 ; i<5; i++){
                      
                      $('#output').append('<div class="container-fluid post-container"> <div class="row"> <div class="col-lg-3 col-md-3 col-sm-3"><img  src="'+movie["wiki_movie"][i][2]+'"alt="Responsive image"/></div> <div class="col-lg-9 col-md-9 col-sm-9 px-3"> <h4 class="card-title">Movie Title:'+movie["wiki_movie"][i][0]+'</h4><p class="card-text">'+movie["wiki_movie"][i][1]+'</p> </div></div></div>');                      
                 };

              },

             error: function(){
             $('#output').empty(); 
             $('#form-response').empty();
             $('#form-response').html('<div class="alert alert-info" role="alert">Something went wrong... We are working on it!</div>');                     
             }}); 
     }) 
   }); 