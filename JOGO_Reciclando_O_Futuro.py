import math
from pygame.math import Vector2

import pygame, sys, random
from pygame import  mixer
import os


mixer.init()
pygame.init()


SCREEN_LARG = 1200
SCREEN_ALT = 820

screen = pygame.display.set_mode((SCREEN_LARG, SCREEN_ALT))
pygame.display.set_caption('Reciclando o Futuro')

#frames------------------------------------------------------------
clock = pygame.time.Clock()
FPS = 60

#variaveis do JOGO
main_menu = True
menu_state = "main"



#movimento e acao do Jogador----------------------------------------------------------------
cima = False
baixo = False
direita = False
esquerda = False



#imagens-----------------------------------------------------------------------------------
#BOTOES
#botoes MENU
start_img = pygame.image.load('botoes/1.png').convert_alpha()
creditos_img = pygame.image.load('botoes/3.png').convert_alpha()
sair_img = pygame.image.load('botoes/2.png').convert_alpha()
restart_img = pygame.image.load('botoes/5.png').convert_alpha()
voltar_img = pygame.image.load('botoes/4.png').convert_alpha()
como_jogar_img = pygame.image.load('botoes/7.png').convert_alpha()

#imagens MENU

BG_Menu = pygame.image.load('cenário/MENU.jpg')
BG_Creditos = pygame.image.load('cenário/Creditos.jpg').convert_alpha()
BG_ComoJogar = pygame.image.load('cenário/BG COMO_JOGAR.jpg').convert_alpha()


#Coletar LIXO
lixo_saco_img = pygame.image.load('Imagens/LIXO/0.png').convert_alpha()
lixo_saco_img = pygame.transform.scale(lixo_saco_img, (75,75))
lixo_copo_img = pygame.image.load('Imagens/LIXO/1.png').convert_alpha()
lixo_copo_img = pygame.transform.scale(lixo_copo_img, (65,100))
lixo_papel_img = pygame.image.load('Imagens/LIXO/2.png').convert_alpha()
lixo_papel_img = pygame.transform.scale(lixo_papel_img, (55, 55))
item_Boxes = {
    'Saco'      : lixo_saco_img,
    'Copo'      : lixo_copo_img,
    'Papel'      : lixo_papel_img,
}


BG_Jogo = pygame.image.load('cenário/BG JOGO.jpg').convert_alpha()


#CORES
BG = (135, 206, 235)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0,255,0)
BLUE = (0, 0, 255)

font = pygame.font.Font('fonte/Grobold.ttf', 32)
fonte = pygame.font.Font('fonte/Grobold.ttf', 50)

#musicas e sons ---------------------------------------------------------------
pygame.mixer.music.load('Sons/music.wav')
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1, 0.0, 5000)


ponto_fx = pygame.mixer.Sound('Sons/coin.wav')
ponto_fx.set_volume(0.111)

hit_fx = pygame.mixer.Sound('Sons/hit.wav')
hit_fx.set_volume(0.0111)

gameOver_fx = pygame.mixer.Sound('Sons/game_over.wav')
gameOver_fx.set_volume(0.02)


def draw_text(texto, font, cor, x, y):
    font = font.render(texto, True, cor)
    screen.blit(font, (x, y))



def desenhar_FundoJOGO():
    screen.blit(BG_Jogo, (0,0))
    rel_x = SCREEN_LARG % BG_Jogo.get_rect().width
    screen.blit(BG_Jogo, (rel_x - BG_Jogo.get_rect().width, 0))
    if rel_x < 1280:
        screen.blit(BG_Jogo, (rel_x, 0))



#Botões
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self, tela):
        action = False
        self.tela = tela


        #posiçao do mouse
        position = pygame.mouse.get_pos()

        #checar mouse apertar o botao
        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False


        #desenhar o Botão
        screen.blit(self.image, self.rect)

        return action


class Player(pygame.sprite.Sprite):
    def __init__(self, pasta_arquivo, x, y, tamanho, velocidade, pontos):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.pasta_arquivo = pasta_arquivo
        self.velocidade = velocidade
        self.pontuaçao = pontos
        self.start_pontos = pontos
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.virar = False
        self.jump = False
        self.vel_y = 0
        self.animacao_lista = []
        self.frame_indice = 0
        self.action = 0 #só vai nadar se apertar o botao
        self.update_time = pygame.time.get_ticks()

        #criar ai
        self.move_counter = 0


        #carregar imagens do jogador
        temp_list = []
        for i in range(9):  #animaçao para nadar SE TIVESSE OUTRA ANIMAÇAO ERA SÓ COPIAR ESSE FOR E  MUDAR  A PASTA DA ANIMAÇAO
            image = pygame.image.load(f'Imagens/{self.pasta_arquivo}/vivo/{i}.png').convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width() * tamanho), (int(image.get_height() * tamanho))))
            temp_list.append(image)
        self.animacao_lista.append(temp_list)
        temp_list = []
        for i in range(2):  #animaçao para nadar SE TIVESSE OUTRA ANIMAÇAO ERA SÓ COPIAR ESSE FOR E  MUDAR  A PASTA DA ANIMAÇAO
            image = pygame.image.load(f'Imagens/{self.pasta_arquivo}/morto/{i}.png').convert_alpha()
            image = pygame.transform.scale(image, (int(image.get_width() * tamanho), (int(image.get_height() * tamanho))))
            temp_list.append(image)
        self.animacao_lista.append(temp_list)
        self.image = self.animacao_lista[self.action][self.frame_indice]
        self.rect = self.image.get_rect()
        self.pos_x = x
        self.pos_y = y
        self.rect.center = (self.pos_x, self.pos_y)


    def update(self):
        self.atualizar_animacao()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1



    def mover(self, cima, baixo, direita, esquerda):
        #resetar variaveis do movimento
        dx = 0
        dy = 0

        #atribuindo movimento
        if esquerda:
            dx = -self.velocidade
            self.virar = True
            self.direction = -1
        if direita:
            dx = self.velocidade
            self.virar = False
            self.direction = 1
        if cima:
            dy = -self.velocidade
        if baixo:
            dy = self.velocidade


        #CHECAR COLICÕES ---------------------------------------------------------------------
        #Colisao com o chao
        # Jogador não sair da janela
        if self.rect.bottom + dy > 830:
            dy = 830 - self.rect.bottom  # nao ir para baixo da janela
        if self.rect.top + dy < 0:
            dy = 0 + self.rect.top  # nao ir para cima da janela

        if self.rect.right + dx > 1200:
            dx = 1200 - self.rect.right  # nao ir para baixo da janela
        if self.rect.left + dx < 0:
            dx = 0 - self.rect.left  # nao ir para cima da janela


        #colisão com os Animais------------------------------------------------------------------
        if pygame.sprite.collide_rect(self, tartaruga):
            Jogador.health -= 0.05
            hit_fx.play()

        if pygame.sprite.collide_rect(self, inimigo):
            Jogador.health -= 0.1
            hit_fx.play()

        if pygame.sprite.collide_rect(self, peixe):
            Jogador.health -= 0.01
            hit_fx.play()



        # Atualizar posiçao do retangulo
        self.rect.x += dx
        self.rect.y += dy





    def reset(self, pasta_arquivo, x, y, tamanho, velocidade, pontos):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.pasta_arquivo = pasta_arquivo
        self.velocidade = velocidade
        self.pontuaçao = pontos
        self.start_pontos = pontos
        self.shoot_cooldown = 0
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.virar = False
        self.jump = False
        self.vel_y = 0
        self.animacao_lista = []
        self.frame_indice = 0
        self.action = 0  # só vai nadar se apertar o botao
        self.update_time = pygame.time.get_ticks()

        # criar ai
        self.move_counter = 0

        # carregar imagens do jogador
        temp_list = []
        for i in range(
                9):  # animaçao para nadar SE TIVESSE OUTRA ANIMAÇAO ERA SÓ COPIAR ESSE FOR E  MUDAR  A PASTA DA ANIMAÇAO
            image = pygame.image.load(f'Imagens/{self.pasta_arquivo}/vivo/{i}.png').convert_alpha()
            image = pygame.transform.scale(image,
                                           (int(image.get_width() * tamanho), (int(image.get_height() * tamanho))))
            temp_list.append(image)
        self.animacao_lista.append(temp_list)
        temp_list = []
        for i in range(
                2):  # animaçao para nadar SE TIVESSE OUTRA ANIMAÇAO ERA SÓ COPIAR ESSE FOR E  MUDAR  A PASTA DA ANIMAÇAO
            image = pygame.image.load(f'Imagens/{self.pasta_arquivo}/morto/{i}.png').convert_alpha()
            image = pygame.transform.scale(image,
                                           (int(image.get_width() * tamanho), (int(image.get_height() * tamanho))))
            temp_list.append(image)
        self.animacao_lista.append(temp_list)
        self.image = self.animacao_lista[self.action][self.frame_indice]
        self.rect = self.image.get_rect()
        self.pos_x = x
        self.pos_y = y
        self.rect.center = (self.pos_x, self.pos_y)


    def atualizar_animacao(self):
        #atualizar animaçao
        ANIMACAO_COOLDOWN = 100 #parada
        #atualizar imagem
        self.image = self.animacao_lista[self.action][self.frame_indice]
        #checar tempo da animaçao
        if pygame.time.get_ticks() - self.update_time > ANIMACAO_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_indice += 1
        #se nao tiver mais imagens vai voltar e ficar em loop
        if self.frame_indice >= len(self.animacao_lista[self.action]):
            if self.action == 1:
                self.frame_indice = len(self.animacao_lista[self.action]) -1
            else:
                self.frame_indice = 0


    def update_action(self, new_action):
        #checar se a animaçao é diferente da anterior
        if new_action != self.action:
            self.action = new_action
            #atualizar configuraçao da animaçao
            self.frame_indice = 0
            self.update_time = pygame.time.get_ticks()



    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.velocidade = 0
            self.alive = False
            self.update_action(1)

            if self.rect.y > 200:
                self.rect.y -= 5
                gameOver_fx.play()




    def desenhar(self):
        screen.blit(pygame.transform.flip(self.image, self.virar, False), self.rect)
        #pygame.draw.rect(screen, RED, self.rect, 1)


class Animal(pygame.sprite.Sprite):
    def __init__(self, arquivo, x, y, velocidade):
        self.arquivo = arquivo
        self.pos_x = x
        self.pos_y = y
        self.velocidade = velocidade
        self.move_direction = 1
        self.virar = True
        self.image = pygame.image.load(f'Imagens/Animais/{arquivo}.png')
        self.rect = self.image.get_rect()



    def update(self):
        self.move_direction -= 1
        self.rect.left -= 1 * self.velocidade
        if self.rect.centerx == 0:
            self.rect.centery = random.randint(10, 800)
        if self.rect.centerx <= 0:
            self.rect.centerx = 1250
            self.rect.centery = random.randint(10, 800)



    def desenhar(self):
        screen.blit(pygame.transform.flip(self.image, self.virar, False), self.rect)
        #pygame.draw.rect(screen, RED, self.rect, 1)


class Tubarao(pygame.sprite.Sprite):
    def __init__(self, pasta_arquivo, x, y, velocidade):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.pasta_arquivo = pasta_arquivo
        self.velocidade = velocidade
        self.move_direction = -1
        self.pos_tuba_x = x
        self.pos_tuba_y = y
        self.virar = True
        self.animacao_lista = []
        self.frame_indice = 0
        self.action = 0 #só vai nadar se apertar o botao
        self.update_time = pygame.time.get_ticks()
        temp_list = []
        for i in range(2):  #animaçao para nadar SE TIVESSE OUTRA ANIMAÇAO ERA SÓ COPIAR ESSE FOR E  MUDAR  A PASTA DA ANIMAÇAO
            image = pygame.image.load(f'Imagens/{self.pasta_arquivo}/tuba/{i}.png').convert_alpha()
            image = pygame.transform.scale(image, (200,100))
            temp_list.append(image)
        self.animacao_lista.append(temp_list)
        self.image = self.animacao_lista[self.action][self.frame_indice]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.move_counter = 0


    def update(self):

        self.move_direction -= 1
        self.rect.left -= 1 * self.velocidade
        if self.rect.centerx == 0:
            self.rect.centery = random.randint(10, 800)
        if self.rect.centerx <= 0:
            self.rect.centerx = 1250
            self.rect.centery = random.randint(10, 800)





    def atualizar_animacao(self):
        #atualizar animaçao
        ANIMACAO_COOLDOWN = 100 #parada
        #atualizar imagem
        self.image = self.animacao_lista[self.action][self.frame_indice]
        #checar tempo da animaçao
        if pygame.time.get_ticks() - self.update_time > ANIMACAO_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_indice += 1
        #se nao tiver mais imagens vai voltar e ficar em loop
        if self.frame_indice >= len(self.animacao_lista[self.action]):
            self.frame_indice = 0



    def desenhar(self):
        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, RED, self.rect, 1)


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, velocidade):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.velocidade = velocidade
        self.pos_x = x

        self.image = item_Boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.move_direction = 0



    def randomizar(self):
        self.pos_x = 1250
        self.pos_y = random.randint(30, SCREEN_ALT - 10)
        self.rect.center = (self.pos_x, self.pos_y)


    def update(self):
        self.move_direction -= 0.015
        self.rect.centerx += self.move_direction * self.velocidade
        if self.rect.centerx == 0:
            self.rect.centery = random.randint(10,800)
        if self.rect.centerx <= 0:
            self.rect.centerx = 1250
            self.rect.centery = random.randint(10, 800)
            Jogador.health -= 0.5


        #checar colisao com os personagens
        if pygame.sprite.collide_rect(self, Jogador):
            if self.item_type == 'Copo':
                Jogador.pontuaçao += 2
                ponto_fx.play()


            elif self.item_type == 'Saco':
                Jogador.pontuaçao += 3
                ponto_fx.play()

            elif self.item_type == 'Papel':
                Jogador.pontuaçao += 1
                ponto_fx.play()




            #reaparecer os itens
            self.randomizar()
            print(Jogador.pontuaçao)


class HealthBar():
    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.health = health


    def draw(self, health):
        #update new health
        self.health = health
        #calcular saude do Jogador
        ratio = self.health / 100

        pygame.draw.rect(screen, BLACK, (self.x -2, self.y -2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))



# Sprite Grupos

item_Box_group = pygame.sprite.Group()


#temp - criar LIXO para coletar
item_Box = ItemBox('Copo',1300, 0.15)
item_Box_group.add(item_Box)
item_Box = ItemBox('Papel',500, 0.2)
item_Box_group.add(item_Box)
item_Box = ItemBox('Saco',1000, 0.3)
item_Box_group.add(item_Box)



Jogador = Player('Player', 100, 700, 1, 10, 0) #tamanho = 1 é a escala normal da imagem
SaudeJogador = HealthBar(10, 10, Jogador.health)

inimigo = Tubarao('Animais', 800, 550, 10)
tartaruga = Animal('tartaruga', 900,200, 7)
peixe = Animal('peixe', 800,500, 3)

#BOTOES
restart = Button(SCREEN_LARG // 2 - 90, SCREEN_ALT // 2 + 20, restart_img)

start_button = Button(SCREEN_LARG // 3 - 200, SCREEN_ALT // 3, start_img)
exit_button = Button(SCREEN_LARG // 3 + 90 , SCREEN_ALT // 3 + 350, sair_img)
creditos_button = Button(SCREEN_LARG // 3 + 60 , SCREEN_ALT // 3, creditos_img)
voltar_button = Button(SCREEN_LARG // 2 + 230, SCREEN_ALT// 2 + 320, voltar_img)
como_jogar_button = Button(SCREEN_LARG // 3 + 360, SCREEN_ALT // 3, como_jogar_img)



run = True
while run:

    clock.tick(FPS)



    desenhar_FundoJOGO()
    #desenhar o menu do JOGO
    if main_menu == True:
        #checar Menu
        if menu_state == "main":
            screen.blit(BG_Menu, (0,0))
            if exit_button.draw(screen):
                hit_fx.play()
                run = False

            if start_button.draw(screen):
                hit_fx.play()
                main_menu = False

            if como_jogar_button.draw(screen):
                hit_fx.play()
                menu_state = "como jogar"


            if creditos_button.draw(screen):
                menu_state = "creditos"
                hit_fx.play()

        if menu_state == "creditos":
            screen.blit(BG_Creditos, (0, 0))
            if voltar_button.draw(screen):
                hit_fx.play()
                menu_state = "main"

        if menu_state == "como jogar":
            screen.blit(BG_ComoJogar, (0, 0))
            if voltar_button.draw(screen):
                hit_fx.play()
                menu_state = "main"





    else:

        SaudeJogador.draw(Jogador.health)
        #mostrar pontos
        draw_text(f'Lixo Coletado: {Jogador.pontuaçao}', font, BLACK, 10, 35)

        # update
        Jogador.update()

        if Jogador.alive:

            SCREEN_LARG -= 5
            inimigo.atualizar_animacao()
            inimigo.update()



            tartaruga.update()
            peixe.update()

            item_Box_group.update()




        #desenhar
        Jogador.desenhar()
        inimigo.desenhar()
        tartaruga.desenhar()
        peixe.desenhar()



        item_Box_group.draw(screen)

        if not Jogador.alive:
            #screen.blit(fundo_restart, (200, 250))
            draw_text(f'Game Over', fonte, BLUE, 450, 320)
            draw_text(f'Você retirou {Jogador.pontuaçao} Lixos do mar.', font, BLACK, 370, 390)
            pygame.mixer.music.stop()



            if restart.draw(screen):
                Jogador.reset('Player', 100, 700, 1, 6, 0)
                pygame.mixer.music.play()


        #atualizar açoes do jogador
        if Jogador.alive:

            if cima or baixo or direita or esquerda:
                Jogador.update_action(0) #0: vivo #1: Dead
            #else:
            #caso o Jogador fizesse mais de 1 açao, tipo andar , correr
                #Jogador.update_action(1)  #se colocar isso quando nao mecher na tecla aparece o fantasma
            Jogador.mover(cima, baixo, direita, esquerda)



    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False

        #Pressionar teclas
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                cima = True
            if event.key == pygame.K_DOWN:
                baixo = True
            if event.key == pygame.K_LEFT:
                esquerda = True
            if event.key == pygame.K_RIGHT:
                direita = True

            if event.key == pygame.K_ESCAPE:
                main_menu = True


        # PARAR de Pressionar teclas
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                cima = False
            if event.key == pygame.K_DOWN:
                baixo = False
            if event.key == pygame.K_LEFT:
                esquerda = False
            if event.key == pygame.K_RIGHT:
                direita = False




    pygame.display.update()



pygame.quit()
