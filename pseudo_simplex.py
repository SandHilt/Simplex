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
    # Localizacao no array do tipo de restricao
    __TIPO_RESTRICAO = 0

    def __init__(self, tipo_fo, obj):
        # Funcao objetivo
        self.obj = [tipo_fo] + obj

        # Colunas
        self.rows = []
        # Restricoes
        self.cons = []

        # Variaveis de folga
        self.__folga = 0

        self.base = []

    # Adicionando a lista de restricoes a tabela
    def adicionar_restricao(self, sinal, expressao, valor):
        # Primeiro vamos concatena-la
        self.rows.append( [sinal] + expressao )
        self.cons.append( valor )
        self.base = np.zeros(len(self.base) + 1)
        
    # Muda toda funcao de MAX para MIN
    def __tipo_funcao_objetivo(self):
        if(self.obj[self.__TIPO_RESTRICAO] == Tipo.MAX):
            self.obj = np.dot(self.obj, -1)
            self.obj[self.__TIPO_RESTRICAO] = Tipo.MIN

    # Muda toda restricao de MENOR_IGUAL ou MAIOR_IGUAL para IGUAL
    def __tipo_restricoes(self):
        for restricao in self.rows:
            # No caso se for menor ou igual
            if(restricao[self.__TIPO_RESTRICAO] == Sinal.MENOR_IGUAL):
                self.__folga += 1

                self.obj += [0]
                for res in self.rows:
                    res += [0]
                restricao[len(restricao)-1] = 1
                restricao[self.__TIPO_RESTRICAO] = Sinal.IGUAL
    
    def __unir_com_rhs(self):
        for i in range(len(self.rows)):
            self.rows[i] += [self.cons[i]]

    # Mostra a situacao atual da matrix
    def mostrar_situacao(self):
        tipo = 'max' if self.obj[self.__TIPO_RESTRICAO] == Tipo.MAX else 'min'
        print '\n', tipo, self.obj[1:]
        for row in self.rows:
            print row[1:]

    def resolver(self):

        print '\nAntes de comecar'
        self.mostrar_situacao()

        print '\nMudando a funcao objetivo'
        self.__tipo_funcao_objetivo()
        self.mostrar_situacao()

        print '\nMudando as restricoes para a forma padrao'
        self.__tipo_restricoes()
        self.mostrar_situacao()

        print '\nUnindo com o resultado'
        self.__unir_com_rhs()        
        self.mostrar_situacao()

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
    tabela.resolver()
