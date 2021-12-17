class LoginService:
    SESSION_ID = 0

    def loggedin(self):
        return self.SESSION_ID == 0
