import token
import lexer

INTEGER = 'INTEGER'
NUMBER = 'NUMBER'

PLUS = 'PLUS'
MINUS = 'MINUS'
MULTIPLY = 'MULTIPLY'
DIVIDE = 'DIVIDE'
MODULO = 'MODULO'

LPAREN = '('
RPAREN = ')'
LCURL = '{'
RCURL = '}'

ASSIGN = '='
SEMI = ';'
ID = 'ID'
COMMA = ','
DOT = '.'

FOR = 'FOR'
IF = 'IF'
ELSE = 'ELSE'
LET = 'LET'

EOF = 'EOF'

class Node(object):
    def __init__(self, line):
        self.line = line

class Program(Node):
    def __init__(self, declarations, line):
        Node.__init__(self, line)
        self.children = declarations

class VarDecl(Node):
    def __init__(self, varNode, typeNode, line):
        Node.__init__(self, line)
        self.varNode = varNode
        self.typeNode = typeNode

class Type(Node):
    def __init__(self, token, line):
        Node.__init__(self, line)
        self.token = token
        self.value = token.value

class Expression(Node):
    def __init__(self, children, line):
        Node.__init__(self, line)
        self.children = children

class Assign(Node):
    # assignment statements
    # left node is the variable and the right node is the node returned by the expr parser method
    def __init__(self, left, op, right, line):
        Node.__init__(self, line)
        self.left = left
        self.token = self.op = op
        self.right = right

class Var(Node):
    # holds a variable
    def __init__(self, token, line):
        Node.__init__(self, line)
        self.token = token
        self.value = token.value

class NoOp(Node):
    # empty statement
    pass

class BinOP(Node):
    def __init__(self, left, op, right, line):
        Node.__init__(self, line)
        self.left = left
        self.token = self.op = op
        self.right = right

class Num(Node):
    def __init__(self, token, line):
        Node.__init__(self, line)
        self.token = token
        self.value = token.value

class CompoundStmt(Node):
    def __init__(self, children, line):
        Node.__init__(self, line)
        self.children = children

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.currentToken = self.lexer.getNextToken()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, tokenType):
        if self.currentToken.type == tokenType:
            self.currentToken = self.lexer.getNextToken()
        else:
            self.error()

    def program(self):
        """Program Statement:   declarations"""
        root = Program(
            declarations= self.declarations(),
            line = self.lexer.line
        )
        return root

    def declarations(self):
        """
        declarations: declarationList
        """
        declarations = []
        while self.currentToken.type == LET:
            declarations.extend(self.declarationList)
        return declarations

    def declarationList(self):
        """
        declarationList: declaration+
        """
        result = self.declaration()
        while self.currentToken.type == LET:
            result.extend(self.declaration())
        return result

    def declaration(self):
        """
        declaration: typeSpec init_declaratorList SEMICOLON
        """
        result = list()
        typeNode = self.typeSpec()
        for node in self.init_declaratorList():
            if(isinstance(node, Var)):
                result.append(VarDecl(
                    typeNode=typeNode,
                    varNode=node,
                    line=self.lexer.line
                ))
            else:
                result.append(node)
            self.eat(SEMI)
            return result

    def init_declaratorList(self):
        """
        init_declaratorList: init_declarator (COMMA init_declarator)*
        """
        result = list()
        result.extend(self.init_declarator())
        while self.currentToken.type == COMMA:
            self.eat(COMMA)
            result.extend(self.init_declarator())
        return result

    def init_declarator(self):
        """
        init_declarator: variable (ASSIGN assignmentExpression)
        """
        var = self.variable()
        result = list()
        result.append(var)
        if self.currentToken.type == ASSIGN:
            token = self.currentToken
            self.eat(ASSIGN)
            result.append(Assign(
                left=var,
                op=token,
                right=self.assignmentExpression(),
                line=self.lexer.line
            ))
        return result

    def statement(self):
        """
        statement:  iterationStatement
                    selectionStatement
                    compoundStatement
                    expressionStatement
        Will add their functionalities and more later
        """
        if self.checkCompoundStatement():
            return self.compoundStatement()
        return self.expressionStatement()

    def checkCompoundStatement(self):
        return self.currentToken.type == LCURL

    def compoundStatement(self):
        """
        compoundStatement: LCURL (delcarationList | statement)* RCURL
        """
        result = []
        self.eat(LCURL)
        while self.currentToken.type != RCURL:
            if self.currentToken.type == LET:
                result.extend(self.declarationList())
            else:
                result.append(self.statement())
        self.eat(RCURL)
        return CompoundStmt(
            children=result,
            line=self.lexer.line
        )

    def expressionStatement(self):
        """
        expressionStatement: expression* SEMICOLON
        """

        node = None
        if self.currentToken.type != SEMI:
            node = self.expression()
        self.eat(SEMI)
        return node and node or NoOp(line=self.lexer.line)

    def expression(self):
        """
        expression: assignmentExpression (COMMA assignmentExpression)
        """
        result = list()
        result.append(self.assignExpression())
        while self.currentToken.type == COMMA:
            self.eat(COMMA)
            result.append(self.assignExpression())
        return Expression(
            children=result,
            line=self.lexer.line
        )

    def checkAssignmentExpression(self):
        if self.currentToken.type == ID:
            self.eat(ID)
            return (self.currentToken.type == ASSIGN)
        return False

    def assignmentExpression(self):
        """
        assignment_expression       : assignment_expression (COMMA assignment_expression)*
        """
        if self.checkAssignmentExpression():
            node = self.variable()
            while self.currentToken.type == ASSIGN:
                token = self.currentToken
                self.eat(token.type)
                return Assign(
                    left= node,
                    op=token,
                    right= self.assignmentExpression(),
                    line=self.lexer.line
                )

    def argumentExpressionList(self):
        """
        argument_expression_list    : assignment_expression (COMMA assignment_expression)*
        """
        args = [self.assignmentExpression()]
        while self.currentToken.type == COMMA:
            self.eat(COMMA)
            args.append(self.assignmentExpression())
        return args

    def primary_expression(self):
        """
        primary_expression          : LPAREN expression RPAREN
                                    | constant
                                    | variable
        """
        token = self.currentToken
        if token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expression()
            self.eat(RPAREN)
            return node
        elif token.type in (INTEGER, NUMBER):
            return self.constant()
        else:
            return self.variable()

    def constant(self):
        """
        constant                    : INTEGER_CONST
                                    | REAL_CONST
        """
        token = self.currentToken
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(
                token=token,
                line=self.lexer.line
            )
        elif token.type == NUMBER:
            self.eat(Num)
            return Num(
                token=token,
                line=self.lexer.line
            )

    def typeSpec(self):
        """
        typeSpec: Type
        """
        token = self.currentToken
        if token.type == LET:
            self.eat(token.type)
            return Type(
                token=token,
                line=self.lexer.line
            )

    def variable(self):
        """
        variable: ID
        """
        node = Var(
            token=self.currentToken,
            line=self.lexer.line
        )
        self.eat(ID)
        return node

    def empty(self):
        """An empty production"""
        return NoOp(
            line=self.lexer.line
        )

    def factor(self):
        token = self.currentToken
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def term(self):
        node = self.factor()
        while self.currentToken.type in (MULTIPLY, DIVIDE, MODULO):
            token = self.currentToken
            if token.type == MULTIPLY:
                self.eat(MULTIPLY)
            elif token.type == DIVIDE:
                self.eat(DIVIDE)
            elif token.type == MODULO:
                self.eat(MODULO)
            node = BinOP(left = node, op = token, right = self.factor())

        return node

    def expr(self):
        """
        expr   : term ((PLUS | MINUS) term)*
        term   : factor ((MUL | DIV) factor)*
        factor : INTEGER | LPAREN expr RPAREN
        """
        node = self.term()

        while self.currentToken.type in (PLUS, MINUS):
            token = self.currentToken
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOP(left=node, op=token, right=self.term())

        return node

    def parse(self):
        node = self.program()
        if self.currentToken.type != EOF:
            self.error()
        return node