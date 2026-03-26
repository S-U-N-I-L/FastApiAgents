from employee import Employee

class Developer(Employee):

    def __init__(self):
        self.designation = "Developer"

    def work(self):
        print(self.name + "developer working")