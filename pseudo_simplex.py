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

    # Total de numero de variaveis
    numero_variavel = 0

    def __init__(self, tipo_fo, obj):
        # Funcao objetivo
        self.obj = [tipo_fo] + obj + [0]

        # Colunas / Restricoes
        self.rows = []

        # Variaveis de folga
        self.__folga = []

        # Variaveis artificiais
        self.__art = []

        self.__obj_art = []

        self.base = []

    def arrendondar(self, valor):
        return np.round(valor, self.__DIGITOS_SIGNIFICATIVOS)

    # Adicionando a lista de restricoes a tabela
    def adicionar_restricao(self, sinal, expressao, valor):
        # Primeiro vamos concatena-la
        self.rows.append([sinal] + expressao + [valor])

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
        # Index do numero atual da variavel adicional
        # Deve ser decrescido -1 pois no inicio tem
        # o tipo da otimizacao MAX ou MIN e ainda
        # nao esta concatenado com rhs (valores)
        self.numero_variavel = len(self.obj) - 2

        for idx, restricao in enumerate(self.rows):
            sinal = restricao[self.__TIPO_RESTRICAO]
            self.numero_variavel += 1

            # Caso tenha numero negativo do lado direito
            if restricao[-1] < 0:
                self.rows[idx] = np.dot(restricao, -1).tolist()

            # No caso se for igual, entao aplicamos as variaveis
            # artificiais
            if sinal == Sinal.IGUAL:
                self.__art += [self.numero_variavel]
                self.base.append(self.numero_variavel)
                self.obj[-1:-1] = [0]

                # Adicionando zero as restricoes
                for row in self.rows:
                        row[-1:-1] = [0]

                # Adicionando coeficiente a restricao
                self.rows[idx][-2] = 1
            # No caso de for menor ou igual, ou seja, uma fase
            elif sinal == Sinal.MENOR_IGUAL:
                self.__folga += [self.numero_variavel]
                self.obj[-1:-1] = [0]

                # Adicionando zero as restricoes
                for res in self.rows:
                    res[-1:-1] = [0]

                # Adicionando coeficiente a restricao
                restricao[-2] = 1

                # Criando uma base inicial
                self.base.append(self.numero_variavel)

                restricao[self.__TIPO_RESTRICAO] = Sinal.IGUAL

            # No caso de for maior ou igual, ou seja, de duas fases
            elif sinal == Sinal.MAIOR_IGUAL:
                self.__folga += [self.numero_variavel]
                self.__art += [self.numero_variavel + 1]

                # adicionando a variavel artificial a base
                self.base.append(self.numero_variavel + 1)

                # Como a cada interacao ele ja incrementa
                # eu aumento soh mais uma porque sao duas variaveis
                self.numero_variavel += 1

                # Adicionando dois zeros a funcao objetivo
                self.obj[-1:-1] = [0, 0]

                for res in self.rows:
                    res[-1:-1] = [0, 0]

                restricao[-3] = -1
                restricao[-2] = 1
                restricao[self.__TIPO_RESTRICAO] = Sinal.IGUAL

    def saida_1(self, tipo):
        print '\n', tipo, '\t', self.arrendondar(self.obj[1:])
        for row in self.rows:
            print '\t', self.arrendondar(row[1:])

    # saida com o tabulate, um modulo para a saida ficar legivel no terminal
    def saida_2(self, tipo):
        pretty_row = []

        for row in self.rows:
            pretty_row.append(row[1:])

        # tipo + tabela + formato da tabela + headers
        print '\n',tipo,'\n', tb(np.round([self.obj[1:]] + pretty_row,\
        self.__DIGITOS_SIGNIFICATIVOS), tablefmt='psql',\
        headers=['x' + `a` for a in range(1, len(self.obj[1:]))]+['rhs']),'\n'

    # Mostra a situacao atual da matriz
    def mostrar_situacao(self):
        tipo = 'min' if self.obj[self.__TIPO_RESTRICAO] == Tipo.MIN else 'max'

        # self.saida_1(tipo)
        self.saida_2(tipo)

    # Procura pelo pivo
    def __pivo(self):
        # Mostrando a base atual
        print '\nBase atual', self.base

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
        # Se houver variavel artificial
        # Preciso fazer a primeira fase das duas
        # ja que a segunda fase eh o mesmo processo
        if len(self.__art) > 0:
            # print self.__art
            for restricao in self.rows:
                for art in self.__art:
                    pass
                    # print restricao, art, restricao[art-1]



        criterio_parada = len([a for a in self.obj[1:-1] if a<0])

        # Alterando array para ndarray para fazer com que
        # cada linha seja do tipo float
        self.obj = np.array(self.obj, dtype=float)
        for restricao in self.rows:
            restricao = np.array(restricao, dtype=float)

        contador = 1
        while criterio_parada != 0:
            print '\n--------\n', `contador` + 'a', 'Interacao com pivo'
            contador += 1

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
            print '\nb)Vamos zerar a coluna do pivo\n'

            linha_pivo = self.rows[sai_base]

            for i in range(len(self.rows)):
                restricao = self.rows[i]
                if i != sai_base:
                    self.rows[i] += np.dot(linha_pivo, -restricao[entra_base])
                    print '\nSomando a restricao', i + 1
                    self.mostrar_situacao()

            # Adicionando a linha pivo na funcao objetivo
            linha_pivo = linha_pivo[1:]
            aux_obj = self.obj[1:]
            aux_obj += np.dot(linha_pivo, -aux_obj[entra_base-1])
            self.obj = np.array([0] + aux_obj.tolist(), dtype=float)
            print '\nSomando a linha do pivo a funcao objetivo'
            self.mostrar_situacao()

            # Trocando a base
            self.base[sai_base] = entra_base

            criterio_parada = len([a for a in self.obj[1:-1] if a<0])

    def resolver(self):
        print '\n1)Antes de comecar'
        self.mostrar_situacao()

        print '\n2)Mudando a funcao objetivo'
        self.__tipo_funcao_objetivo()
        self.mostrar_situacao()

        print '\n3)Mudando as restricoes para a forma padrao'
        self.__tipo_restricoes()
        self.mostrar_situacao()

        print '\n4)Procurando o pivo'
        self.__escalonamento()

        print '\n5)Resolucao'
        print '\nZ', '=', self.obj[-1]
        for i, res in enumerate(self.rows):
            print 'x' + `self.base[i]`,'=', res[-1]

if __name__ == '__main__':

    """
    max z = 2x + 3y + 2z
    st
    2x + y + z <= 4
    x + 2y + z <= 7
    z          <= 5
    x,y,z >= 0
    """
    # tabela = Simplex(Tipo.MAX, [2, 3, 2])
    # tabela.adicionar_restricao(Sinal.MENOR_IGUAL, [2, 1, 1], 4)
    # tabela.adicionar_restricao(Sinal.MENOR_IGUAL, [1, 2, 1], 7)
    # tabela.adicionar_restricao(Sinal.MENOR_IGUAL, [0, 0, 1], 5)
    # tabela.resolver()

    """
    max z = 6x1 - x2
    st
    4x1 + x2    <= 21
    2x1 + 3x2   >= 13
    x1 - x2      = -1
    x1,x2 >= 0
    """

    tabela = Simplex(Tipo.MAX, [6, -1])
    tabela.adicionar_restricao(Sinal.MENOR_IGUAL, [4, 1], 21)
    tabela.adicionar_restricao(Sinal.MAIOR_IGUAL, [2, 3], 13)
    tabela.adicionar_restricao(Sinal.IGUAL, [1, -1], -1)
    tabela.resolver()
