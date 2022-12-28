function Login() {
    self = this
    self.logged = ko.observable();
    self.loginData = ko.observable({});
    self.validate = () => {
        self.logged(false);
        if ($.cookie("sessionId")) {
            $.post(
                "/verifySession", 
                {},
                (result) => {
                    self.logged(result["isValid"]);
                    self.updateLoginData()
                }
            ); 
        }
    }
    self.updateLoginData = () => {
        if (self.logged()) {
            $.post(
                "/personalData",
                {},
                (result) => {
                    self.loginData(result);
                }
                
            )
        }
    }
    self.logout = () => {
        $.removeCookie("sessionId");
        self.validate()
    }
}

var login = new Login()
login.validate()
