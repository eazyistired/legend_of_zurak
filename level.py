import pygame
from settings import tile_size, screen_width, screen_height
from tiles import *
from player import *
from enemy import Enemy
from particles import ParticleEffect
from decoration import *
from support import import_csv_layout, import_cut_graphic
from game_data import levels


class Level:
    def __init__(self, current_level, surface, create_overworld):
        # level setup
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = 0
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']
        self.create_overworld = create_overworld

        # Player
        self.player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(self.player_layout)

        # Terrain setup
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')

        # Grass setup
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')

        # Enemy
        enemy_layout = import_csv_layout(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')

        # Crates setup
        crate_layout = import_csv_layout(level_data['crates'])
        self.crate_sprites = self.create_tile_group(crate_layout, 'crates')

        # Coins setup
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')

        # Fb palms
        fg_palm_layout = import_csv_layout(level_data['fg palms'])
        self.fg_palms_sprites = self.create_tile_group(fg_palm_layout, 'fg palms')

        # Bg palms
        bg_palm_layout = import_csv_layout(level_data['bg palms'])
        self.bg_palms_sprites = self.create_tile_group(bg_palm_layout, 'bg palms')

        # Constraints setup
        constraints_layout = import_csv_layout(level_data['constraints'])
        self.constraints_sprites = self.create_tile_group(constraints_layout, 'constraints')

        # Dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # Decoration
        self.sky = Sky(8)
        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 35, level_width)
        self.clouds = Clouds(400, level_width, 20)

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size

                if cell == '0':
                    self.player.add(Player((x, y), self.display_surface, self.crate_jump_particles))
                elif cell == '1':
                    hat_surface = pygame.image.load('./graphics/character/hat.png')
                    self.goal.add(StaticTile((x, y), tile_size, hat_surface))

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                if cell != '-1':
                    x = col_index * tile_size
                    y = row_index * tile_size

                    sprite = StaticTile
                    if type == 'terrain':
                        terrain_tile_list = import_cut_graphic('./graphics/terrain/terrain_tiles.png')
                        tile_surface = terrain_tile_list[int(cell)]
                        sprite = StaticTile((x, y), tile_size, tile_surface)
                    elif type == 'grass':
                        grass_tile_list = import_cut_graphic('./graphics/decoration/grass/grass.png')
                        tile_surface = grass_tile_list[int(cell)]
                        sprite = StaticTile((x, y), tile_size, tile_surface)
                    elif type == 'crates':
                        sprite = Crate((x, y), tile_size)
                    elif type == 'coins':
                        if cell == '0':
                            sprite = Coin((x, y), tile_size, './graphics/coins/gold')
                        elif cell == '1':
                            sprite = Coin((x, y), tile_size, './graphics/coins/silver')
                    elif type == 'fg palms':
                        if cell == '0':
                            sprite = PalmTree((x, y), tile_size, './graphics/terrain/palm_small', 38)
                        elif cell == '1':
                            sprite = PalmTree((x, y), tile_size, './graphics/terrain/palm_large', 70)
                    elif type == 'bg palms':
                        sprite = PalmTree((x, y), tile_size, './graphics/terrain/palm_bg', 64)
                    elif type == 'enemies':
                        sprite = Enemy((x, y), tile_size, './graphics/enemy/run')
                    elif type == 'constraints':
                        sprite = Tile((x, y), tile_size)

                    sprite_group.add(sprite)

        return sprite_group

    def crate_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)

        jump_particle_sprite = ParticleEffect(pos, 'jump')
        self.dust_sprite.add(jump_particle_sprite)

    def create_land_particles(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > 3 * screen_width / 4 and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.move()

        collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palms_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            player.on_left = False
        if player.on_right and (player.rect.right > self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        collidable_sprites = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palms_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y > 1 or player.direction.y < 0:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

    def enemy_collision(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraints_sprites, False):
                enemy.reverse()

    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level, 0)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level, self.new_max_level)

    def run(self):
        # Input

        # Decoration
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        # Scroll
        self.scroll_x()

        # Player
        self.player.update()
        self.horizontal_movement_collision()
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_land_particles()
        self.player.draw(self.display_surface)

        # Goal
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        # Bg palms
        self.bg_palms_sprites.update(self.world_shift)
        self.bg_palms_sprites.draw(self.display_surface)

        # Dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # Terrain
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        # Enemy
        self.enemy_sprites.update(self.world_shift)
        self.enemy_sprites.draw(self.display_surface)

        # Constraints
        self.constraints_sprites.update(self.world_shift)
        self.enemy_collision()

        # Crates
        self.crate_sprites.update(self.world_shift)
        self.crate_sprites.draw(self.display_surface)

        # Grass
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw((self.display_surface))

        # Coins
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)

        # Fg palms
        self.fg_palms_sprites.update(self.world_shift)
        self.fg_palms_sprites.draw(self.display_surface)

        # Water
        self.water.draw(self.display_surface, self.world_shift)

        # Check death/win condition
        self.check_death()
        self.check_win()
