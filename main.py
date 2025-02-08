import pygame
import sys
import os

# Diretórios (ajuste conforme necessário)
diretorioPrincipal = os.path.dirname(__file__)
diretorioImg = os.path.join(diretorioPrincipal, 'img')
diretorioSons = os.path.join(diretorioPrincipal, 'sons')

pygame.init()
screen_width, screen_height = 640, 360
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Nadsuu Adventure")

spriteSheet = pygame.image.load(os.path.join(diretorioImg, 'global.png')).convert_alpha()

class Personagem(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        # Cria um dicionário para armazenar as animações.
        # Cada chave representa um estado (ex: 'parado', 'andando')
        # e o valor é uma lista com os frames da animação.
        
        self.animacoes = {
            'parado': [],
            'andando': []
        }
        
        # Carrega os frames da animação 'parado'
        for i in range(2):
            img = spriteSheet.subsurface((i * 32, 0), (32, 32))
            img = pygame.transform.scale(img, (49 * 3, 32 * 3))
            self.animacoes['parado'].append(img)
            
        # Carrega os frames da animação 'andando'
        # Supondo que os frames de "andando" estejam na segunda linha do spritesheet.
        for i in range(2):
            img = spriteSheet.subsurface((i * 32, 32), (49, 32))
            img = pygame.transform.scale(img, (49 * 3, 32 * 3))
            self.animacoes['andando'].append(img)
        
        # Define o estado inicial e os atributos da animação
        self.estado_atual = 'parado'
        self.index = 0
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        self.rect = self.image.get_rect()
        self.rect.center = (100, 100)
        
    def update(self, dt):
        # dt é o delta time (tempo decorrido entre frames)
        # Use-o para controlar a velocidade da animação de forma independente do FPS.
        velocidade_animacao = 5  # ajuste conforme necessário
        self.index += velocidade_animacao * dt
        
        # Se o índice passar do número de frames, reseta para reiniciar a animação
        if self.index >= len(self.animacoes[self.estado_atual]):
            self.index = 0
            
        self.image = self.animacoes[self.estado_atual][int(self.index)]
        
    def set_estado(self, novo_estado):
        # Muda o estado do personagem se for diferente do atual
        if novo_estado in self.animacoes and novo_estado != self.estado_atual:
            self.estado_atual = novo_estado
            self.index = 0

# Grupo de sprites
globalsprites = pygame.sprite.Group()
prota = Personagem()
globalsprites.add(prota)

clock = pygame.time.Clock()

while True:
    dt = clock.tick(30) / 1000.0  # Delta time em segundos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Exemplo: mudar estado com as setas
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                prota.set_estado('andando')
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                prota.set_estado('parado')
    
    globalsprites.update(dt)
    screen.fill((255, 255, 255))
    globalsprites.draw(screen)
    pygame.display.flip()
