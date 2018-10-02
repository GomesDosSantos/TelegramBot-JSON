from bs4 import BeautifulSoup as sopa
import requests as web
import re
import json


global d_final


def buscarPagina( href ):
    pagina = web.get( href )
    return sopa( pagina.content , 'html.parser' )


def buscarIngredientesImg( receita ):
    pagina = buscarPagina( f'https://cybercook.uol.com.br{receita}' )
    imagem = pagina.find( 'img' , { 'class' : 'photo' } )
    imagem = imagem['src'] # Quero apenas o URL da foto

    ingredientes = pagina.find( 'ul' , { 'class' : 'ingredient-list grid-lg-12 grid-sm-12' } )
    # /\ Este contém uma lista de apenas os ingredientes
    preparacao = pagina.find( 'ol' , { 'class' : 'ingredient-list grid-lg-12 grid-sm-12' } )
    # /\ Contém uma lista de como preparar

    in_list = list() # Vai armazenar os ingredientes de forma limpa
    pr_list = list() # Vai armazenar os passos de preparo de forma limpa

    temp = list() # Lista Auxiliar Temporária
    # Limpa os itens para retornar todos eles padronizados
    aux = ingredientes.findAll( 'li' )
    for i in aux:
        for palavra in re.split( r'\s' , i.text ):
            # Algumas vezes aqui, teremos \n e caracteres sem valor
            if not len(palavra) <=  0:
                temp.append( palavra )
        if temp not in in_list: in_list.append( temp )
        temp = list() # Limpa a lista dessa rodada
        
    # Já foi para Ingredientes, agora para o Como Preparar
    temp = list() # Limpa a lista temporária
    aux = preparacao.findAll( 'li' )
    for i in aux:
        for palavra in re.split( r'\s' , i.text ):
            if not len(palavra) <= 1:
                temp.append( palavra )
        if temp not in pr_list: pr_list.append( temp )
        temp = list() # Limpa a lista dessa rodada

    # Transforma os itens formatados em, ao invés de uma lista de listas
    # Uma lista de Strings
    for s in in_list:
        aux = ' '.join(s)
        in_list[ in_list.index(s) ] = aux
    # Para ambos
    for s in pr_list:
        aux = ' '.join(s)
        pr_list[ pr_list.index(s) ] = aux


    # return tuple()
    # ( 'img_url' , [ingredientes] , [preparacao] )
    return ( imagem , in_list , pr_list )

def buscarReceitas( paginas ):

    links = dict()
    ls_dic = list()
    k = dict()
    for numero in range( 1, paginas+1 ):
        pagina = web.get( f"https://cybercook.uol.com.br/receitas/culinaria-brasileira?pagina={numero}" )
        pagina = sopa( pagina.content , 'html.parser' )
    
        conteudo = pagina.find( 'main' )
        conteudo = conteudo.findAll( 'a' )

        # { NOME : [ LINK , IMG_SRC ] }

        # O retorno da raspagem é
        # '\n\n\n\n\n\n\n
        # 'Nome_receita
        # '\n\n\n\n\n\n\n\n\n
        # Sendo assim, todo número par eu possuo um LINK e NOME válidos para usar
        con = 1
        
        for a in conteudo:
            if not con % 2 == 0:
                pass
            else:
                aux = list()
                for s in re.split( r'\s' , a.text ):
                    if not len(s) <= 1: # Vai pular todos os espaços em branco do retorno
                        aux.append( s ) # Vai adicionar somente as palavras
                k[ ' '.join(aux) ] = a.get('href')
            con += 1
        # /\ vai pegar todos os nomes de receitas e links respectivos
        k = removerInutilizaveis( k, numero + 1 )

        ls_dic.append( k )
        
    for dicionario in ls_dic:
        for key, value in dicionario.items():
            #if key not in links.keys(): Não é necessário perguntar
            links[ key ] = value
                
    return links

def gravarJson( dicionario ):
    caminho = '/home/guilherme/Área de Trabalho/Receitas_Bot/CyberCook/glossario.json'

    print( f'JSON salvo em: {caminho}\n' )
    
    with open( caminho, 'w' ) as arquivo_final:
        json.dump( { 'receitas' : dicionario } , arquivo_final )


def removerInutilizaveis( dicionario , iteracao ):
    # 1 -> pag_atual | última
    # 2 -> anterior | pag_atual | última
    aux = ( list( dicionario.items() ) )[: -3 if iteracao > 1 else -2 ]
    d = dict()
    for r in aux:
        d[ r[0] ] = r[1]
    return d

def buscaThread( lista , n ):

    global d_final # Vai modificar a variável GLOBAL
    i = n
    
    for item in lista:
        
        k, v = item[0], item[1]
        
        try:
            aux = buscarIngredientesImg( v )
            d_final[ k ] = [ i , k , aux[0] , aux[1] , aux[2] ]
            i += 1
        except:
            continue
        # Por que isso?
        # Algumas vezes, mesmo após executar o 'removerInutilizaveis' ainda resta
        # uns links inválidos que não se encaixam na raspagem de 'buscarIngredientesImg'
        # Então, para evitar ter que iterar sobre uma lista possivelmente grande do que
        # antes ( que era apenas uma parte -> removerInutilizaveis )
        # Durante a exceção, só pular
    

def iniciar():
    print( 'Iniciado.' )
    from threading import Thread
    import time
    t = time.time()

    # No final ficará assim
    # { RECEITAS : [
    #       receita1 : { id, nome , img_src , ingredientes[] , como_preparar[]},
    #       receita2 : { id, nome , img_src , ingredientes[] , como_preparar[]}
    # ]}

    # Vai buscar por receitas em 5 páginas no site
    links = buscarReceitas( 10 )

    id = 0 # IDs únicos para cada receita

    global d_final
    # Agora vamos escrever o código que irá organizar tudo e gravar em um JSON
    d_final = {} # Dicionário para armazenar as receitas

    # Divide a lista completa pela metade
    l1 = list( links.items() )[len(links)//2:]
    l2 = list( links.items() )[:len(links)//2]

    # Joga as partes em 2 threads
    thread1 = Thread( target = buscaThread, args = ( l1 , 0 ) )
    thread1.start()
    thread2 = Thread( target = buscaThread, args = ( l2 , len(links)//2 ) )
    thread2.start()


    thread1.join() # Espera ambos os Threads terminarem de operar
    thread2.join()
    
    gravarJson( d_final )
    print( 'Operação Finalizada.\nTempo total: {:f}'.format( time.time() - t ) )
    

if __name__ == "__main__":
    iniciar()

    
