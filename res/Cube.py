import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image, ImageSequence

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

textures = []
gif_paths = ['gifs/bici.gif','gifs/bros.gif','gifs/escoba.gif','gifs/hambriento.gif','gifs/musico.gif','gifs/reza.gif']
gif_frames = []
frame_counter = 0

def load_gif_texture(path):
    img = Image.open(path)
    frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(img)]
    return frames

def init_colors():
    glEnable(GL_DEPTH_TEST)

def draw_cube():
    glBegin(GL_QUADS)
    for i, surface in enumerate(surfaces):
        glBindTexture(GL_TEXTURE_2D, textures[i])
        for vertex in surface:
            if vertex % 2 == 0:
                glTexCoord2f(0, 0)
            else:
                glTexCoord2f(1, 1)
            glVertex3fv(vertices[vertex])
    glEnd()

    glBegin(GL_LINES)
    glColor3fv((0, 0, 0))
    for edge in aristas:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def update_textures():
    global frame_counter
    frame_counter += 1
    for i, frames in enumerate(gif_frames):
        frame = frames[frame_counter % len(frames)]
        glBindTexture(GL_TEXTURE_2D, textures[i])
        img_data = np.array(frame.getdata(), np.uint8)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, frame.size[0], frame.size[1], GL_RGBA, GL_UNSIGNED_BYTE, img_data)

""" def draw_cube():
    glBegin(GL_QUADS)
    for i, surface in enumerate(surfaces):
        glColor3fv(colors[i])
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()

    glBegin(GL_LINES)
    glColor3fv((0, 0, 0))
    for edge in aristas:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd() """

def draw_square():
    glBegin(GL_LINES)
    for edge in aristas:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def load_texture(image):
    texture_surface = pygame.image.load(image)
    texture_data = pygame.image.tostring(texture_surface, "RGB", True)
    width, height = texture_surface.get_size()
    
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    return texture_id

def init_textures():
    global gif_frames
    gif_frames = [load_gif_texture(gif_path) for gif_path in gif_paths]

    glEnable(GL_TEXTURE_2D)
    for i, frames in enumerate(gif_frames):
        texture_id = glGenTextures(1)
        textures.append(texture_id)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        # Cargar la primera imagen del gif
        img_data = np.array(frames[0].getdata(), np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, frames[0].size[0], frames[0].size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

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
    global gif_paths
    dragging = False
    closest_vertex = -1
    pygame.init()

    # Configurar el modo de pantalla completa
    """ info = pygame.display.Info()
    display = (info.current_w, info.current_h)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | FULLSCREEN) """

    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    init_colors()

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    # Configuración de la cámara
    gluLookAt(0.0, 2.0, 3.0,  # Posición de la cámara
              0.0, 0.0, 0.0,  # Punto al que se mira
              0.0, 1.0, 0.0)  # Vector "arriba"
    glTranslatef(0.0,-1.0, -2.0)
    glRotatef(45,0,5,0)

    init_textures()

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

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_cube()
        update_textures()
        pygame.display.flip()
        pygame.time.wait(100)

main()