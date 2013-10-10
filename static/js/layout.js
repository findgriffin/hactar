$( document ).ready(function() {
    var what = $( "#what" )
    what.click(function( event ) {
        if (what.val() == 'http://') {
            $( "#what" ).val('');
        };
    });
    var why = $( "#why" )
    why.click(function( event ) {
        if (why.val() == 'Why?') {
            $( "#why" ).val('');
        };
    });
    var search = $( "#searchq" )
    search.click(function( event ) {
        if (search.val() == 'search memes') {
            $( "#searchq" ).val('');
        };
    });
    var username = $( "#username" )
    username.click(function( event ) {
        if (username.val() == 'username') {
            $( "#username" ).val('');
        };
    });
    var password = $( "#password" )
    password.click(function( event ) {
        if (password.val() == 'password') {
            $( "#password" ).val('');
        };
    });
});
