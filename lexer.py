import token

INTEGER, PLUS, MINUS, MULTIPLY, DIVIDE, MODULO, LPAREN, RPAREN, EOF = (
        'INTEGER', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO', '(', ')', 'EOF'
        )

class Lexer(object):
    def __init__(self, text):
        # string input: "3 + 8"
        self.text = text
        # index to the text
        self.pos = 0
        # current token
        self.currentToken = None
        self.currentChar = self.text[self.pos]

    def error(self):
        raise Exception('Invalid syntax')

    def advance(self):
        # advance the pos variable to go to the next char
        self.pos += 1

        if self.pos > len(self.text) - 1:
            self.currentChar = None
        else:
            self.currentChar = self.text[self.pos]

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def skipWhiteSpace(self):
        # skip white spaces
        while self.currentChar is not None and self.currentChar.isspace():
            self.advance()

    def integer(self):
        # return an integer read in from the input
        result = ''
        while self.currentChar is not None and self.currentChar.isdigit():
            result += self.currentChar
            self.advance()

        return int(result)

    def getNextToken(self):
        "Lexical Analyzer"
        "Breaks the input into tokens"

        while self.currentChar is not None:
            if self.currentChar.isspace():
                self.skipWhiteSpace()
                continue

            if self.currentChar.isdigit():
                return token.Token(INTEGER, self.integer())

            if self.currentChar == '+':
                self.advance()
                return token.Token(PLUS, '+')

            if self.currentChar == '-':
                self.advance()
                return token.Token(MINUS, '-')

            if self.currentChar == '*':
                self.advance()
                return token.Token(MULTIPLY, '*')

            if self.currentChar == '/':
                self.advance()
                return token.Token(DIVIDE, '/')

            if self.currentChar == '%':
                self.advance()
                return token.Token(MODULO, '%')

            if self.currentChar == '(':
                self.advance()
                return token.Token(LPAREN, '(')

            if self.currentChar == ')':
                self.advance()
                return token.Token(RPAREN, ')')

            self.error()

        return token.Token(EOF, None)