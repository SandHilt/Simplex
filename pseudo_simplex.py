import numpy as np
import matplotlib as mp
import timeit

# Testando para ver se tem ou nao o modulo
try:
    from tabulate import tabulate as tb
    saida_2 = True
except ImportError:
    saida_2 = False

class Problema:
    PRIMAL = 1
    DUAL = -1

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

    def __init__(self, tipo_fo, obj, orientacao_problema=Problema.PRIMAL):
        # Funcao objetivo
        self.obj = [tipo_fo] + obj + [0]

        # Colunas / Restricoes
        self.rows = []

        # Variaveis de folga
        self.__folga = []

        # Variaveis artificiais
        self.__art = []

        # z_0 para funcao objetivo artificial
        self.__z_0 = []

        # base
        self.base = []

        # Orientacao do Problema
        self.orientacao_problema = orientacao_problema

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

        print 'Vamos criar um base inicial:'

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
                print 'Colocando', 'x' + `self.numero_variavel`, 'na base.'
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

                # Colocando esse numero na base
                print 'Colocando', 'x' + `self.numero_variavel`, 'na base.'
                self.base.append(self.numero_variavel)

                restricao[self.__TIPO_RESTRICAO] = Sinal.IGUAL

            # No caso de for maior ou igual, ou seja, de duas fases
            elif sinal == Sinal.MAIOR_IGUAL:
                self.__folga += [self.numero_variavel]
                self.__art += [self.numero_variavel + 1]

                # Adicionando a variavel artificial a base
                print 'Colocando', 'x' + `self.numero_variavel + 1`, 'na base.'
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

    # saida normal sem nenhum modulo adicional
    def saida_1(self, orientacao_problema, tipo, obj):
        print '\n', orientacao_problema, tipo, '\t', self.arrendondar(obj[0][1:])
        for i in range(len(obj)-1):
            print '\t', self.arrendondar(obj[i][1:])
        for row in self.rows:
            print '\t', self.arrendondar(row[1:])

    # saida com o tabulate, um modulo para a saida ficar legivel no terminal
    def saida_2(self, orientacao_problema, tipo, obj):
        pretty_row = []
        for row in self.rows:
            pretty_row.append(row[1:])

        pretty_obj = []
        for fo in obj:
            pretty_obj.append(fo[1:])

        # tipo + tabela + formato da tabela + headers
        print '\n', orientacao_problema, tipo,'\n', tb(np.round(pretty_obj + pretty_row,\
        self.__DIGITOS_SIGNIFICATIVOS), tablefmt='psql',\
        headers=['x' + `a` for a in range(1, len(obj[0][1:]))]+['rhs']),'\n'

    # Mostra a situacao atual da matriz
    def mostrar_situacao(self, pack=[], somente_funcao_objetivo_original=True):

        if somente_funcao_objetivo_original == True:
            pack = [self.obj]
        else:
            # pack = np.array([pack.tolist()] + [self.obj], dtype=float)
            pack = [pack.tolist()] + [self.obj]

        tipo = 'min' if pack[0][self.__TIPO_RESTRICAO] == Tipo.MIN else 'max'
        orientacao = '(P)' if self.orientacao_problema == Problema.PRIMAL else '(D)'

        if saida_2 == False:
            self.saida_1(orientacao, tipo, pack)
        else:
            self.saida_2(orientacao, tipo, pack)

    # Procura pelo pivo
    def __pivo(self, obj, base=[]):
        # Mostrando a base atual
        print '\nBase atual', self.base

        # Variavel flag
        menor = float('Infinity')

        objetivo = obj.tolist()

        # Index inicial para escolher quem entra na base
        entra_base = -1

        # Caso eu tenha repassado uma base especial
        if len(base) == 0:
            # Encontra o indice da coluna com o valor mais negativo
            # na funcao objetivo  para saber quem entra na base
            try:
                entra_base = objetivo.index(min([a for a in objetivo[1:-1] if a<0]))
                print '\nNa funcao objetivo,\nesse eh o menor numero negativo:',\
                self.arrendondar(obj[entra_base]),'[coluna=' + `entra_base` + ']'
            # Caso nao haja ninguem para entrar na base,
            # entao estamos na solucao otima
            except(ValueError):
                print 'ja esta na solucao otima'
        else:
            entra_base = [a for a in objetivo[1:-1] for b in self.__art if a != b]

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
    def __escalonamento(self, obj=[], base=[]):
        print '\n5)Procurando o pivo'

        obj += [self.obj]
        somente_funcao_objetivo_original = True

        if len(obj) != 0:
            somente_funcao_objetivo_original = False

        criterio_parada = len([a for a in obj[0][1:-1] if a<0]) or len(base)

        # Alterando array para ndarray para fazer com que
        # cada linha seja do tipo float
        for i in range(len(obj)):
            obj[i] = np.array(obj[i], dtype=float)
        for restricao in self.rows:
            restricao = np.array(restricao, dtype=float)

        contador = 1
        while criterio_parada != 0:
            print '\n--------\n', `contador` + 'a', 'Interacao com pivo'
            contador += 1

            entra_base, sai_base = self.__pivo(obj[0], base)

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
            self.mostrar_situacao(obj[0], somente_funcao_objetivo_original)

            # Agora precisamos zerar a coluna do pivo nas restricoes
            # e depois na funcao objetivo
            print '\nb)Vamos zerar a coluna do pivo\n'

            linha_pivo = self.rows[sai_base]

            for i in range(len(self.rows)):
                restricao = self.rows[i]
                if i != sai_base:
                    self.rows[i] += np.dot(linha_pivo, -restricao[entra_base])
                    print '\nSomando a restricao', i + 1
                    self.mostrar_situacao(obj[0], somente_funcao_objetivo_original)

            print '\nSomando a linha do pivo a funcao objetivo'
            # Adicionando a linha pivo na funcao objetivo
            linha_pivo = linha_pivo[1:]
            for i in range(len(obj)):
                aux_obj = obj[i][1:]
                aux_obj += np.dot(linha_pivo, -aux_obj[entra_base-1])
                if i == len(obj)-1:
                    self.obj = np.array([0] + aux_obj.tolist(), dtype=float)
            self.mostrar_situacao(obj[0], somente_funcao_objetivo_original)

            # Trocando a base
            self.base[sai_base] = entra_base

            criterio_parada = len([a for a in obj[0][1:-1] if a<0])

    # Descobre se o prblema eh de uma ou duas fases
    def __teste_fases(self):
        # Listando as variaveis de folga
        for i in range(len(self.rows)):
            for folga in self.__folga:
                if abs(self.rows[i][folga]) == 1:
                    print 'A restricao', i+1, 'possui',\
                    'x' + `folga`, 'como variavel de folga.'

        # Se houver variavel artificial
        # Preciso fazer a primeira fase das duas
        # ja que a segunda fase eh o mesmo processo
        if len(self.__art) > 0:
            print '\n', 'O problema eh de duas fases.'

            self.__z_0 = np.zeros(2 + self.numero_variavel, dtype=float)
            print 'Mostrando nova funcao objetivo:'
            for art in self.__art:
                self.__z_0[art] = 1

            self.mostrar_situacao(self.__z_0, False)

            # Vamos procurar onde esta as restricoes
            # de cada variavel artificial
            for i in range(len(self.rows)):
                for art in self.__art:
                    if self.rows[i][art] == 1:
                        print 'A restricao', i+1, 'possui',\
                        'x' + `art`, 'como variavel artificial.'
                        aux = self.rows[i]
                        aux = np.dot(aux, -1).tolist()
                        self.__z_0 += aux

            print '\nAlterando os valores em suas respectivas restricoes temos:'
            self.mostrar_situacao(self.__z_0, False)
            print 'Agora vamos trabalhar com ela...'
            self.__escalonamento([self.__z_0])

            variaveis_art_basicas = [a for a in self.base for b in self.__art if a == b]

            print 'Chegamos em uma solucao otima\npara a primeira fase com base:', self.base, '\n'

            if len(variaveis_art_basicas) != 0:
                print 'Temos variaveis artificiais como base, precisamos elimina-las.'
                self.__escalonamento([self.__z_0], base=variaveis_art_basicas)
            else:
                print 'Nao ha variaveis artificiais como base, vamos continuar.\n'
                print 'E vamos eliminar as variaveis artificiais.', self.__art

                print self.obj
                self.obj = np.delete(self.obj, self.__art)
                print self.obj

                for i in range(len(self.rows)):
                    print '\n', 'restricao', i+1, self.rows[i]
                    self.rows[i] = np.delete(self.rows[i], self.__art)
                    print 'restricao', i+1, self.rows[i]

            print 'Agora vamos para a segunda fase.'
            self.mostrar_situacao()
            self.__escalonamento()
        else:
            print '\nO problema eh de uma fase.'
            self.__escalonamento()

    def resolver(self):
        print '\n1)Antes de comecar'
        self.mostrar_situacao()

        print '\n2)Mudando a funcao objetivo'
        self.__tipo_funcao_objetivo()
        self.mostrar_situacao()

        print '\n3)Mudando as restricoes para a forma padrao', '\n'
        self.__tipo_restricoes()
        self.mostrar_situacao()

        print '\n4)Verificando se eh de duas fases\n'
        self.__teste_fases()

        print '\n6)Resolucao'
        print '\nZ', '=', self.obj[-1]
        for i, res in enumerate(self.rows):
            print 'x' + `self.base[i]`,'=', res[-1]

def testes():
    # Problema de uma fase
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

    # Problema de duas fases
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

if __name__ == '__main__':

    numero_testes = 1
    tempo = round(timeit.timeit(testes, number=numero_testes), 2)
    print '\nTempo:', tempo ,'s em', numero_testes, 'teste(s).'
