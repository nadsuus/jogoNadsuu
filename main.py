import pygame
import sys
import os
import json

# Configurações Globais
SCREEN_WIDTH, SCREEN_HEIGHT = 940, 360
FPS = 30

# --------------------------------------------------
# CLASSES DOS PERSONAGENS
# --------------------------------------------------
class Personagem(pygame.sprite.Sprite):
    def __init__(self, spriteSheet, screen_height):
        super().__init__()
        self.vidas = 3
        self.estaOlhandoParaDireita = True
        self.falling = True
        self.is_jumping = False

        # Animações do personagem
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

        for estado, linha, num_frames in [
            ('parado', 0, 2),
            ('correndo', 1, 2),
            ('saltando', 2, 3),
            ('atacando', 3, 4),
            ('morrendo', 4, 2)
        ]:
            for i in range(num_frames):
                x = i * largura_frame
                y = linha * altura_frame
                img = spriteSheet.subsurface((x, y), (largura_frame, altura_frame))
                img = pygame.transform.scale(img, (largura_frame * escala, altura_frame * escala))
                self.animacoes[estado].append(img)

        self.estado_atual = 'parado'
        self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        self.rect = self.image.get_rect(center=(100, 100))

        # Física
        self.pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.vel = pygame.math.Vector2(0, 0)
        self.gravity = 1000
        self.jump_force = -300

        # Timer para ignorar colisões após o pulo
        self.ignore_collision_timer = 0

    def update(self, dt):
        self.old_y = self.pos.y  # Salva a posição vertical antiga

        if self.ignore_collision_timer > 0:
            self.ignore_collision_timer -= dt

        # Atualiza animação
        velocidade_animacao = 15 if self.estado_atual == 'atacando' else 8
        self.index += velocidade_animacao * dt
        if self.index >= len(self.animacoes[self.estado_atual]):
            if self.estado_atual == 'atacando':
                self.set_estado('parado')
            self.index = 0

        frame = self.animacoes[self.estado_atual][int(self.index)]
        if not self.estaOlhandoParaDireita:
            frame = pygame.transform.flip(frame, True, False)
        self.image = frame

        # Aplica física (gravidade e pulo)
        if self.falling or self.is_jumping:
            self.vel.y += self.gravity * dt
            self.pos.y += self.vel.y * dt

        self.rect.y = int(self.pos.y)

        if self.vidas <= 0:
            self.set_estado('morrendo')

    def set_estado(self, novo_estado):
        if novo_estado in self.animacoes and novo_estado != self.estado_atual:
            self.estado_atual = novo_estado
            self.index = 0

    def pular(self):
        if not self.is_jumping and not self.falling:
            self.is_jumping = True
            self.ignore_collision_timer = 0.5  # Ignorar colisões por 0.5s
            self.pos.y -= 30  # Eleva o personagem para "descolar" da plataforma
            self.vel.y = self.jump_force
            self.set_estado('saltando')
            print("Pulando")


class Esqueleto(pygame.sprite.Sprite):
    def __init__(self, diretorioImg, screen_height):
        super().__init__()
        caminho_esqueleto = os.path.join(diretorioImg, "Skeleton", "GlobalSkeleton.png")
        self.skeletonSheet = pygame.image.load(caminho_esqueleto).convert_alpha()
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

        for estado, linha, num_frames in [
            ("attack", 0, 8),
            ("death", 1, 4),
            ("idle", 2, 4),
            ("shield", 3, 4),
            ("take_hit", 4, 4),
            ("walk", 5, 4)
        ]:
            for i in range(num_frames):
                x = i * largura_frame
                y = linha * altura_frame
                img = self.skeletonSheet.subsurface((x, y), (largura_frame, altura_frame))
                img = pygame.transform.scale(img, (int(largura_frame * escala), int(altura_frame * escala)))
                self.animacoes[estado].append(img)

        self.estado_atual = "idle"
        self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        self.rect = self.image.get_rect(midbottom=(400, screen_height - 18))
        self.animation_speed = 5
        self.health = 100
        self.invulnerable_timer = 0
        self.damage_cooldown = 0

    def receber_dano(self, dano):
        if self.invulnerable_timer > 0:
            return
        self.health -= dano
        print("Esqueleto recebeu dano! Vida:", self.health)
        if self.health <= 0:
            self.estado_atual = "death"
        else:
            self.estado_atual = "take_hit"
            self.animation_speed = 10
            self.invulnerable_timer = 0.5

    def update(self, dt):
        distancia = jogo.player.rect.centerx - self.rect.centerx
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
        if jogo.player.rect.centerx < self.rect.centerx:
            self.image = pygame.transform.flip(self.image, True, False)

# --------------------------------------------------
# CLASSES DOS ELEMENTOS DO MAPA
# --------------------------------------------------
class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

class PlataformaBase(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill((50, 50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))

# A função de colisão agora usa as coordenadas das plataformas do JSON
def checar_colisoes_plataforma(jogador, plataformas_normais, plataforma_base, dt):
    # Se o jogador já está no solo (não pulando nem caindo), não verifica colisões
    if not (jogador.falling or jogador.is_jumping):
        return

    # Se o timer de ignorar colisões ainda estiver ativo, sai
    if hasattr(jogador, 'ignore_collision_timer') and jogador.ignore_collision_timer > 0:
        return

    epsilon = 5  # margem de tolerância

    if jogador.vel.y > 0:
        estaNoChao = False
        for plat in plataformas_normais:
            if jogador.rect.colliderect(plat.rect):
                if (jogador.old_y + jogador.rect.height) < (plat.rect.top + epsilon) and jogador.rect.bottom >= plat.rect.top:
                    jogador.pos.y = plat.rect.top - jogador.rect.height
                    jogador.rect.bottom = plat.rect.top
                    jogador.vel.y = 0
                    jogador.falling = False
                    jogador.is_jumping = False
                    print("Caindo na plataforma")
                    estaNoChao = True
                    break
        if not estaNoChao and plataforma_base is not None:
            if jogador.rect.colliderect(plataforma_base.rect):
                if (jogador.old_y + jogador.rect.height) < (plataforma_base.rect.top + epsilon) and jogador.rect.bottom >= plataforma_base.rect.top:
                    jogador.pos.y = plataforma_base.rect.top - jogador.rect.height
                    jogador.rect.bottom = plataforma_base.rect.top
                    jogador.vel.y = 0
                    jogador.falling = False
                    print("Caindo na base")
                    estaNoChao = True

        # Se o jogador não colidiu com nenhuma plataforma, ele continua caindo
        if not estaNoChao:
            jogador.falling = True

class Buraco(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

class PedraCaindo(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, altura, velocidade):
        super().__init__()
        self.image = pygame.Surface((largura, altura))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.velocidade = velocidade

    def update(self, dt):
        self.rect.y += self.velocidade * dt
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Level:
    def __init__(self, arquivo_json):
        with open(arquivo_json, "r") as f:
            self.data = json.load(f)
        self.plataformas_normais = pygame.sprite.Group()
        self.plataforma_base = None
        self.buracos = pygame.sprite.Group()
        self.pedras = pygame.sprite.Group()
        
        for p in self.data["platforms"]:
            if p["x"] == 0 and p["width"] == SCREEN_WIDTH:
                self.plataforma_base = PlataformaBase(p["x"], p["y"], p["width"], p["height"])
            else:
                self.plataformas_normais.add(Plataforma(p["x"], p["y"], p["width"], p["height"]))
                
        for h in self.data["holes"]:
            self.buracos.add(Buraco(h["x"], h["y"], h["width"], h["height"]))
        for stone in self.data["falling_stones"]:
            self.pedras.add(PedraCaindo(stone["x"], stone["y"], stone["width"], stone["height"], stone["speed"]))

# --------------------------------------------------
# CLASSE PRINCIPAL DO JOGO
# --------------------------------------------------
class Jogo:
    def __init__(self):
        self.diretorioPrincipal = os.path.dirname(__file__)
        self.diretorioImg = os.path.join(self.diretorioPrincipal, 'img')
        self.diretorioSons = os.path.join(self.diretorioPrincipal, 'sons')
        pygame.init()
        pygame.mixer.init()
        self.tela = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nadsuu Adventure")
        self.relogio = pygame.time.Clock()
        self.fase = 1
        self.carregar_recursos()
        self.criar_objetos()
        self.reiniciar_jogo()
        self.estado = "menu"

    def carregar_recursos(self):
        self.camadas = []
        self.posicoes_x = []
        self.velocidades = [20, 40, 60, 80, 100, 120, 140, 160]
        for i in range(1, 9):
            caminho_imagem = os.path.join(self.diretorioImg, f"camada{i}.png")
            imagem = pygame.image.load(caminho_imagem).convert_alpha()
            self.camadas.append(imagem)
            self.posicoes_x.append(0)
        self.spriteSheet = pygame.image.load(os.path.join(self.diretorioImg, 'global.png')).convert_alpha()

    def criar_objetos(self):
        self.grupoPlayer = pygame.sprite.Group()
        self.grupoInimigo = pygame.sprite.Group()
        self.level = self.carregar_fase(self.fase)

    def carregar_fase(self, fase):
        # Carrega um nível diferente dependendo da fase
        if fase == 1:
            return Level(os.path.join(self.diretorioPrincipal, "level1.json"))
        elif fase == 2:
            return Level(os.path.join(self.diretorioPrincipal, "level2.json"))
        else:
            return Level(os.path.join(self.diretorioPrincipal, "level1.json"))

    def reiniciar_jogo(self):
        self.pontuacao = 0
        self.game_over = False
        self.player = Personagem(self.spriteSheet, SCREEN_HEIGHT)
        self.grupoPlayer.empty()
        self.grupoPlayer.add(self.player)
        self.inimigo = Esqueleto(self.diretorioImg, SCREEN_HEIGHT)
        self.grupoInimigo.empty()
        self.grupoInimigo.add(self.inimigo)
        self.posicoes_x = [0 for _ in range(len(self.camadas))]

    def tratar_eventos(self, dt):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_w:
                    print("W pressionado")
                    self.player.pular()
                if evento.key == pygame.K_j:
                    self.player.set_estado('atacando')
                if self.game_over and evento.key == pygame.K_r:
                    self.reiniciar_jogo()
                    self.estado = "menu"

        teclas = pygame.key.get_pressed()
        if self.player.estado_atual != 'atacando':
            if (teclas[pygame.K_a] or teclas[pygame.K_d]) and not self.player.is_jumping and not self.player.falling:
                if teclas[pygame.K_a]:
                    print("Esquerda")
                elif teclas[pygame.K_d]:
                    print("Direita")
                self.player.set_estado('correndo')
                print("Andando")
            elif not self.player.is_jumping and not self.player.falling:
                self.player.set_estado('parado')

        min_x = 100
        max_x = SCREEN_WIDTH - 100 - self.player.rect.width
        if teclas[pygame.K_a]:
            self.player.estaOlhandoParaDireita = False
            if self.player.rect.x > min_x:
                self.player.rect.x -= 5
                self.player.pos.x = self.player.rect.x
            else:
                for idx in range(len(self.camadas)):
                    self.posicoes_x[idx] += self.velocidades[idx] * dt
                    if self.posicoes_x[idx] > 0:
                        self.posicoes_x[idx] = 0
        if teclas[pygame.K_d]:
            self.player.estaOlhandoParaDireita = True
            if self.player.rect.x < max_x:
                self.player.rect.x += 5
                self.player.pos.x = self.player.rect.x
            else:
                for idx in range(len(self.camadas)):
                    self.posicoes_x[idx] -= self.velocidades[idx] * dt
                    if self.posicoes_x[idx] <= -self.camadas[idx].get_width():
                        self.posicoes_x[idx] = 0

    def atualizar(self, dt):
        self.grupoPlayer.update(dt)
        self.grupoInimigo.update(dt)
        checar_colisoes_plataforma(self.player, self.level.plataformas_normais, self.level.plataforma_base, dt)
        # Se o personagem cair abaixo da tela (buraco), morre
        if self.player.pos.y > SCREEN_HEIGHT + 100:
            self.game_over = True
            print("Caiu no buraco!")
        # Transição de fase: se o personagem atingir a borda direita, passa para a próxima cena
        if self.player.rect.x >= SCREEN_WIDTH - 50 and self.fase == 1:
            self.fase = 2
            self.level = self.carregar_fase(self.fase)
            self.player.pos.x = 50
            self.player.rect.x = 50
            print("Transição para fase 2")
        if self.player.vidas <= 0:
            self.game_over = True

        if self.player.estado_atual == 'atacando' and self.player.rect.colliderect(self.inimigo.rect):
            self.inimigo.receber_dano(20)
            self.pontuacao += 20

    def desenhar(self, deslocamento_camera=0):
        self.tela.fill((255, 255, 255))
        # Desenha o parallax
        for idx, camada in enumerate(self.camadas):
            self.tela.blit(camada, (self.posicoes_x[idx], 0))
            self.tela.blit(camada, (self.posicoes_x[idx] + camada.get_width(), 0))
        
        # Desenha o level: plataforma base, plataformas normais, buracos e pedras
        if self.level.plataforma_base is not None:
            self.tela.blit(self.level.plataforma_base.image, (self.level.plataforma_base.rect.x - deslocamento_camera, self.level.plataforma_base.rect.y))
        for plat in self.level.plataformas_normais:
            self.tela.blit(plat.image, (plat.rect.x - deslocamento_camera, plat.rect.y))
        for buraco in self.level.buracos:
            self.tela.blit(buraco.image, (buraco.rect.x - deslocamento_camera, buraco.rect.y))
        for pedra in self.level.pedras:
            self.tela.blit(pedra.image, (pedra.rect.x - deslocamento_camera, pedra.rect.y))
        
        # Desenha os grupos de sprites
        self.grupoInimigo.draw(self.tela)
        self.grupoPlayer.draw(self.tela)
    
        if self.game_over:
            fonte = pygame.font.SysFont("Arial", 36)
            texto = fonte.render("Game Over! Pressione R para reiniciar", True, (255, 0, 0))
            self.tela.blit(texto, (50, SCREEN_HEIGHT // 2))
    
        pygame.display.flip()
        
    def executar(self):
        while True:
            dt = self.relogio.tick(FPS) / 1000.0
            self.tratar_eventos(dt)
            self.atualizar(dt)
            self.desenhar()

# Cria uma instância global de Jogo para acesso nas classes
jogo = Jogo()

if __name__ == "__main__":
    jogo.executar()
