function loginVM() {
    this.logged = false
    this.loginData = {}
    this.validate = () => {
        if ($.cookie("sessionId")) {
            $.post(
                "/verifySession", 
                {
                    sessionId: $.cookie("sessionId")
                },
                (result) => {
                    this.logged = result["isValid"];
                }
            ); 
        } else {
            this.logged = false;
        }
    }
    this.updateLoginData = () => {
        this.validate()
        if (this.logged) {
            $.post(
                "/personalData",
                {
                    sessionId: $.cookie("sessionId")
                },
                (result) => {
                    this.loginData = result
                }
                
            )
        }
    }
}

var login = new loginVM()
login.validate()
