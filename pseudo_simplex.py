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
    # Localizacao no array do tipo de restricao e o tipo de otimizacao
    __TIPO_RESTRICAO = 0

    def __init__(self, tipo_fo, obj):
        # Funcao objetivo
        self.obj = [tipo_fo] + obj

        # Colunas / Restricoes
        self.rows = []
        # Restricoes
        self.cons = []

        # Variaveis de folga
        self.__folga = 0

        # Variaveis artificiais
        self.__art = 0

        self.__obj_art = []

        self.base = []

    # Adicionando a lista de restricoes a tabela
    def adicionar_restricao(self, sinal, expressao, valor):
        # Primeiro vamos concatena-la
        self.rows.append([sinal] + expressao)
        self.cons.append(valor)
        # self.base += [0]

    # Transforma a funcao MAX para MIN
    def __tipo_funcao_objetivo(self):
        if(self.obj[self.__TIPO_RESTRICAO] == Tipo.MAX):
            # numpy.dot converte para ndarray
            self.obj = np.dot(self.obj, -1)
            # voltando a ser um array
            self.obj = self.obj.tolist()
            self.obj[self.__TIPO_RESTRICAO] = Tipo.MIN

    # Transforma as desiguadades em igualdades
    def __tipo_restricoes(self):
        for restricao in self.rows:
            sinal = restricao[self.__TIPO_RESTRICAO]

            # No caso de for menor ou igual, ou seja, uma fase
            if sinal == Sinal.MENOR_IGUAL or sinal == Sinal.IGUAL:
                self.__folga += 1

                self.obj += [0]

                # Adicionando zero as restricoes
                for res in self.rows:
                    res += [0]

                # Adicionando coeficiente a restricao
                restricao[len(restricao)-1] = 1

                # Criando uma base inicial
                self.base.append(len(restricao)-1)

                if sinal == Sinal.MENOR_IGUAL:
                    restricao[self.__TIPO_RESTRICAO] = Sinal.IGUAL

            # No caso de for maior ou igual, ou seja, de duas fases
            elif sinal == Sinal.MAIOR_IGUAL:
                self.__folga += 1
                self.__art += 1

                self.obj += [0, 0]

                for res in self.rows:
                    res += [0, 0]
                restricao[len(restricao)-2] = -1
                restricao[len(restricao)-1] = 1
                restricao[self.__TIPO_RESTRICAO] = Sinal.IGUAL
                self.__obj_art = np.zeros(len(self.__obj_art) + 1)

    # Unindo a todas as restricoes os seus respectivos resultados
    def __unir_com_rhs(self):
        for i in range(len(self.rows)):
            self.rows[i] += [self.cons[i]]

    # Coloca a saida como um modo convencional de ver
    def __formatar_saida(self, arr, tipo_otimizacao=None, final=False):
        saida = '\t'

        if final == False:
            if tipo_otimizacao != None:
                saida = tipo_otimizacao + '\t'

            for index, coeficiente in enumerate(arr):
                cf = '' + `coeficiente`
                if coeficiente >= 0 and index != 0:
                    cf = '+' + cf
                saida += cf + 'x' + `index + 1`

        else:
            for i in range(len(arr)):
                if i != 0:
                    saida += ','
                saida += 'x' + `i+1`
            saida += '>= 0'

        return saida

    # Mostra a situacao atual da matriz
    def mostrar_situacao(self):
        tipo = 'max' if self.obj[self.__TIPO_RESTRICAO] == Tipo.MAX else 'min'

        print '\n', tipo, '\t', self.obj[1:]
        # print self.__formatar_saida(self.obj[1:], tipo)

        for row in self.rows:
            print '\t', row[1:]
            # print self.__formatar_saida(row[1:])

        # print self.__formatar_saida(self.obj[1:], final=True)

    # Procura pelo pivo
    def __pivo(self):
        # Variavel flag
        menor = float('Infinity')

        objetivo = self.obj.tolist()

        # Encontra o indice da coluna com o valor mais negativo
        # na funcao objetivo  para saber quem entra na base
        entra_base = objetivo.index(min(objetivo[1:]))

        # Index inicial para escolher quem sai da base
        sai_base = -1

        # O valor precisa ser negativo
        if self.obj[entra_base] < 0:
            # Vamos procurar quem sai da base
            print '\nEsse que entra'
            print 'x' + `entra_base`
            for index, restricao in enumerate(self.rows):
                # Exclui divisoes por zero
                if restricao[entra_base] != 0:
                    # Divisao entre o resultado da restricao
                    # e a vitima para ser o pivo
                    razao = restricao[-1] / float(restricao[entra_base])

                    # Elimina numeros negativos da escolha do pivo
                    if razao < 0:
                        continue
                    elif razao < menor:
                        menor = razao
                        sai_base = index

            if menor == float('Infinity'):
                print '\nproblema inviavel'
            else:
                print '\nEsse que sai'
                print 'x' + `self.base[sai_base]` + '\n'

            return entra_base, sai_base
        # Caso nao haja ninguem para entrar na base,
        # entao estamos na solucao otima
        else:
            print 'ja esta na solucao otima'

    # Aqui vai procurar o pivo e fazer os escalonamentos necessarios
    def __escalonamento(self):
        criterio_parada = len([a for a in self.obj[1:] if a<0])

        # Alterando array para ndarray
        self.obj = np.array(self.obj, dtype=float)
        for restricao in self.rows:
            restricao = np.array(restricao, dtype=float)

        while criterio_parada != 0:
            entra_base, sai_base = self.__pivo()

            # O pivo esta aqui
            pivo = float(self.rows[sai_base][entra_base])

            print 'O pivo dessa interacao eh: ', pivo

            # Agora vamos dividir a linha toda pelo proprio pivo
            self.rows[sai_base] = np.dot(self.rows[sai_base], 1 / pivo)

            self.mostrar_situacao()


            print 'Vamos zerar a coluna do pivo'
            # Agora precisamos zerar a coluna do pivo nas restricoes
            # e depois na funcao objetivo
            for i in range(len(self.rows)):
                item = self.rows[i]
                if i != sai_base:
                    self.rows[i] += np.dot(self.rows[sai_base], -item[entra_base])

            self.base[sai_base] = entra_base

            criterio_parada -= 1

    def resolver(self):
        print '\n1)Antes de comecar'
        self.mostrar_situacao()

        print '\n2)Mudando a funcao objetivo'
        self.__tipo_funcao_objetivo()
        self.mostrar_situacao()

        print '\n3)Mudando as restricoes para a forma padrao'
        self.__tipo_restricoes()
        self.mostrar_situacao()

        print '\n4)Unindo com o resultado'
        self.__unir_com_rhs()
        self.mostrar_situacao()

        print '\n5)Base inicial'
        print self.base

        print '\n6)Procurando o pivo'
        self.__escalonamento()

if __name__ == '__main__':

    """
    max z = 2x + 3y + 2z
    st
    2x + y + z <= 4
    x + 2y + z <= 7
    z          <= 5
    x,y,z >= 0
    """
    tabela = Simplex(Tipo.MAX, [2, 3, 2])
    tabela.adicionar_restricao(Sinal.MENOR_IGUAL, [2, 1, 1], 4)
    tabela.adicionar_restricao(Sinal.MENOR_IGUAL, [1, 2, 1], 7)
    tabela.adicionar_restricao(Sinal.MENOR_IGUAL, [0, 0, 1], 5)
    tabela.resolver()
