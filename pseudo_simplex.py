import numpy as np
import matplotlib as mp

class Sinal:
    MAIOR_IGUAL = 1
    IGUAL = 0
    MENOR_IGUAL = -1
    
class Tipo:
    MAX = 1
    MIN = 0

class Simplex:
    def __init__(self, f_o, obj):
        # Determina qual eh a funcao objectivo
        self.f_o = f_o
        # Funcao objetivo
        self.obj = obj

        # Colunas
        self.rows = []
        # Restricoes
        self.cons = []

    # Adicionando a lista de restricoes a tabela
    def adicionar_restricao(self, sinal, expressao, valor):
        # Primeiro vamos concatena-la
        self.rows.append(expressao)
        self.cons.append(valor)


if __name__ == '__main__':

    """
    max z = 2x + 3y + 2z
    st
    2x + y + z <= 4
    x + 2y + z <= 7
    z          <= 5
    x,y,z >= 0
    """
    
    tabela = Simplex(Tipo.MAX, [2,3,2])
    tabela.adicionar_restricao(Sinal.MENOR_IGUAL, [2,1,1], 4)
    tabela.adicionar_restricao(Sinal.MENOR_IGUAL, [1,2,1], 7)
    tabela.adicionar_restricao(Sinal.MENOR_IGUAL, [0,0,1], 5)
