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
        self.max_vidas = 3  # Definindo a vida máxima
        self.is_damaged = False  # Flag para controlar o efeito visual de dano

        self.invulnerable_timer = 0
        self.falling = False  # Flag que indica se o player está caindo no buraco
        
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
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes['parado'].append(img)
        # Animação CORRENDO (linha 1, 2 frames)
        for i in range(2):
            x = i * largura_frame
            y = altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes['correndo'].append(img)
        # Animação SALTANDO (linha 2, 4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 2 * altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes['saltando'].append(img)
        # Animação ATACANDO (linha 3, 2 frames)
        for i in range(2):
            x = i * largura_frame
            y = 3 * altura_frame
            img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes['atacando'].append(img)
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
        self.rect.center = (100, 100)
        self.facing_right = True
        self.pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.vel = pygame.math.Vector2(0, 0)
        self.gravity = 1000
        self.ground_y = screen_height - 115
        
    def update(self, dt):
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt
            self.is_damaged = True  # Ativa o efeito de dano
        else:
            self.is_damaged = False  # Reseta o efeito visual de dano

        self.old_y = self.pos.y  # Armazena a posição anterior

        velocidade_animacao = 5
        self.index += velocidade_animacao * dt
        if self.index >= len(self.animacoes[self.estado_atual]):
            self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        
        # Efeito visual de piscar em vermelho quando estiver com dano
        if self.is_damaged:
            tinted_image = self.image.copy()
            tinted_image.fill((255, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = tinted_image

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        self.vel.y += self.gravity * dt
        self.pos.y += self.vel.y * dt
        if self.pos.y > screen_height:
            self.pos.y = screen_height
            self.vel.y = 0

        self.rect.y = int(self.pos.y)

        if self.falling and self.rect.top > screen_height:
            self.vidas = 0
        if self.vidas <= 0:
            self.set_estado('morrendo')
            print("Game Over!")

            if self.invulnerable_timer > 0:
                self.invulnerable_timer -= dt
            else:
                self.invulnerable_timer = 0

            self.old_y = self.pos.y  # Armazena a posição anterior
            
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
            
            if self.falling and self.rect.top > screen_height:
                self.vidas = 0
            if self.vidas <= 0:
                self.set_estado('morrendo')
                print("Game Over!")

    def set_estado(self, novo_estado):
        if novo_estado in self.animacoes and novo_estado != self.estado_atual:
            self.estado_atual = novo_estado
            self.index = 0


# --------------------------------------------------
# CLASSE DO INIMIGO "SKELETON" COM IA, VIRADA E DELAY DE DANO
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
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["attack"].append(img)
        # Linha 1: Death (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["death"].append(img)
        # Linha 2: Idle (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 2 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["idle"].append(img)
        # Linha 3: Shield (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 3 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["shield"].append(img)
        # Linha 4: Take Hit (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 4 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["take_hit"].append(img)
        # Linha 5: Walk (4 frames)
        for i in range(4):
            x = i * largura_frame
            y = 5 * altura_frame
            img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
            img = pygame.transform.scale(img, (largura_frame*escala, altura_frame*escala))
            self.animacoes["walk"].append(img)
        self.estado_atual = "idle"
        self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.midbottom = (400, screen_height - 18)
        self.animation_speed = 5
        self.health = 5
        self.max_health = 5  # Definindo a vida máxima do esqueleto

        self.invulnerable_timer = 0
        self.damage_cooldown = 0  # Delay de 1 segundo para causar dano
        
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

game_over = False
state = "menu"

def draw_health_bar(surface, x, y, current_health, max_health, width=100, height=10):
    health_ratio = current_health / max_health
    pygame.draw.rect(surface, (255, 0, 0), (x, y, width, height))
    pygame.draw.rect(surface, (0, 255, 0), (x, y, width * health_ratio, height))
    pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 2)  # Borda preta


# --------------------------------------------------
# LOOP PRINCIPAL DO JOGO
# --------------------------------------------------
while True:
    dt = clock.tick(30) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if state == "menu":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                state = "playing"
        elif state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    if prota.vel.y == 0:
                        prota.vel.y = -500
                        prota.set_estado('saltando')
        elif state == "game_over":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()
                state = "menu"
    
    keys = pygame.key.get_pressed()
    
    if state == "playing" and prota.estado_atual != 'morrendo':
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
        level.update(dt)
        check_collisions(prota, level.platforms)
        check_holes(prota, level.buracos)
        
        # Se o player estiver caindo e sair da tela, ele morre
        if prota.falling and prota.rect.top > screen_height:
            prota.vidas = 0
        
        if prota.vidas <= 0:
            state = "game_over"
        
        if prota.estado_atual == 'atacando' and prota.rect.colliderect(skeleton.rect):
            skeleton.take_damage(20)
            pontuacao += 20
        
        if skeleton.estado_atual == 'attack' and skeleton.rect.colliderect(prota.rect):
            if skeleton.damage_cooldown <= 0 and prota.invulnerable_timer <= 0:
                prota.vidas -= 1
                prota.invulnerable_timer = 2  # 2 segundos de invulnerabilidade
                skeleton.damage_cooldown = 1


    if state == "menu":
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("Arial", 36)
        text = font.render("Pressione ESPAÇO para iniciar", True, (255, 255, 255))
        screen.blit(text, (50, screen_height//2))
    elif state == "playing":
        screen.fill((135, 206, 235))
        for idx, camada in enumerate(camadas):
            screen.blit(camada, (x_positions[idx], 0))
            screen.blit(camada, (x_positions[idx] + camada.get_width(), 0))
        level.draw(screen)
        globalInimigo.draw(screen)
        globalPlayer.draw(screen)
        # Desenhar barras de vida
        draw_health_bar(screen, prota.rect.x, prota.rect.y - 20, prota.vidas, prota.max_vidas, width=60, height=8)
        draw_health_bar(screen, skeleton.rect.x, skeleton.rect.y - 20, skeleton.health, skeleton.max_health, width=60, height=8)

    elif state == "game_over":
        screen.fill((0, 0, 0))
        font = pygame.font.SysFont("Arial", 36)
        text = font.render("Game Over! Pressione R para reiniciar", True, (255, 0, 0))
        screen.blit(text, (50, screen_height//2))
    
    pygame.display.flip()
