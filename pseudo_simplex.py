import numpy as np
import matplotlib as mp
from tabulate import tabulate as tb

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

    # Digitos significativos para usar na precisao das saidas
    __DIGITOS_SIGNIFICATIVOS = 3

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

    def arrendondar(self, valor):
        return np.round(valor, self.__DIGITOS_SIGNIFICATIVOS)

    # Adicionando a lista de restricoes a tabela
    def adicionar_restricao(self, sinal, expressao, valor):
        # Primeiro vamos concatena-la
        self.rows.append([sinal] + expressao)
        self.cons.append(valor)

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
        self.obj += [0]

    # Coloca a saida como um modo convencional de ver
    # tipo_otimizacao = para saber se os coeficientes sao do tipo MAX ou MIN
    # final = se
    def __formatar_saida(self, arr, tipo_otimizacao=None, final=False, rhs=True):
        saida = '\t'

        if final == False:
            if tipo_otimizacao != None:
                saida = tipo_otimizacao + '\t'

            for index, coeficiente in enumerate(arr):
                # Estou na funcao objetivo e este eh o ultimo coeficiente
                if tipo_otimizacao != None and index+1 == len(arr) and rhs == True:
                    saida += '=' + `coeficiente`
                    continue
                cf = `self.arrendondar(coeficiente)`
                if coeficiente == 1:
                    cf = ''
                if coeficiente >= 0 and index != 0:
                    cf = '+' + cf
                saida += cf + 'x_' + `index + 1`
        else:
            for i in range(len(arr)):
                if i != 0:
                    saida += ','
                saida += 'x_' + `i+1`
            saida += '>= 0'

        return saida


    def saida_1(self, tipo):
        print '\n', tipo, '\t', self.arrendondar(self.obj[1:])
        for row in self.rows:
            print '\t', self.arrendondar(row[1:])

    def saida_2(self, tipo, rhs):
        print self.__formatar_saida(self.obj[1:], tipo, rhs=rhs)
        for row in self.rows:
            print self.__formatar_saida(row[1:], rhs=rhs)
        print self.__formatar_saida(self.obj[1:], final=True)

    # saida com o tabulate, um modulo para a saida ficar legivel no terminal
    def saida_3(self, tipo):
        pretty_row = []

        for row in self.rows:
            pretty_row.append(row[1:])

        print '\n',tipo,'\n', tb(np.round([self.obj[1:]] + pretty_row,\
        self.__DIGITOS_SIGNIFICATIVOS), tablefmt='psql'),'\n'

    # Mostra a situacao atual da matriz
    def mostrar_situacao(self, rhs=True):
        tipo = 'min' if self.obj[self.__TIPO_RESTRICAO] == Tipo.MIN else 'max'
        self.saida_3(tipo)

    # Procura pelo pivo
    def __pivo(self):
        # Mostrando a base atual
        print '\nBase atual',self.base

        # Variavel flag
        menor = float('Infinity')

        objetivo = self.obj.tolist()

        # Index inicial para escolher quem entra na base
        entra_base = -1

        # Encontra o indice da coluna com o valor mais negativo
        # na funcao objetivo  para saber quem entra na base
        try:
            entra_base = objetivo.index(min([a for a in objetivo[1:] if a<0]))
            print '\nNa funcao objetivo,\nesse eh o menor numero negativo:',\
            self.arrendondar(self.obj[entra_base]),'[coluna=' + `entra_base` + ']'
        # Caso nao haja ninguem para entrar na base,
        # entao estamos na solucao otima
        except(ValueError):
            print 'ja esta na solucao otima'

        # Index inicial para escolher quem sai da base
        sai_base = -1

        if entra_base != -1:
            print '\nEsse que entra: x' + `entra_base`, '\n'
            # Vamos procurar quem sai da base
            for index, restricao in enumerate(self.rows):
                # Exclui divisoes por zero
                if restricao[entra_base] > 0:
                    # Divisao entre o resultado da restricao
                    # e a vitima para ser o pivo
                    razao = self.arrendondar(restricao[-1] / float(restricao[entra_base]))
                    print 'Na restricao', `index+1` + ', com base x' + `self.base[index]` + ',',\
                    'a razao de', self.arrendondar(restricao[-1]), '/',\
                    self.arrendondar(restricao[entra_base]),'=',razao

                    # Elimina numeros negativos da escolha do pivo
                    if razao <= 0:
                        continue
                    elif razao < menor:
                        menor = razao
                        sai_base = index
                else:
                    print 'Na restricao', `index+1` + ', com base x' + `self.base[index]` + ',',\
                    'o numero eh nulo, negativo ou indeterminado:',\
                    self.arrendondar(restricao[-1]), '/', self.arrendondar(restricao[entra_base])
            if menor == float('Infinity'):
                print '\nproblema eh inviavel'
            else:
                print '\nEsse que sai: x' + `self.base[sai_base]` + '\n'

        return entra_base, sai_base

    # Aqui vai procurar o pivo e fazer os escalonamentos necessarios
    def __escalonamento(self):
        criterio_parada = len([a for a in self.obj[1:-1] if a<0])

        # Alterando array para ndarray para fazer com que
        # cada linha seja do tipo float
        self.obj = np.array(self.obj, dtype=float)
        for restricao in self.rows:
            restricao = np.array(restricao, dtype=float)

        while criterio_parada != 0:
            entra_base, sai_base = self.__pivo()

            # Significa que nao foi possivel achar um novo pivo
            if(entra_base == -1 or sai_base == -1):
                break

            # O pivo esta aqui
            pivo = float(self.rows[sai_base][entra_base])

            print 'O pivo dessa interacao eh:', self.arrendondar(pivo), \
            '[linha=' + `sai_base + 1` + ', coluna=' + `entra_base` + ']\n'

            print 'a)Dividindo a coluna pivo'
            # Agora vamos dividir a linha toda pelo proprio pivo
            self.rows[sai_base] = np.dot(self.rows[sai_base], 1 / pivo)
            self.mostrar_situacao()

            # Agora precisamos zerar a coluna do pivo nas restricoes
            # e depois na funcao objetivo
            print '\n\nb)Vamos zerar a coluna do pivo'

            linha_pivo = self.rows[sai_base]

            for i in range(len(self.rows)):
                restricao = self.rows[i]
                if i != sai_base:
                    self.rows[i] += np.dot(linha_pivo, -restricao[entra_base])
                    self.mostrar_situacao()

            # Adicionando a linha pivo na funcao objetivo
            linha_pivo = linha_pivo[1:]
            aux_obj = self.obj[1:]
            aux_obj += np.dot(linha_pivo, -aux_obj[entra_base-1])
            self.obj = np.array([0] + aux_obj.tolist(), dtype=float)
            self.mostrar_situacao()

            # Trocando a base
            self.base[sai_base] = entra_base

            criterio_parada = len([a for a in self.obj[1:-1] if a<0])

    def resolver(self):
        print '\n1)Antes de comecar'
        self.mostrar_situacao(False)

        print '\n2)Mudando a funcao objetivo'
        self.__tipo_funcao_objetivo()
        self.mostrar_situacao(False)

        print '\n3)Mudando as restricoes para a forma padrao'
        self.__tipo_restricoes()
        self.mostrar_situacao(False)

        print '\n4)Unindo com o resultado'
        self.__unir_com_rhs()
        self.mostrar_situacao()

        print '\n5)Procurando o pivo'
        self.__escalonamento()

        print '\n6)Resolucao'
        print '\nZ=', self.obj[-1]
        for i, res in enumerate(self.rows):
            print 'x' + `self.base[i]` + "=", res[-1]

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
