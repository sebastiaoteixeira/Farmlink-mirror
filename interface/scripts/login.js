function isLogged() {
    if ($.cookie("sessionId")) {
        return $.ajax({
            url: "sessionId", 
            type: 'POST',
            data: {
                sessionId: $.cookie("sessionId")
            },
            success: () => {
                return true;
            },
            fail: () => {
                return false;
            }
        }); 
    } else {
        return false;
    }

}

