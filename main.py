import pygame
import sys
import os
import json

# --------------------------------------------------
# CONFIGURAÇÃO DE DIRETÓRIOS
# --------------------------------------------------
diretorioPrincipal = os.path.dirname(__file__)
diretorioImg = os.path.join(diretorioPrincipal, 'img')
diretorioSons = os.path.join(diretorioPrincipal, 'sons')

# --------------------------------------------------
# INICIALIZAÇÃO DO PYGAME E DO MIXER DE SONS
# --------------------------------------------------
pygame.init()
pygame.mixer.init()
# musica_path = os.path.join(diretorioSons, 'musicaPrincipal.wav')
# pygame.mixer.music.load(musica_path)
# pygame.mixer.music.play(-1)

# --------------------------------------------------
# CONFIGURAÇÃO DA TELA E VARIÁVEIS GLOBAIS
# --------------------------------------------------
screen_width, screen_height = 940, 360
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Nadsuu Adventure")
clock = pygame.time.Clock()
pontuacao = 0

# Estado do jogo: "menu", "playing", "game_over"
state = "menu"

# --------------------------------------------------
# CARREGA O CENÁRIO PARALLAX (8 camadas)
# --------------------------------------------------
camadas = []
for i in range(1, 9):
    caminho_imagem = os.path.join(diretorioImg, f"camada{i}.png")
    imagem = pygame.image.load(caminho_imagem).convert_alpha()
    camadas.append(imagem)

# Inicializa as posições horizontais para cada camada
x_positions = [0 for _ in range(len(camadas))]
speeds = [20, 40, 60, 80, 100, 120, 140, 160]

# --------------------------------------------------
# CARREGA O SPRITESHEET DO PERSONAGEM
# --------------------------------------------------
spriteSheet = pygame.image.load(os.path.join(diretorioImg, 'global.png')).convert_alpha()

# --------------------------------------------------
# CLASSE PERSONAGEM (JOGADOR)
# --------------------------------------------------
class Personagem(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.vidas = 3
        # Dicionário para armazenar as animações (estados) do personagem
        self.animacoes = {
            'parado': [],
            'correndo': [],
            'saltando': [],
            'atacando': [],
            'morrendo': []
        }
        
        largura_frame = 32   # Largura original do frame no spritesheet
        altura_frame = 32    # Altura original do frame no spritesheet
        escala = 3           # Fator de escala para aumentar o tamanho do sprite
        
        # Animação PARADO (linha 0, 2 frames)
        for i in range(2):
            x = i * largura_frame
            y = 0
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes['parado'].append(img)
        
        # --------------------
        # Animação CORRENDO (linha 1, 2 frames)
        for i in range(2):
            x = i * largura_frame
            y = altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes['correndo'].append(img)
        
        # --------------------
        # Animação SALTANDO (linha 2, 4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 2 * altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes['saltando'].append(img)
        
        # --------------------
        # Animação ATACANDO (linha 3, 2 frames)
        for i in range(2):
            x = i * largura_frame
            y = 3 * altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes['atacando'].append(img)
        
        # --------------------
        # Animação MORRENDO (linha 4, 2 frames)
        for i in range(2):
            x = i * largura_frame
            y = 4 * altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes['morrendo'].append(img)
        
        self.estado_atual = 'parado'
        self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        self.rect = self.image.get_rect()
        # Define uma posição inicial "segura" para o personagem
        self.rect.center = (100, 100)
        
        # Atributo para definir a direção do personagem (True = direita, False = esquerda)
        self.facing_right = True
        
        # Configuração para gravidade e movimento vertical (usando vetores)
        self.pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.vel = pygame.math.Vector2(0, 0)
        self.gravity = 1000
        self.ground_y = screen_height - 115
        
    def update(self, dt):
        # Atualiza a animação com base no delta time
        velocidade_animacao = 5
        self.index += velocidade_animacao * dt
        if self.index >= len(self.animacoes[self.estado_atual]):
            self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        
        # Inverte a imagem se o personagem não estiver olhando para a direita
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        
        # Atualiza a velocidade e a posição vertical aplicando a gravidade
        self.vel.y += self.gravity * dt
        self.pos.y += self.vel.y * dt
        
        # Se o personagem atingir o chão, fixa a posição e zera a velocidade vertical
        if self.pos.y > self.ground_y:
            self.pos.y = self.ground_y
            self.vel.y = 0

        self.rect.y = int(self.pos.y)
        
        # Verifica condição de Game Over (vidas <= 0)
        if self.vidas <= 0:
            self.set_estado('morrendo')
            print("Game Over!")
            
    def set_estado(self, novo_estado):
        if novo_estado in self.animacoes and novo_estado != self.estado_atual:
            self.estado_atual = novo_estado
            self.index = 0


# --------------------------------------------------
# CLASSE DO INIMIGO "SKELETON" COM IA BÁSICA E VIRADA DE IMAGEM
# --------------------------------------------------
class Skeleton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        skeleton_path = os.path.join(diretorioImg, "Skeleton", "GlobalSkeleton.png")
        self.skeletonSheet = pygame.image.load(skeleton_path).convert_alpha()
        
        # Dicionário para armazenar as animações do Skeleton
        self.animacoes = {
            "attack": [],
            "death": [],
            "idle": [],
            "shield": [],
            "take_hit": [],
            "walk": []
        }
        largura_frame = 64   # Largura do frame original do Skeleton
        altura_frame = 64    # Altura do frame original do Skeleton
        escala = 1.8         # Fator de escala para aumentar o tamanho do Skeleton
        
        # --------------------
        # Linha 0: Animação "attack" (8 frames)
        for i in range(8):
            x = i * largura_frame
            y = 0
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["attack"].append(img)
        
        # --------------------
        # Linha 1: Animação "death" (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["death"].append(img)
        
        # --------------------
        # Linha 2: Animação "idle" (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 2 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["idle"].append(img)
        
        # --------------------
        # Linha 3: Animação "shield" (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 3 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["shield"].append(img)
        
        # --------------------
        # Linha 4: Animação "take_hit" (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 4 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["take_hit"].append(img)
        
        # --------------------
        # Linha 5: Animação "walk" (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 5 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["walk"].append(img)
        
        # Estado inicial do Skeleton: idle
        self.estado_atual = "idle"
        self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (400, screen_height - 18)
        self.animation_speed = 5  # Velocidade da animação
        
        # Define a vida do inimigo e o timer de invulnerabilidade
        self.health = 100
        self.invulnerable_timer = 0
        
    def take_damage(self, damage):
        if self.invulnerable_timer > 0:
            return
        self.health -= damage
        print("Skeleton took damage! Health:", self.health)
        if self.health <= 0:
            self.estado_atual = "death"
        else:
            self.estado_atual = "take_hit"
            self.animation_speed = 10
            self.invulnerable_timer = 0.5
        
    def update(self, dt):
        # IA: Persegue o jogador
        distancia = prota.rect.centerx - self.rect.centerx
        if self.estado_atual not in ["death", "take_hit"]:
            if abs(distancia) < 300:
                self.estado_atual = "walk"
                if abs(distancia) < 50:
                    self.estado_atual = "attack"
            else:
                self.estado_atual = "idle"
            if self.estado_atual == "walk":
                velocidade_perseguicao = 50
                if distancia > 0:
                    self.rect.x += velocidade_perseguicao * dt
                else:
                    self.rect.x -= velocidade_perseguicao * dt
        
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
        
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
        
        self.index += self.animation_speed * dt
        if self.index >= len(self.animacoes[self.estado_atual]):
            if self.estado_atual == "death":
                self.kill()
                return
            self.index = 0
            if self.estado_atual == "take_hit" and self.health > 0:
                self.estado_atual = "idle"
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        
        # Vira a imagem conforme a posição do jogador
        if prota.rect.centerx < self.rect.centerx:
            self.image = pygame.transform.flip(self.image, True, False)

# --------------------------------------------------
# CLASSES PARA OBJETOS DO MAPA (USANDO JSON)
# --------------------------------------------------
class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

class Buraco(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill((21, 24, 38))  # Altere os valores RGB para mudar a cor do buraco
        self.rect = self.image.get_rect(topleft=(x, y))

class PedraCaindo(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height))
        self.image.fill((150, 150, 150))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed

    def update(self, dt):
        self.rect.y += self.speed * dt
        if self.rect.top > screen_height:
            self.kill()

# --------------------------------------------------
# CLASSE LEVEL (CARREGA JSON)
# --------------------------------------------------
class Level:
    def __init__(self, json_file):
        with open(json_file, "r") as f:
            self.data = json.load(f)
        self.platforms = pygame.sprite.Group()
        self.buracos = pygame.sprite.Group()
        self.pedras = pygame.sprite.Group()
        for p in self.data["platforms"]:
            plat = Plataforma(p["x"], p["y"], p["width"], p["height"])
            self.platforms.add(plat)
        for h in self.data["holes"]:
            buraco = Buraco(h["x"], h["y"], h["width"], h["height"])
            self.buracos.add(buraco)
        for stone in self.data["falling_stones"]:
            pedra = PedraCaindo(stone["x"], stone["y"], stone["width"], stone["height"], stone["speed"])
            self.pedras.add(pedra)
    def update(self, dt):
        self.platforms.update(dt)
        self.buracos.update(dt)
        self.pedras.update(dt)
    def draw(self, surface, camera_offset=0):
        for plat in self.platforms:
            surface.blit(plat.image, (plat.rect.x - camera_offset, plat.rect.y))
        for buraco in self.buracos:
            surface.blit(buraco.image, (buraco.rect.x - camera_offset, buraco.rect.y))
        for pedra in self.pedras:
            surface.blit(pedra.image, (pedra.rect.x - camera_offset, pedra.rect.y))

# --------------------------------------------------
# FUNÇÃO PARA CHECAR COLISÕES COM PLATAFORMAS
# --------------------------------------------------
def check_collisions(player, platforms):
    player_on_platform = False  # Flag para verificar se o jogador está em uma plataforma

    for plat in platforms:
        # Verifica se o jogador está caindo e colidiu com a plataforma
        if player.vel.y > 0 and player.rect.colliderect(plat.rect):
            if (player.old_y + player.rect.height) <= plat.rect.top:
                # Posiciona o jogador exatamente em cima da plataforma
                player.pos.y = plat.rect.top
                player.rect.bottom = plat.rect.top
                player.vel.y = 0
                player.falling = False
                player_on_platform = True
                break  # Sai do loop após a primeira colisão

    # Se não estiver em nenhuma plataforma, define que o jogador está no ar
    if not player_on_platform:
        player.falling = True
    # Impede o jogador de atravessar por baixo
    elif player.vel.y < 0 and player.rect.colliderect(plat.rect):
        if player.old_y >= plat.rect.bottom:
            player.pos.y = plat.rect.bottom + 1
            player.rect.top = plat.rect.bottom + 1
            player.vel.y = 0



# --------------------------------------------------
# FUNÇÃO PARA CHECAR SE O PLAYER CAIU NO BURACO
# --------------------------------------------------
def check_holes(player, holes):
    # Verifica se o centro do player está dentro do intervalo horizontal de algum buraco
    falling = False
    for buraco in holes:
        if player.rect.centerx >= buraco.rect.left and player.rect.centerx <= buraco.rect.right:
            # Se o player estiver acima do buraco (próximo do topo) e não estiver colidindo com uma plataforma
            if player.rect.bottom >= buraco.rect.top:
                falling = True
                break
    player.falling = falling

# --------------------------------------------------
# CARREGA O MAPA A PARTIR DO JSON
# --------------------------------------------------
level = Level(os.path.join(diretorioPrincipal, "level1.json"))

# --------------------------------------------------
# FUNÇÃO PARA REINICIAR O JOGO
# --------------------------------------------------
def reset_game():
    global prota, skeleton, globalPlayer, globalInimigo, x_positions, pontuacao, game_over, level
    pontuacao = 0
    prota = Personagem()
    globalPlayer.empty()
    globalPlayer.add(prota)
    skeleton = Skeleton()
    globalInimigo.empty()
    globalInimigo.add(skeleton)
    x_positions = [0 for _ in range(len(camadas))]
    level = Level(os.path.join(diretorioPrincipal, "level1.json"))
    game_over = False

# --------------------------------------------------
# CRIAÇÃO DOS GRUPOS DE SPRITES
# --------------------------------------------------
globalPlayer = pygame.sprite.Group()
globalInimigo = pygame.sprite.Group()

prota = Personagem()
globalPlayer.add(prota)

skeleton = Skeleton()
globalInimigo.add(skeleton)

game_over = False  # Flag para controle do estado do jogo

# --------------------------------------------------
# LOOP PRINCIPAL DO JOGO
# --------------------------------------------------
while True:
    dt = clock.tick(30) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Evento de pulo: se a tecla W for pressionada e o personagem estiver no chão
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if prota.vel.y == 0:
                    prota.vel.y = -500  # Velocidade inicial do pulo
                    prota.set_estado('saltando')
            # Se o jogo estiver em Game Over e o jogador pressionar R, reinicia o jogo
            if game_over and event.key == pygame.K_r:
                reset_game()
                state = "menu"
    
    keys = pygame.key.get_pressed()
    
    # --------------------------------------------------
    # CONTROLE DE ESTADO DO PERSONAGEM
    # --------------------------------------------------
    if keys[pygame.K_j]:
        prota.set_estado('atacando')
    elif keys[pygame.K_a] or keys[pygame.K_d]:
        if prota.vel.y == 0:
            prota.set_estado('correndo')
    else:
        if prota.vel.y == 0:
            prota.set_estado('parado')
    
    # --------------------------------------------------
    # MOVIMENTAÇÃO HORIZONTAL DO PERSONAGEM E PARALLAX
    # --------------------------------------------------
    min_x = 100
    max_x = screen_width - 100 - prota.rect.width
    
    if keys[pygame.K_a]:
        prota.facing_right = False
        if prota.rect.x > min_x:
            prota.rect.x -= 5
            prota.pos.x = prota.rect.x
        else:
            for idx, camada in enumerate(camadas):
                x_positions[idx] += speeds[idx] * dt
                if x_positions[idx] > 0:
                    x_positions[idx] = 0
    if keys[pygame.K_d]:
        prota.facing_right = True
        if prota.rect.x < max_x:
            prota.rect.x += 5
            prota.pos.x = prota.rect.x
        else:
            for idx, camada in enumerate(camadas):
                x_positions[idx] -= speeds[idx] * dt
                if x_positions[idx] <= -camadas[idx].get_width():
                    x_positions[idx] = 0
    
    # --------------------------------------------------
    # ATUALIZAÇÃO DOS SPRITES
    # --------------------------------------------------
    globalPlayer.update(dt)
    globalInimigo.update(dt)
    
    # --------------------------------------------------
    # DETECÇÃO DE COLISÃO PARA APLICAR DANO
    # --------------------------------------------------
    if prota.estado_atual == 'atacando' and prota.rect.colliderect(skeleton.rect):
        skeleton.take_damage(20)
        pontuacao += 20
    
    # --------------------------------------------------
    # CONDIÇÃO DE GAME OVER
    # --------------------------------------------------
    if prota.vidas <= 0:
        game_over = True
    
    # --------------------------------------------------
    # DESENHO NA TELA
    # --------------------------------------------------
    screen.fill((255, 255, 255))
    for idx, camada in enumerate(camadas):
        screen.blit(camada, (x_positions[idx], 0))
        screen.blit(camada, (x_positions[idx] + camada.get_width(), 0))
    
    globalInimigo.draw(screen)
    globalPlayer.draw(screen)
    
    if game_over:
        font = pygame.font.SysFont("Arial", 36)
        text = font.render("Game Over! Pressione R para reiniciar", True, (255, 0, 0))
        screen.blit(text, (50, screen_height//2))
    
    pygame.display.flip()
