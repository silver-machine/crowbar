from error import error

class Stack:
    def __init__(self):
        self.stack = []

    def pop(self):
        try:
            return self.stack.pop()
        except IndexError:
            error("Stack Error", "Stack Underflow")
        
    def push(self, val):
        self.stack.append(val)