class User:
    def __init__(self, email="", password="", role="", id=""):
        self.email = email
        self.password = password
        self.role = role
        self.id = id

    def __repr__(self):
        return f"{self.email}, {self.role}"
