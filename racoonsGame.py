import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

vertices = [
    (-1, -1, -1),
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, 1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, 1, 1)
]

aristas = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7)
]

surfaces = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 1, 5, 4),
    (2, 3, 7, 6),
    (1, 2, 6, 5),
    (4, 0, 3, 7)
]

# Definición de colores para cada cara del cubo
colors = [
    (1, 0, 0),  # Rojo
    (0, 1, 0),  # Verde
    (0, 0, 1),  # Azul
    (1, 1, 0),  # Amarillo
    (1, 0, 1),  # Magenta
    (0, 1, 1)   # Cian
]

gif_paths = ['gifs/bici.gif','gifs/bros.gif','gifs/escoba.gif','gifs/hambriento.gif','gifs/musico.gif','gifs/uvas.gif']

# Posiciones iniciales de las texturas del cubo
texture_indices = list(range(len(gif_paths)))

def shuffle_textures():
    global texture_indices
    texture_indices = texture_indices[1:] + [texture_indices[0]] 

def load_gif_texture(image_path):
    gif = Image.open(image_path)
    frames = []
    try:
        while True:
            frame = gif.copy()
            frame_data = frame.convert("RGBA").tobytes()
            frames.append((frame.size, frame_data))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames

def init_textures():
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return texture_id

def update_textures(texture_id, frame):
    size, data = frame
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size[0], size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

def draw_cube(textures):
    for i, surface in enumerate(surfaces):
        glBindTexture(GL_TEXTURE_2D, textures[i])
        glBegin(GL_QUADS)
        for i, vertex in enumerate(surface):
            if i == 0:
                glTexCoord2f(0, 1)
            elif i == 1:
                glTexCoord2f(1, 1)
            elif i == 2:
                glTexCoord2f(1, 0)
            elif i == 3:
                glTexCoord2f(0, 0)
            glVertex3fv(vertices[vertex])
        glEnd()

    glBegin(GL_LINES)
    for edge in aristas:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def get_vertex_under_mouse(mouse_x, mouse_y, vertices):
    viewport = glGetIntegerv(GL_VIEWPORT)
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    
    min_distance = float('inf')
    closest_vertex_index = -1
    
    for i, vertex in enumerate(vertices):
        screen_coords = gluProject(vertex[0], vertex[1], vertex[2], modelview, projection, viewport)
        distance = ((screen_coords[0] - mouse_x) ** 2 + (screen_coords[1] - (viewport[3] - mouse_y)) ** 2) ** 0.5
        if distance < min_distance:
            min_distance = distance
            closest_vertex_index = i
            
    if min_distance < 10:  # Tolerance threshold
        return closest_vertex_index
    else:
        return -1

def update_vertex_with_mouse_drag(vertices, indice, mouse_x, mouse_y):
    # Aquí implementas la lógica para actualizar el vértice según el arrastre
    viewport = glGetIntegerv(GL_VIEWPORT)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)

    mouse_y = viewport[3] - mouse_y

    mouse_pos = gluUnProject(mouse_x, mouse_y, 0, modelview, projection, viewport)

    vertices[indice] = mouse_pos

def main():
    dragging = False
    closest_vertex = -1
    pygame.init()

    # Configurar el modo de pantalla completa
    info = pygame.display.Info()
    display = (info.current_w, info.current_h)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN)

    """ display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL) """

    pygame.mixer.init()
    pygame.mixer.music.load('arn94.mp3')
    pygame.mixer.music.play()

    # Cargar los frames de todos los GIFs
    all_gif_frames = [load_gif_texture(path) for path in gif_paths]
    num_gifs = len(all_gif_frames)
    gif_indices = [0] * num_gifs

    # Crear texturas para cada GIF
    texture_ids = [init_textures() for _ in gif_paths]

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)

    # Configuración de la cámara
    gluLookAt(0.0, 2.0, 3.0,  # Posición de la cámara
            0.0, 0.0, 0.0,  # Punto al que se mira
            0.0, 1.0, 0.0)  # Vector "arriba"
    glTranslatef(0.0,-1.0, -2.0)
    glRotatef(45,0,5,0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)

    running = True
    while running:
        for event in pygame.event.get():    
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                dragging = True
                x, y = event.pos
                closest_vertex = get_vertex_under_mouse(x, y, vertices)
                print("Closest Vertex:", closest_vertex)
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                closest_vertex = -1
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    x, y = event.pos
                    vertex = update_vertex_with_mouse_drag(vertices, closest_vertex, x, y)
                    print(f"Mouse coordinates while dragging: {x}, {y}")
                    print(f"Updated vertex while dragging: {vertex}")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    shuffle_textures()

        for i in range(num_gifs):
            frames = all_gif_frames[texture_indices[i]]
            update_textures(texture_ids[i], frames[gif_indices[texture_indices[i]]])
            gif_indices[texture_indices[i]] = (gif_indices[texture_indices[i]] + 1) % len(frames)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        draw_cube(texture_ids)
        pygame.display.flip()
        pygame.time.wait(100)

if __name__ == "__main__":
    main()