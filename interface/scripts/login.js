function loginVM() {
    this.logged = false
    this.loginData = {}
    this.validate = () => {
        this.logged = false
        if ($.cookie("sessionId")) {
            $.post(
                "/verifySession", 
                {"null": null},
                (result) => {
                    this.logged = result["isValid"];
                    this.updateLoginData()
                }
            ); 
        }
    }
    this.updateLoginData = () => {
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
