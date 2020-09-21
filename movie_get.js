var return_first =  function() {                      
    var tmp = [] ;    
    $.ajax({                     
           type: "GET",                     
           url: 'https://vs3v3ahw4b.execute-api.us-east-2.amazonaws.com/Testing/recommend_movie',
           contentType: 'application/json',
           crossDomain: "true",  
           dataType: 'json',
           success: function(res){
            $.each(res, function(k, r){   
                 var m = JSON.parse(r);                                   
                 for (var i= 0 ; i< m.length; i++){
                   tmp.push(m[i])
                 }                   
              })               
             }
          });
          
          return tmp;
    }(); 
    