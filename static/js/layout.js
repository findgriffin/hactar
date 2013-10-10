window.onload = function(){
    // get submit button
    var submitbutton = document.getElementById("searchq");
    // add listener to button
    if(submitbutton.addEventListener){
        submitbutton.addEventListener("focus", function() {
            if (submitbutton.value == 'search memes'){
                submitbutton.value = '';
            }
        });
    };
    // get description field
    var descfield = document.getElementById("why");
    // add listener to descfield field
    if(descfield){
        if(descfield.addEventListener){
            descfield.addEventListener("focus", function() {
                if (descfield.value == 'Why?'){
                    descfield.value = '';
                }
            });
        };
    };
    // get description field
    var urlfield = document.getElementById("what");
    // add listener to urlfield field
    if(urlfield){
        if(urlfield.addEventListener){
            urlfield.addEventListener("click", function() {
                if (urlfield.value == 'http://'){
                    urlfield.value = '';
                }
            });
        };
    };
    // get description field
    var userfield = document.getElementById("username");
    if(userfield){
        if(userfield.addEventListener){
            userfield.addEventListener("focus", function() {
                if (userfield.value == 'username'){
                    userfield.value = '';
                }
            });
        };
    }; 
    // get description field
    var passfield = document.getElementById("password");
    if(passfield){
        if(passfield.addEventListener){
            passfield.addEventListener("click", function() {
                if (passfield.value == 'password'){
                    passfield.value = '';
                }
            });
        };
    };
}
