import pygame

pygame.init()


class Text:
    def __init__(self, font, pos, text, color=[0, 0, 0], center=False):
        self.font = font
        self.x = pos[0]
        self.y = pos[1]
        self.text = text
        self.color = color
        self.center = center

    def render(self, screen):
        text = self.font.render(self.text, True, self.color)
        text_rect = text.get_rect()
        if self.center:
            text_rect.centerx = self.x
        else:
            text_rect.x = self.x
        if self.center:
            text_rect.centery = self.y
        else:
            text_rect.y = self.y 
        screen.blit(text, text_rect)
