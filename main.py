import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame, math
pygame.init()

WH_RATIO = 6/5
W = 1200
H = int(W // WH_RATIO)
FPS = 60

screen_fullscreen_info = pygame.display.Info()
MAX_W, MAX_H = screen_fullscreen_info.current_w, screen_fullscreen_info.current_h

win = pygame.display.set_mode((W, H))#, pygame.RESIZABLE)
pygame.display.set_caption("Tower Defence")

#COLOURS

BLACK = (0,0,0)
GREY = (200, 200, 200)
RED = (150, 20, 20)


file_name = os.path.basename(__file__)
assets_path = os.path.abspath(__file__)[:-len(file_name)] + "assets\\"

def make_image(name, size):
    return pygame.transform.scale(pygame.image.load(assets_path + name), size)

cursor = make_image("cursor.png", (32, 32))
cursor_mask = pygame.mask.Mask((1, 1), True)

def check_quit():

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
    return False



def launch_screen(clock):
    pygame.mouse.set_visible(False)
    frame_count = 0

    bg = make_image("launch background.png", (W, H))

    title_width, title_height = W * 0.8, H * 0.5
    title_jiggle_speed = 0.1875
    title_sine_amplitude = 5

    original_ycor = H / 20
    title_xcor = W / 2 - title_width / 2
    title_ycor = original_ycor

    title = make_image("launch title.png", (title_width, title_height))

    play_button_width = title_width * 0.5
    play_button_height = title_height // 3
    play_button_xcor, play_button_ycor = W * 0.5 - play_button_width * 0.5, H - H // 3

    play_button = make_image("launch play.png", (play_button_width, play_button_height))
    play_button_mask = pygame.mask.from_surface(play_button)

    play_button_multiplier = 1.1
    enlarged_button_width = play_button_width * play_button_multiplier
    enlarged_button_height = play_button_height * play_button_multiplier

    enlarged_button = pygame.transform.scale(play_button, (enlarged_button_width, enlarged_button_height))
    enlarged_button_xcor = play_button_xcor - (enlarged_button_width - play_button_width) / 2
    enlarged_button_ycor = play_button_ycor - (enlarged_button_height - play_button_height) / 2

    while True:
        clock.tick(FPS)

        title_ycor = original_ycor + math.sin(frame_count * title_jiggle_speed) * title_sine_amplitude
        frame_count += 1

        mouse_xcor, mouse_ycor = pygame.mouse.get_pos()
        cursor_overlapping_play_button = cursor_mask.overlap(play_button_mask, (play_button_xcor - mouse_xcor, play_button_ycor - mouse_ycor))

        if cursor_overlapping_play_button:
            blitted_play_button = enlarged_button
            blitted_play_button_xcor = enlarged_button_xcor
            blitted_play_button_ycor = enlarged_button_ycor

            if pygame.mouse.get_pressed()[0]:
                return True
        else:
            blitted_play_button = play_button
            blitted_play_button_xcor = play_button_xcor
            blitted_play_button_ycor = play_button_ycor

        win.blit(bg, (0,0))
        win.blit(title, (title_xcor, title_ycor))
        win.blit(blitted_play_button, (blitted_play_button_xcor, blitted_play_button_ycor))
        win.blit(cursor, (mouse_xcor, mouse_ycor))

        pygame.display.flip()

        if check_quit():
            return False
        

def lock_animation(lock_xcor, frame):
    duration_direction = FPS / 20
    length = 2
    add_frames = True
    
    if frame < duration_direction:
        lock_xcor += length
    elif frame < duration_direction * 2:
        lock_xcor -= length
    elif frame < duration_direction * 3:
        lock_xcor -= length
    elif frame < duration_direction * 4:
        lock_xcor += length
    else:
        add_frames = False

    return lock_xcor, add_frames
        

def load_levels(clock, player_level):
    frame = 0
    denial_frame = 0

    page = 1
    pages = 5

    insert_animation = False

    bg = make_image("map bg.png", (W, H))


    # PAGE TEXT AND PAGE COUNT
    page_text_width = 194
    page_text_height = page_text_width / 2

    page_text = make_image("page text.png", (page_text_width, page_text_height))

    nums_width = page_text_width * 0.25
    nums_height = page_text_height
    nums = [make_image(f"{i + 1}.png", (nums_width, nums_height)) for i in range(pages)]

    page_nums_gap = 20

    page_text_xcor = W / 2 - (page_text_width + page_nums_gap + nums_width) / 2
    page_text_ycor = 80

    nums_xcor = page_text_xcor + page_text_width + page_nums_gap
    nums_ycor = page_text_ycor


    # LEVEL IMAGES
    level_width = W * 0.22
    level_height = level_width * 0.6

    num_horizontal_levels, num_vertical_levels = 3, 3
    level_xpadding = (W - num_vertical_levels * level_width) / (num_vertical_levels + 1)
    level_ypadding = (H - num_horizontal_levels * level_height) / (2 * (num_horizontal_levels + 1))
    y_start = (H - num_horizontal_levels * level_height) / (num_horizontal_levels + 1)

    levels = []
    original_levels_cors = []
    levels_mask = []

    for i in range(num_horizontal_levels * num_vertical_levels):
        try:
            level = make_image(f"level {i + 1} image.png", (level_width, level_height))

            levels.append(level)
            levels_mask.append(pygame.mask.from_surface(level))

            xcor = level_xpadding * (i % num_vertical_levels + 1) + level_width * (i % num_vertical_levels)
            ycor = level_ypadding * (i // num_horizontal_levels + 1) + level_height * (i // num_horizontal_levels) + y_start

            original_levels_cors.append((xcor, ycor))

        except FileNotFoundError:
            continue

    for level in levels[player_level:]:
        level.set_alpha(100)

    bottom_level_bottom_ycor = original_levels_cors[7][1] + level_height

    changing_cors = [list(cors) for cors in original_levels_cors]
    
    rect_outline_width = 3
    outline_radius = 20


    # BACK BUTTON
    back_btn_width = W * 0.11
    back_btn_height = back_btn_width / 2

    back_btn_xcor = W * 0.5 - back_btn_width * 0.5
    back_btn_ycor = (H - bottom_level_bottom_ycor - back_btn_height) / 2 + bottom_level_bottom_ycor

    back_btn = make_image("back text.png", (back_btn_width, back_btn_height))
    back_btn_outline_width = 6
    back_btn_rect = pygame.rect.Rect(

        back_btn_xcor - back_btn_outline_width / 2, 
        back_btn_ycor - back_btn_outline_width / 2, 
        back_btn_width + back_btn_outline_width, 
        back_btn_height + back_btn_outline_width
        )
    
    
    # LOCKS
    lock_width = level_width * 0.4
    lock_height = level_height * 0.6
    lock = make_image("lock.png", (lock_width, lock_height))

    original_lock_cors = [[cors[0] + level_width / 2 - lock_width / 2, cors[1] + level_height / 2 - lock_height / 2] for cors in changing_cors][player_level::]
    changing_lock_cors = original_lock_cors.copy()


    # RIGHT/LEFT ARROWS
    arrow_width = back_btn_width * 0.75
    arrow_height = back_btn_height * 0.75
    arrow_back_btn_gap = 20

    right_arrow = make_image("arrow.png", (arrow_width, arrow_height))
    right_arrow_mask = pygame.mask.from_surface(right_arrow)
    left_arrow = pygame.transform.rotate(right_arrow, 180)
    left_arrow_mask = pygame.mask.from_surface(left_arrow)

    right_arrow_incative = False
    left_arrow_incative = False

    right_arrow_cors = (back_btn_xcor + back_btn_width + arrow_back_btn_gap, back_btn_ycor + back_btn_height / 2 - arrow_height / 2)
    left_arrow_cors = (back_btn_xcor - arrow_back_btn_gap - arrow_width, back_btn_ycor + back_btn_height / 2 - arrow_height / 2)

    while True:
        clock.tick(FPS)

        mouse_xcor, mouse_ycor = pygame.mouse.get_pos()
        cursor_rect = pygame.rect.Rect(mouse_xcor, mouse_ycor, 1, 1)

        frame += 1
        #sin_frame = math.sin(frame * 0.02) * 10

        win.blit(bg, (0,0))

        pressed = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pressed = True

            elif event.type == pygame.QUIT:
                return False  

        for i, (level, cors, mask) in enumerate(zip(levels, changing_cors, levels_mask)):
            #cors[1] = original_levels_cors[i][1] + sin_frame
            win.blit(level, cors)

            if cursor_mask.overlap(mask, (cors[0] - mouse_xcor, cors[1] - mouse_ycor)):
                outline_rect = pygame.rect.Rect(cors[0] - rect_outline_width * 0.5, cors[1] - rect_outline_width * 0.5, level_width + rect_outline_width, level_height + rect_outline_width)

                if i >= player_level:
                    colour = RED
                    if pressed:
                        insert_animation = True
                        chosen_lock_index = i - 1
                else:
                    colour = GREY
                    if pressed:
                        return True

                pygame.draw.rect(win, colour, outline_rect, rect_outline_width, outline_radius)

        if insert_animation:
            changing_lock_cors[chosen_lock_index][0], add_frames = lock_animation(changing_lock_cors[chosen_lock_index][0], denial_frame)
            if add_frames:
                denial_frame += 1
            else:
                insert_animation = False
                denial_frame = 0


        for i, cors in enumerate(changing_lock_cors):
            #cors[1] = original_lock_cors[i][1] + sin_frame
            win.blit(lock, cors)

        if cursor_rect.colliderect(back_btn_rect):
            pygame.draw.rect(win, BLACK, back_btn_rect, back_btn_outline_width, outline_radius // 2)
            if pressed:
                return "b"
            
        win.blit(back_btn, (back_btn_xcor, back_btn_ycor))

        left_arrow_incative = (page == 1)
        right_arrow_incative = (page == pages)

        right_arrow.set_alpha(50 if right_arrow_incative else 255)
        left_arrow.set_alpha(50 if left_arrow_incative else 255)   
            
        if not left_arrow_incative and cursor_mask.overlap(left_arrow_mask, (left_arrow_cors[0] - mouse_xcor, left_arrow_cors[1] - mouse_ycor)):
            left_arrow.set_alpha(150)
            if pressed:
                page -= 1


        if not right_arrow_incative and cursor_mask.overlap(right_arrow_mask, (right_arrow_cors[0] - mouse_xcor, right_arrow_cors[1] - mouse_ycor)):
            right_arrow.set_alpha(150)
            if pressed:
                page += 1


        win.blit(left_arrow, left_arrow_cors)
        win.blit(right_arrow, right_arrow_cors)

        win.blit(page_text, (page_text_xcor, page_text_ycor))
        win.blit(nums[page - 1], (nums_xcor, nums_ycor))
        win.blit(cursor, (mouse_xcor, mouse_ycor))
        
        pygame.display.flip()
        

def play_level(bg_mask, bg, clock):
    alpha = 0
    bg.set_alpha(alpha)
    increment = 255 / FPS * 2

    done_time = 0

    while done_time < FPS:
        clock.tick(FPS)

        win.blit(bg, (0,0))
        
        if alpha < 255:
            alpha += increment
        else:
            done_time += increment
        
        bg.set_alpha(alpha)

        pygame.display.flip()

        if check_quit():
            return False

    acceptable_dist_track = 5

    tower_slots_height = 100
    tower_slots = make_image("tower slots.png", (W, tower_slots_height))

    tower_slots_xcor = 0
    tower_slots_ycor = H - tower_slots_height



    click_width = 100
    click_height = 25
    dropdown_click = make_image("dropdown click.png", (click_width, click_height))
    click_mask = pygame.mask.from_surface(dropdown_click)
    
    click_xcor = W / 2 - click_width / 2
    click_ycor = tower_slots_ycor - click_height

    while True:
        clock.tick(FPS)
        #print(clock.get_fps())

        mouse_xcor, mouse_ycor = pygame.mouse.get_pos()

        win.blit(bg, (0,0))
        win.blit(tower_slots, (tower_slots_xcor, tower_slots_ycor))
        win.blit(dropdown_click, (click_xcor, click_ycor))

        if cursor_mask.overlap(click_mask, (click_xcor - mouse_xcor, click_ycor - mouse_ycor)):
            dropdown_click.set_alpha(200)
        else:
            dropdown_click.set_alpha(255)

        win.blit(cursor, (mouse_xcor, mouse_ycor))

        for dx in range(-acceptable_dist_track, acceptable_dist_track + 1):
            for dy in range(-acceptable_dist_track, acceptable_dist_track + 1):
                if cursor_mask.overlap(bg_mask, (-mouse_xcor + dx, -mouse_ycor + dy)): #NEEDS CHANGE FOR WHEN DRAGGING TOWER +W/2 +H/2 TO OFFSET
                    pass

        pygame.display.flip()

        if check_quit():
            return False
        

def main():
    clock = pygame.time.Clock()
    level = 1

    levels_made = 1
    levels_bgs = [pygame.mask.from_surface(make_image(f"level {i  + 1} mask.png", (W, H))) for i in range(levels_made)]
    bg_levels = [make_image(f"bg{i + 1} background.png", (W,H)) for i in range(levels_made)]
    
    run = launch_screen(clock)
    pygame.mouse.set_visible(False)

    while run:
        clock.tick(FPS)

        setup = True
        while setup:
            game_playing = load_levels(clock, level)

            if not game_playing:
                setup = False
                run = False
            elif game_playing == "b":
                if not launch_screen(clock):
                    run = False
                    game_playing = False
                    setup = False
            else:
                setup = False
        
        if run:
            game_playing = play_level(levels_bgs[0], bg_levels[0], clock)
            if not game_playing:
                run = False
                break

    print("Thanks for playing")
    pygame.quit()
    

if __name__ == "__main__":
    main()
