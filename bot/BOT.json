# Links interessantes e úteis: 
#   https://github.com/python-telegram-bot/python-telegram-bot
#   https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-–-Your-first-Bot
#   https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/README.md
#   https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot.py
#   https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
#   https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot2.py

# pyBOT --toFinal

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging # Log para o Console

import string
import time
import json

tok = 'botToken'

# Configuração para o LOGGING
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, LISTING, PREPARING = range(3)

"""
    Início com Dados

"""

global listaPratos
global receitas
global receitaAtual


def carregarJson():
    global receitas
    with open( '..\JSON\glossario.json' , 'r' ) as arquivo:
        receitas = json.load( arquivo ) # no object-hook

def recomendacoes():
    import random
    nomesr = list()
    nomesr = list( receitas['receitas'] ) # Cria uma lista apenas com os nomes das receitas
    return (receitas['receitas'])[ random.choice( nomesr ) ] # Retorna a receita apenas ( uma lista )

def novos_pratos( bot , update , user_data ):
    # Em primeira instância, mostra uma receita aleatória
    receita = recomendacoes()
    update.message.reply_text( 'A receita de hoje é: ' + str(receita[1]) )

    bot.sendPhoto( chat_id = update.message.chat_id , photo = str(receita[2]) )

    update.message.reply_text( 'E esses são os ingredientes: ' )
    
    for i in receita[3]:
        update.message.reply_text( i )

    update.message.reply_text( 'Gostaria de ver como se faz?' )

    global receitaAtual
    receitaAtual = receita[1]
    
    return PREPARING

def montarListaPratos( nomereceitas ):
    global listaPratos
    listaPratos = ''

    for receita in nomereceitas:
        listaPratos = listaPratos + '|'

    listaPratos = listaPratos[:-1]
    
    

                                       # nome receita
def listarIngredientes( bot , update , user_data ):
    text = update.message.text
    user_data['choice'] = text
    del user_data['choice']

    r = ( (receitas['receitas'])[text]) # Container da receita
    
    # já tenho o nome
    # Preciso enviar ingrediente por ingrediente

    bot.sendPhoto( chat_id=update.message.chat_id, photo= str( r[2] ) )
    update.message.reply_text( text + ' se faz com os ingredientes: ' )

    # Envia ingrediente por ingrediente
    for ingrediente in r[ 3 ]:
        update.message.reply_text( ingrediente )

    global receitaAtual # Modifica a receita que está sendo mostrada ao usuário
    receitaAtual = text
    #montarListaPratos() # TEM QUE MONTAR ANTES->buscar_pratos

    # Manda a mensagem
    update.message.reply_text( 'Gostaria de ver como se prepara?' )
    return PREPARING

def listarPreparacao( bot , update ):
    # Pega a receitaAtual e manda os ingredientes
    update.message.reply_text( 'Recomendamos seguir estas instruções: ' )
    for passo in ( ( receitas['receitas'] ) )[ receitaAtual ] [ 4 ]:
        update.message.reply_text( passo )

    # Neste ponto, a conversa já pode ter sido encerrada, então
    cancel( bot, update )

"""
    O Próprio BOT
"""
def start( bot, update ):
    user = update.message.from_user # User ID
    comandLog( update, "iniciar" )
    #update.message.reply_text("Olá! Como posso ajudá-lo(a)?")

    resposta_teclado = [ [ 'Buscar Pratos', 'Procurar por Ingredientes', 'Recomendações' ] ]
    update.message.reply_text( '\nAgora, escolha a opção abaixo que melhor lhe satisfazer ou envie /cancelar para parar.\n\n' , reply_markup = ReplyKeyboardMarkup( resposta_teclado, one_time_keyboard = True ) )

    return CHOOSING

##
def buscar_pratos( bot, update, user_data ):
    text = update.message.text
    user_data['choice'] = text
    
    escolha_pratos = list()

    qtd_receitasBuscaPratos = 3

    for x in range( 1 , ( qtd_receitasBuscaPratos + 1 ) ):
        escolha_pratos.append( recomendacoes()[1] ) # Apenas o nome

    print( escolha_pratos )
    
    montarListaPratos( escolha_pratos )

    update.message.reply_text( '\nPor favor, escolha o prato que mais lhe agrada.\n', reply_markup = ReplyKeyboardMarkup( [ escolha_pratos ], one_time_keyboard = True ) )

    #return CHOOSING
    return LISTING
    
##

def cancel( bot , update ):
    #start( bot , update )
    return ConversationHandler.END

def parar( bot , update , user_data ):
    comandLog( update , "cancelar" )
    update.message.reply_text( "Sem problemas, volte quando quiser!" )
    user_data.clear()
    return ConversationHandler.END

def help( bot, update ):
    user = update.message.from_user # User ID
    comandLog( update, "ajuda" )
    update.message.reply_text("Este BOT proporciona uma nova experiência para buscar refeições e possibilita a busca de receitas através de ingredientes, recomendações e surpresas.\n"
                              "Você pode /iniciar para começar de novo ou /cancelar para parar.")

    return ConversationHandler.END


def comandLog( update, mensagem ):
    user = update.message.from_user
    logger.info( "USER: {} {} -> /{}".format( user.first_name, user.last_name, mensagem ) )

def error( bot, update, error):
    logger.warning('Update "%s" caused error "%s%"', update, error)

def main():
    updater = Updater( tok )

    dp = updater.dispatcher

    #dp.add_handler( CommandHandler("iniciar", start) )

    global listaPratos
    listaPratos = ''

    buscarPratosHandler = ConversationHandler(
        entry_points = [ CommandHandler( 'iniciar', start ) ],
        states = {
            CHOOSING: [ RegexHandler( '^(Buscar Pratos|Procurar Por Ingredientes)$',
                                      #resposta_normal,
                                      buscar_pratos,
                                      pass_user_data = True ),
                        RegexHandler( '^(Recomendações)$',
                                      novos_pratos,
                                      pass_user_data = True ),
                        CommandHandler( 'cancelar' , cancel )
                        ],
            LISTING:  [
                        RegexHandler( '(' + listaPratos + ')',
                                      listarIngredientes,
                                      pass_user_data = True ),
                        CommandHandler( 'cancelar' , cancel )
                        ],
            PREPARING: [
                        RegexHandler( '^(yes|sim|Sim|Yes)' ,
                                      listarPreparacao,
                                      pass_user_data = False ),
                        RegexHandler( '^(no|não|Não|No)' ,
                                      cancel,
                                      pass_user_data = False ),
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

    # Quando algo é tratado, o próximo não ocorre
    dp.add_handler( CommandHandler( "cancelar", cancel ) )
    dp.add_handler( MessageHandler(Filters.text, help) )
    
    
    dp.add_error_handler( error )

    updater.start_polling()
    logger.info( "BOT Iniciado, >polling" )

    updater.idle()

if __name__ == '__main__':
    #main() # Tem que carregar primeiro
    carregarJson()
    main()


