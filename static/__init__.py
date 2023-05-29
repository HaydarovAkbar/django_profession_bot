class Messages:
    def __init__(self):
        self.messages = []

    def add(self, message):
        self.messages.append(message)

    def get(self):
        return self.messages

    def clear(self):
        self.messages = []

    welcome_bot = "<b>Assalomu alaykum, botga xush kelibsiz!\n\nYoshingizni kiriting:</b>"
    user_age_error = "<u>%age%</u> bu simvol to'g'ri kelmaydi:\n\nYoshingizni raqamlarda kiriting:"
