from employee import Employee

class Manager(Employee):

    def __init__(self):
        self.designation = "Manager"

    def work(self):
        print(self.name + "manager working")