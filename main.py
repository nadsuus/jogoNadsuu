import pygame
import sys
import os

# --------------------------------------------------
# CONFIGURAÇÃO DE DIRETÓRIOS
# By: Nadsuus
# Data: 10/02/2025
# --------------------------------------------------
diretorioPrincipal = os.path.dirname(__file__)
diretorioImg = os.path.join(diretorioPrincipal, 'img')
diretorioSons = os.path.join(diretorioPrincipal, 'sons')

# --------------------------------------------------
# INICIALIZAÇÃO DO PYGAME E DO MIXER DE SONS
# --------------------------------------------------
pygame.init()
pygame.mixer.init()

musica_path = os.path.join(diretorioSons, 'musicaPrincipal.wav')
# pygame.mixer.music.load(musica_path)
# pygame.mixer.music.play(-1)

# --------------------------------------------------
# CONFIGURAÇÃO DA TELA
# --------------------------------------------------
screen_width, screen_height = 940, 360
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Nadsuu Adventure")
clock = pygame.time.Clock()
pontuacao = 0

# --------------------------------------------------
# CARREGA O CENÁRIO PARALLAX
# --------------------------------------------------
camadas = []
for i in range(1, 9):
    caminho_imagem = os.path.join(diretorioImg, f"camada{i}.png")
    imagem = pygame.image.load(caminho_imagem).convert_alpha()
    camadas.append(imagem)

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
        self.invulnerable_timer = 0  # Tempo de invulnerabilidade após receber dano
        
        self.animacoes = {
            'parado': [],
            'correndo': [],
            'saltando': [],
            'atacando': [],
            'morrendo': []
        }
        
        largura_frame = 32
        altura_frame = 32
        escala = 3
        
        # Animação PARADO (linha 0, 2 frames)
        for i in range(2):
            x = i * largura_frame
            y = 0
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes['parado'].append(img)
        
        # Animação CORRENDO (linha 1, 2 frames)
        for i in range(2):
            x = i * largura_frame
            y = altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes['correndo'].append(img)
        
        # Animação SALTANDO (linha 2, 4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 2 * altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes['saltando'].append(img)
        
        # Animação ATACANDO (linha 3, 2 frames)
        for i in range(2):
            x = i * largura_frame
            y = 3 * altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes['atacando'].append(img)
        
        # Animação MORRENDO (linha 4, 2 frames)
        for i in range(2):
            x = i * largura_frame
            y = 4 * altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes['morrendo'].append(img)
        
        self.estado_atual = 'parado'
        self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.center = (20, 20)
        
        self.facing_right = True
        
        self.pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.vel = pygame.math.Vector2(0, 0)
        self.gravity = 1000
        self.ground_y = screen_height - 115
        
    def update(self, dt):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
        
        velocidade_animacao = 5
        self.index += velocidade_animacao * dt
        if self.index >= len(self.animacoes[self.estado_atual]):
            self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        
        self.vel.y += self.gravity * dt
        self.pos.y += self.vel.y * dt
        
        if self.pos.y > self.ground_y:
            self.pos.y = self.ground_y
            self.vel.y = 0
        self.rect.y = int(self.pos.y)
        
        if self.vidas <= 0:
            self.set_estado('morrendo')
            print("Game Over!")
            
    def set_estado(self, novo_estado):
        if novo_estado in self.animacoes and novo_estado != self.estado_atual:
            self.estado_atual = novo_estado
            self.index = 0

# --------------------------------------------------
# CLASSE DO INIMIGO "SKELETON" COM IA, VIRADA DE IMAGEM E DELAY DE DANO
# --------------------------------------------------
class Skeleton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        skeleton_path = os.path.join(diretorioImg, "Skeleton", "GlobalSkeleton.png")
        self.skeletonSheet = pygame.image.load(skeleton_path).convert_alpha()
        
        self.animacoes = {
            "attack": [],
            "death": [],
            "idle": [],
            "shield": [],
            "take_hit": [],
            "walk": []
        }
        largura_frame = 64
        altura_frame = 64
        escala = 1.8
        
        # Linha 0: Attack (8 frames)
        for i in range(8):
            x = i * largura_frame
            y = 0
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes["attack"].append(img)
        
        # Linha 1: Death (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes["death"].append(img)
        
        # Linha 2: Idle (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 2 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes["idle"].append(img)
        
        # Linha 3: Shield (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 3 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes["shield"].append(img)
        
        # Linha 4: Take Hit (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 4 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes["take_hit"].append(img)
        
        # Linha 5: Walk (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 5 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
            self.animacoes["walk"].append(img)
        
        self.estado_atual = "idle"
        self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (400, screen_height - 18)
        self.animation_speed = 5
        
        self.health = 5
        self.invulnerable_timer = 0
        self.damage_cooldown = 0  # Delay para causar dano ao jogador
        
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
# FUNÇÃO PARA REINICIAR O JOGO
# --------------------------------------------------
def reset_game():
    global prota, skeleton, globalPlayer, globalInimigo, x_positions, pontuacao, game_over
    pontuacao = 0
    prota = Personagem()
    globalPlayer.empty()
    globalPlayer.add(prota)
    skeleton = Skeleton()
    globalInimigo.empty()
    globalInimigo.add(skeleton)
    x_positions = [0 for _ in range(len(camadas))]
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

game_over = False

# --------------------------------------------------
# LOOP PRINCIPAL DO JOGO
# --------------------------------------------------
while True:
    dt = clock.tick(30) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if prota.vel.y == 0:
                    prota.vel.y = -500
                    prota.set_estado('saltando')
            if game_over and event.key == pygame.K_r:
                reset_game()
    
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_j]:
        prota.set_estado('atacando')
    elif keys[pygame.K_a] or keys[pygame.K_d]:
        if prota.vel.y == 0:
            prota.set_estado('correndo')
    else:
        if prota.vel.y == 0:
            prota.set_estado('parado')
    
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
    
    globalPlayer.update(dt)
    globalInimigo.update(dt)
    
    # Se o player está atacando e colidiu com o skeleton, ele recebe dano
    if prota.estado_atual == 'atacando' and prota.rect.colliderect(skeleton.rect):
        skeleton.take_damage(1)
        pontuacao += 20
    
    # Se o skeleton estiver atacando e colidir com o player, aplica dano somente a cada 1s
    if skeleton.estado_atual == 'attack' and skeleton.rect.colliderect(prota.rect):
        if skeleton.damage_cooldown <= 0:
            prota.vidas -= 1
            prota.invulnerable_timer = 2  # Player fica invulnerável por 2 segundos
            skeleton.damage_cooldown = 1   # Delay de 1 segundo para causar novo dano
    
    if prota.vidas <= 0:
        game_over = True
    
    screen.fill((255, 255, 255))
    for idx, camada in enumerate(camadas):
        screen.blit(camada, (x_positions[idx], 0))
        screen.blit(camada, (x_positions[idx] + camada.get_width(), 0))
    
    globalInimigo.draw(screen)
    globalPlayer.draw(screen)
    
    if game_over:
        font = pygame.font.SysFont("Arial", 36)
        text = font.render("Game Over! Pressione R para reiniciar", True, (255, 0, 0))
        screen.blit(text, (50, screen_height // 2))
    
    pygame.display.flip()
