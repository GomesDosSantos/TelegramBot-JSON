# Links interessantes e úteis: 
#   https://github.com/python-telegram-bot/python-telegram-bot
#   https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-–-Your-first-Bot
#   https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/README.md
#   https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py
#   https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
#   https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot2.py


from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)

import logging # Log para o Console

import string
import json

tok = 'BOT-TOKEN'

# Configuração para o LOGGING
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, LISTING, PREPARING, SEARCHING , HELPING, PRONTORECEITAS = range(6)

"""
    Variáveis Globais

"""

global listaPratos
global receitas
global receitaAtual
global ingredientesBusca
global busca
global termino

global inlineMarkup


### Carregamento de dados do Sistema
def carregarJson():
    global receitas
    with open( 'C:\\Users\\Aluno\\Desktop\\o\\glossario.json' , 'r' ) as arquivo:
    #with open( 'C:\\Users\\bugot\\OneDrive - Fatec Centro Paula Souza\\3º Sem\\3 - IHC (Giuliano) ~Interação Humano-Computador\\2 Novo\\glossario.json' , 'r' ) as arquivo:
        receitas = json.load( arquivo ) # no object-hook


# Envio de mensagem em Negrito
def msgBold( bot , update , msg ):
    bot.sendMessage( chat_id=update.message.chat_id, parse_mode="HTML", text="<b>" + msg + "</b>" )
    

# Manda um nome de receita aleatório
def recomendacoes():
    import random
    
    nomesr = list()
    nomesr = list( receitas['receitas'] ) # Cria uma lista apenas com os nomes das receitas

    return (receitas['receitas'])[ random.choice( nomesr ) ] # Retorna a receita apenas ( uma lista )

# Monta o global ListaPratos
def montarListaPratos( nomereceitas ):
    global listaPratos
    listaPratos = ''

    # Não está fazendo NADA
    for receita in nomereceitas:
        listaPratos = receita + '|' + listaPratos

    listaPratos = listaPratos[:-1]
    

# ================= Novos Pratos ================ #

# Envia as informações de uma receita aleatória
def novos_pratos( bot , update , user_data ):
    # Em primeira instância, mostra uma receita aleatória
    receita = recomendacoes()
    update.message.reply_text( 'A receita de hoje é: ' + str(receita[1]) )

    bot.sendPhoto( chat_id = update.message.chat_id , photo = str(receita[2]) )

    update.message.reply_text( 'E estes são os ingredientes: ' )
    
    for i in receita[3]:
        update.message.reply_text( i )

    msgBold( bot , update , 'Gostaria de ver como se faz?' )
    
    # Atualização Variável Global
    global receitaAtual
    receitaAtual = receita[1]
    
    return PREPARING
    # Como se tornou Inline, não é necessário retornar para PREPARING

# Mostra as informações de uma receita pesquisa
                                       # nome receita
def listarIngredientes( bot , update , user_data ):
    text = update.message.text
    user_data['choice'] = text
    del user_data['choice']

    r = ( (receitas['receitas'])[text]) # Container da receita
    
    # já tenho o nome
    # Preciso enviar ingrediente por ingrediente
    bot.sendPhoto( chat_id=update.message.chat_id, photo= str( r[2] ) )
    # Envia a foto da receita
    update.message.reply_text( text + ' se faz com os ingredientes: ' )

    # Envia ingrediente por ingrediente
    for ingrediente in r[ 3 ]:
        update.message.reply_text( ingrediente )

    global receitaAtual # Modifica a receita que está sendo mostrada ao usuário
    receitaAtual = text
    
    # Manda a mensagem
    # https://core.telegram.org/bots/api#html-style
    msgBold( bot , update , "Gostaria de ver como se prepara?" )
    
    return PREPARING

# Lista a preparação de uma receita pesquisada
def listarPreparacao( bot , update ):

    ing =  ( ( receitas['receitas'] ) ) [ receitaAtual ][ 4 ]
    
    msgBold( bot , update , 'Recomendamos seguir estas instruções: ' )

    if len(ing) != 1 :
        for passo in ing:
            update.message.reply_text( passo )
    else:
        ing = ing[0].split( '.' )
        for passo in ing:
            if not passo: continue
            update.message.reply_text( passo + '.' )
    
    # Neste ponto, a conversa já pode ter sido encerrada, então
    cancel( bot, update )


def buscar_pratos( bot, update, user_data ):
    text = update.message.text
    user_data['choice'] = text

    del user_data['choice']

    escolha_pratos = list()

    qtd_receitasBuscaPratos = 4

    m = 0

    for x in range( 1 , ( qtd_receitasBuscaPratos + 1 ) ):
        escolha_pratos.append( recomendacoes()[1] ) # Apenas o nome

    montarListaPratos( escolha_pratos )

    update.message.reply_text( '\nPor favor, escolha o prato que mais lhe agrada.\n', reply_markup = ReplyKeyboardMarkup( [ escolha_pratos[:1] , escolha_pratos[1:] ], one_time_keyboard = True )

    return LISTING

#### =========================== Busca Por Ingredientes ============================= ####

def buscarIngredientes( bot , update ):
    # Vai inicilizar com o usuário a conversa
    # E pedir para enviar o primeiro ingrediente da lista

    import string

    # Frases
    m = [ 'Ok. Para buscarmos com  mais eficiência, gostaríamos que você mandasse ingrediente por ingrediente desse jeito:' ,
          '1kg Arroz', '100ml de Água' , 'Mande pelo chat o nome do ingrediente que você possui. Para terminar é só mandar /pronto.' ]

    for i in m:
        if i[0] in string.digits: # Se o primeiro caracter for algum número
            msgBold( bot , update , i )
        else:
            update.message.reply_text( i )
    
    return SEARCHING

##
def adicionarIngrediente( bot , update , user_data ):
    text = update.message.text
    user_data[ 'choice' ] = text

    del user_data[ 'choice' ]

    # Para a Busca Por Ingredientes
    global ingredientesBuscar # Lista de Ingredientes

    #  quantidade  :   nome
    i = text

    import string
  
    num = ''
    item = ''

    try:
        num = i.split() # Faço apenas um SPLIT
        item = num[1:]  # Tudo o que vem depois
        num = num[0]    # Tudo o que vem antes
    except:
        pass

    q = ''
    for letra in num:
        if letra in string.digits: # DIGITO, logo quantidade
            q = q + letra # Pega APENAS o numeral da mensagem

    o = ' '.join( item )

    ingredientesBuscar[ int(q) ] = o

    print( ingredientesBuscar )

    return SEARCHING

def pronto( bot , update ):

    import re

    # Limite de busca de receitas para tentar buscar o mais rápido possível
    # Caso seja necessário, é possível aumentar o limite para buscar mais receitas
    limite = 10
    c = 0
    l = 0
    
    # Lista de receitas
    receitas = list() # Receita aleatórias para buscar
    p = list()        # Receitas em que os ingredientes forão encontrados
    achou = False     # Status da busca
    
    while True:

        # adiciona x receitas a lista dependendo do limite
        for i in range( limite ):
            r = recomendacoes()
            if r not in receitas:
                receitas.append( r )
                i -= 1

        for receita in receitas:
            status = False
            # id - nome - img - list-indredientes - list-preparacao
            for ingrediente in receita[3]:
                ### BUSCA pelos ingredientes da receita
                for q, i in ingredientesBuscar.items():
                    m = re.search( r'('+str(q)+')?('+i+')' , ingrediente )
                    if m: # Achou correspondência
                        #print( ingrediente , ' achou ' )
                        if receita[1] not in p:
                            p.append( receita[1] )
                            status = True
                            c += 1
                    else:
                        #print( q, i, ingrediente )
                        l += 1
                if status:
                    break
                        

        if c >= 3 or len(p) >= 3:
            # Achou 3 receitas, já está bom
            break
        elif l >= 10:
            limite += 1
            receitas.clear()
            continue
        
    ######### fim while True

    update.message.reply_text( str(len(p)) + ' receitas forão encontradas!' )
    print( str(len(p)) + ' forão encontradas.' )

    print( p )

    global busca
    busca = list()
    
    # Montagem lista de receitas encontradas
    for i in range( len(p) ):
        busca.append( p[i] )

    # Agora é hoje de mostrar as receitas disponíveis ao usuário
    update.message.reply_text( 'Digite o nome da receita ou o número que você gostaria de ver: ' , reply_markup = ReplyKeyboardMarkup( [ busca[:len(busca)//3] , busca[len(busca)//3:] ], one_time_keyboard = True ) )

    for i in range( len(p) ):
        msgBold( bot , update , str( i + 1 ) + ': ' + p[i] )

    #montarListaPratos( p )

    return PRONTORECEITAS

#  Envia as informações de uma determinada receita, seja ela por número (id) da busca acima ou
# pelo nome da receita
def listarReceitaEncontrada( bot , update , user_data ):
    text = update.message.text
    user_data['choice'] = text
    del user_data['choice']

    import string
    import re

    #text -> Item enviado pelo usuário
    
    r = None
    num = ''
    v = False
    
    #if r.trim()
    # https://stackoverflow.com/questions/761804/how-do-i-trim-whitespace-from-a-python-string
    if text.strip() in string.digits:
        # Usuário inseriu o número e não o nome
        for n in text.strip():
            if n in string.digits:
                num += n
                v = True
    else: # Inserção peo nome
        r = ( (receitas['receitas'])[text]) # Container da receita

    if len(num) != 0:
        num = int(num)
        r = (receitas['receitas']) [ busca[num-1] ]
        
        #    receita inserida  nome_receita  lita de receitas
    else:
        r = ( (receitas['receitas']) [text] )
    
    # Envio as informações associadas a esta receita
    # Envia a foto da receita
    bot.sendPhoto( chat_id=update.message.chat_id, photo= str( r[2] ) )
    update.message.reply_text( busca[num-1] if v else text + ' pode-se fazer com os ingredientes: ' )
    # Envia ingrediente por ingrediente
    for ingrediente in r[ 3 ]:
        update.message.reply_text( ingrediente )

    msgBold( bot , update , 'Recomenda-se seguir estas instruções: ' )

    ing = r[4]
    
    # Envia a forma de preparo também
    if len(ing) != 1 :
        for passo in ing:
            update.message.reply_text( passo )
    else:
        ing = ing[0].split( '.' )
        for passo in ing:
            if not passo: continue
            update.message.reply_text( passo + '.' )

    update.message.reply_text( 'Se quiser ver outra das receitas encontradas é só digitar o nome dela ou o número correspondente!' )
    
    # Até cancelar ou sair
    return PRONTORECEITAS
  
##

# ========== Configurações do BOT ============ #

def start( bot, update ):
    user = update.message.from_user # User ID
    comandLog( update, "iniciar" )

    resposta_teclado = [ [ 'Buscar Pratos', 'Procurar Por Ingredientes', 'Recomendações' ] ]
    update.message.reply_text( '\nAgora, escolha a opção abaixo que melhor lhe satisfazer ou envie /cancelar para parar.\n\n' , reply_markup = ReplyKeyboardMarkup( resposta_teclado, one_time_keyboard = True ) )

    return CHOOSING
    
def cancel( bot , update ):    
    return ConversationHandler.END

# Terminar Conversa de forma mais simples
def terminarConversa( bot , update ):
    comandLog( update , "terminarConversa" )

    global termino # Iremos alterar o VALOR da variável globalmente

    if not termino: # Se estivermos na primeira tentativa de terminar a conversa
        update.message.reply_text( "Certeza? Nós ainda podemos continuar." )
        termino = True
    else: # Caso na segunda, já termina logo
        update.message.reply_text( "Sem problemas, volte quando quiser!!" )
        return ConversationHandler.END

    #### TROCAR POR INLINE
    
#
def parar( bot , update , user_data ):
    comandLog( update , "cancelar" )
    update.message.reply_text( "Sem problemas, volte quando quiser!" )
    user_data.clear()
    return ConversationHandler.END


# HELP novo 31/10-2018
# Mais conversação
# Comando de AJUDA que é acionado quando a conversa não foi iniciada ou algum comando inserido NÃO foi reconhecido ou é inexistente
def help( bot, update ):
    user = update.message.from_user # User ID
    comandLog( update, "ajuda" )

    m = [ "Quer ajuda? Então, primeiramente, seja Bem vindo ao receitasBot." , "Este BOT tem o intuito de proporcionar uma nova experiência para buscar refeições e também possibilita a busca de receitas através de ingredientes." ,
          "Você pode pedir alguma recomendação para nós que enviaremos algo especial para você pelo chat!" , "Se tiver alguma dúvida sobre os comandos, envie /comandos." ,
          "Caso alguma coisa esteja errada digite /erro." ]
    
    for n in m:
        update.message.reply_text( n )

    return ConversationHandler.END

# Listar Comandos disponíveis pelo BOT
def listarComandos( bot , update ):

    comandLog( update , 'listarComandos' )
    
    comandos = [ '/iniciar{:s} Inicia a conversa com o BOT. Use-o para buscar as receitas.' , '/cancelar{:s} Cancela o comando atual e te deixa livre pra começar de novo!' ,
                 '/ajuda{:s} Caso precise.' , '/comandos{:s} Lista todos os comandos disponíveis do BOT. Inclusive esse.' , '/erro{:s} Utilize quando encontrar algum erro e quiser contar pra gente.' ]

    for c in comandos:
        update.message.reply_text( c.format( ':' ) )

    update.message.reply_text( 'São esses os comandos disponíveis por agora.' )

    return ConversationHandler.END

###########################
# ========== Manipuladores de ERRO ============= #
def encErro( bot , update ):
    update.message.reply_text( 'Encontrou algum erro?' )
    update.message.reply_text( 'Pra facilitar, você pode apenas digitar no chat o que encontrou.' )
    
    return HELPING


def continuarAjuda( bot , update , user_data ):

    u = user_data
    user_data.clear()

    print( u )
    u = update.message.from_user

    # https://docs.python.org/3/library/datetime.html
    from datetime import date
    data = date.today()
                                                                                     #           USER NAME               DATA       MENSAGEM
    t = 'Erro encontrado por usuário.\nUSER: {:s}.\nData: {:}.\nTEXTO: {:s}'.format( u.first_name + ' ' + u.last_name , data , update.message.text )

    # https://docs.python.org/2/library/string.html
    # Melhor só não deixar o :s dentro de {}
    # Deste modo, o Python já determina uma padrão de separar por - (hífen)
    # Que é o que eu queria
    #with open( 'C:\\Users\\Aluno\\Desktop\\l\\log-error_{0[0]}-{0[1]}-{0[2]}.txt'.format( data.timetuple() ) , 'w' ) as a:
    with open( 'C:\\Users\\Aluno\\Desktop\\r\\log-error_{:}.txt'.format( data ) , 'w' ) as a:
        a.write( t )

    logger.info( 'Erro Encontrado por usuário. LOG Salvo em: log-error_{:}.txt'.format( data ) )
    update.message.reply_text( 'Muito obrigado por nos informar!' )
                              
    return ConversationHandler.END

####
# LOG no Console
def comandLog( update, mensagem ):
    user = update.message.from_user
    logger.info( "USER: {} {} -> /{}".format( user.first_name, user.last_name, mensagem ) )

def error( bot, update, error):
    logger.warning('Update "%s" caused error "%s%"', update, error)


##
# Inicializador principal do BOT
def main():
    updater = Updater( tok )

    dp = updater.dispatcher

    ## Variáveis global que precisam ser inicilizadas aqui
    # Para o Buscar por Pratos
    global listaPratos
    listaPratos = ''

    # Para a Busca Por Ingredientes
    global ingredientesBuscar
    global buscar
    ingredientesBuscar = dict()
    buscar = False
    
    # Para o término da conversa
    global termino
    termino = False

    global inlineMarkup
    inlineMarkup = True

    buscarPratosHandler = ConversationHandler(               #CommandHandler( 'ajuda' , help ) 
        entry_points = [ CommandHandler( 'iniciar', start ) , CommandHandler( 'erro' , encErro ) ], # Pontos de Entrada na conversa (31/10)
        states = {
            CHOOSING: [ RegexHandler( '^(Buscar Pratos)$',
                                      #resposta_normal,
                                      buscar_pratos,
                                      pass_user_data = True ),
                        RegexHandler( '^(Recomendações)$',
                                      novos_pratos,
                                      pass_user_data = True ),
                        RegexHandler( '(Procurar Por Ingredientes)' ,
                                      buscarIngredientes,
                                      pass_user_data = False ),
                        CommandHandler( 'cancelar' , terminarConversa )
                        ],
            LISTING:  [
                        RegexHandler( '(' + listaPratos + ')',
                                      listarIngredientes,
                                      pass_user_data = True ),
                        CommandHandler( 'cancelar' , cancel )
                        ],
            PREPARING: [
                        RegexHandler( '^([Ss]im|[Yy]es)' ,
                                      listarPreparacao,
                                      pass_user_data = False ),
                        RegexHandler( '^([Nn]ão|[Nn]|o)' ,
                                      cancel,
                                      pass_user_data = False ),
                        CommandHandler( 'cancelar' , cancel )
                        ],
            SEARCHING: [
                        RegexHandler( '\w+' ,
                                      adicionarIngrediente,
                                      pass_user_data = True ),
                        CommandHandler( 'pronto' , pronto ),
                        CommandHandler( 'cancelar' , terminarConversa )
                ],
            HELPING: [
                        RegexHandler( '\w+' ,
                                     continuarAjuda,
                                     pass_user_data = True ),
                        CommandHandler( 'cancelar' , cancel )
                        ],
            PRONTORECEITAS: [
                        #RegexHandler
                        RegexHandler( '\d|\w+' ,
                                      listarReceitaEncontrada,
                                      pass_user_data = True ),
                        CommandHandler( 'cancelar' , cancel )
                        ]
            #
            #
        },

        fallbacks = [
            RegexHandler( '^(\/cancelar)$', parar, pass_user_data = True ),
            CommandHandler( 'cancelar' , cancel ),
            RegexHandler( '^(a-Z)$', error, pass_user_data = True ),
            ]
    ) #Fim
    
    dp.add_handler( buscarPratosHandler )

    dp.add_handler( CommandHandler("ajuda", help) )

    dp.add_handler( CommandHandler( "comandos" , listarComandos) )
    dp.add_handler( CommandHandler( "erro" , encErro ) )

    dp.add_handler( CommandHandler( "cancelar", cancel ) )
    dp.add_handler( MessageHandler(Filters.text, help) )
    
    
    dp.add_error_handler( error )

    updater.start_polling()
    logger.info( "BOT Iniciado, >polling" )

    updater.idle()

# MAIN
if __name__ == '__main__':
    carregarJson()
    main()



