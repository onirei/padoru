import cv2
import pygame as pg
from PIL import Image
from const import WIDTH, HEIGHT, WHITE


class Padoru:
    def __init__(self):
        # pygame init
        pg.display.set_caption('PADORU')
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode(size=(1280, 720), flags=0)
        # ascii
        self.ascii_chars = ' .,:+*?%$#@'  # 25
        self.ascii_width = 160
        self.ascii_height = 90
        # assets
        self.video_source = 'assets/video/videoplayback_360p.mp4'
        self.audio_source = 'padoru_padoru.ogg'
        self.frames = []
        pg.font.init()
        pg.mixer.init()
        self.font_size = 8
        self.ascii_font = pg.font.SysFont('Helvetica', self.font_size)
        self.font = pg.font.SysFont('arialunicode', 32)
        self.sound = pg.mixer.Sound('assets/audio/padoru_padoru.ogg')

    def redraw(self, img):
        image = Image.fromarray(img)
        image = image.resize((self.ascii_width, self.ascii_height))
        image = image.convert(mode="L", )
        pixels = image.getdata()
        ascii_str = ''.join(self.ascii_chars[pixel // 25] for pixel in pixels)
        ascii_str_len = len(ascii_str)
        ascii_img = ''.join(
            ascii_str[i:i + self.ascii_width] + '\n' for i in range(0, ascii_str_len, self.ascii_width)
        )
        return ascii_img

    @staticmethod
    def play_animation(len_frames: int, delay: int = 1):
        i = 0
        while True:
            i = 0 if i == len_frames * delay else i
            yield i // delay
            i += 1

    def preload(self):
        self.screen.fill((255, 255, 255))
        loader = 1
        cap = cv2.VideoCapture(self.video_source)
        success, img = cap.read()

        sheet = pg.image.load('assets/sprites/padoru_sprite_sheet.png').convert()
        sheet = pg.transform.scale(sheet, (640, 160))
        x_list = (0, 160, 320, 480)
        tick = self.play_animation(len_frames=len(x_list), delay=2)
        while success:
            self.clock.tick(30)
            self.screen.fill((0, 0, 0))
            success, img = cap.read()
            if not success:
                break
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
            img_cv2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            ascii_img: str = self.redraw(img=img_cv2)
            lines = ascii_img.splitlines()
            image = pg.Surface((1280, 720))
            for i, line in enumerate(lines):
                for j, char in enumerate(line):
                    image.blit(self.ascii_font.render(char, False, WHITE), (self.font_size * j, self.font_size * i))
            im = cv2.resize(img, (320, 180), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
            image.blit(pg.image.frombuffer(im.tobytes(), (320, 180), "BGR"), (0, 0))
            self.frames.append(image)

            sprite = pg.Surface((160, 160))
            sprite.set_colorkey((0, 0, 0))
            sprite.blit(sheet, (0, 0), (x_list[next(tick)], 0, 160, 160))
            self.screen.blit(sprite, (1110, 550))

            loader += 1  # 339
            percent = round(loader / 339 * 100, 1)
            text = self.font.render(str(f'{percent}%'), False, WHITE)
            self.screen.blit(text, ((WIDTH - text.get_rect().width)/2, HEIGHT/2-16))
            pg.display.update()

    def play(self):
        self.sound.play()
        frame_count = 0
        success = True
        while success and frame_count < len(self.frames):
            self.clock.tick(30)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
            self.screen.fill((0, 0, 0))
            self.screen.blit(self.frames[frame_count], (0, 0))
            pg.display.update()
            frame_count += 1
        replay_text = self.font.render('Replay?', False, WHITE)
        replay_rect = replay_text.get_rect()
        replay_rect.center = (WIDTH / 2, HEIGHT / 2)
        y_list = (HEIGHT/2, HEIGHT/2-2, HEIGHT/2-4, HEIGHT/2-2, HEIGHT/2, HEIGHT/2+3, HEIGHT/2+6)
        tick = self.play_animation(len_frames=len(y_list), delay=3)
        while True:
            self.clock.tick(30)
            if replay_rect.collidepoint(pg.mouse.get_pos()):
                replay_text = self.font.render('Replay?', False, (220, 220, 220))
            else:
                replay_text = self.font.render('Replay?', False, WHITE)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and replay_rect.collidepoint(event.pos):
                    self.play()
            self.screen.fill((0, 0, 0))
            replay_rect.y = y_list[next(tick)]
            self.screen.blit(replay_text, replay_rect)
            pg.display.update()
