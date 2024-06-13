import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np

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

edges = [
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

textures = []

########## VIDEO ############
def load_video_texture(video_path):
    player = pyglet.media.Player()
    source = pyglet.media.load(video_path)
    player.queue(source)
    player.play()
    return player

def update_video_texture(player, texture_id):
    if player.source and player.source.video_format:
        image = player.get_texture().get_image_data()
        texture_data = image.get_data('RGB', image.width * 3)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, image.width, image.height, GL_RGB, GL_UNSIGNED_BYTE, texture_data)

#############################
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
    global textures
    textures.append(load_texture("blue.jpeg"))
    textures.append(load_texture("red.jpeg")) #Cara derecha
    textures.append(load_texture("blue.jpeg"))
    textures.append(load_texture("green.jpeg")) #Cara Superior
    textures.append(load_texture("blue.jpeg"))
    textures.append(load_texture("blue.jpeg")) #Cara izquierda

selected_vertex = None
def draw_cube():
    glEnable(GL_TEXTURE_2D)
    for i, surface in enumerate(surfaces):
        glBindTexture(GL_TEXTURE_2D, textures[i])
        glBegin(GL_QUADS)
        for vertex in surface:
            if vertex == 0:
                glTexCoord2f(0, 0)
            elif vertex == 1:
                glTexCoord2f(1, 0)
            elif vertex == 2:
                glTexCoord2f(1, 1)
            elif vertex == 3:
                glTexCoord2f(0, 1)
            glVertex3fv(vertices[vertex])
        glEnd()
    glDisable(GL_TEXTURE_2D)

def draw_square():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()


def update_vertex_with_mouse_drag(vertices, indice, mouse_x, mouse_y):
    # Aquí implementas la lógica para actualizar el vértice según el arrastre
    new_vertex_x, new_vertex_y, new_vertex_z = screen_to_object_coords(mouse_x, mouse_y, 800, 600)
    _,_,new_vertex_z = vertices[indice]
    vertices[indice] = (new_vertex_x,new_vertex_y,new_vertex_z)
    return (new_vertex_x, new_vertex_y, new_vertex_z)

def screen_to_object_coords(mouse_x, mouse_y, screen_width, screen_height):
    x = 2.0 * mouse_x / screen_width - 1.0
    y = 1.0 - 2.0 * mouse_y / screen_height
    z = 0.0  # La coordenada z es 0 en este caso, ya que la conversión es 2D
    return (x, y, z)

# Función que obtiene el índice del vértice del cuadrado bajo el mouse
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

# Variables para controlar el estado del arrastre del mouse
dragging = False
mouse_x, mouse_y = 0, 0
vertex_index = -1  # Índice del vértice actual que se está arrastrando

def init_window(width, height):
    pygame.init()
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    gluPerspective(45, (width / height), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)
    glRotatef(30, 1, 0, 0)  # Rotar 30 grados alrededor del eje X global
    glRotatef(45, 0, 1, 0)  # Rotar 45 grados alrededor del eje Y global


    glEnable(GL_DEPTH_TEST)  # Enable depth testing

def main():
    global selected_vertex
    
    init_window(800, 600)

    # Variables para controlar el estado del arrastre del mouse
    dragging = False
    mouse_x, mouse_y = 0, 0
    #print(pyglet.options['audio'])
    init_textures()

    #################
    #video_player = load_video_texture("videoplayback-_1_.webm")  # Replace with your video path
    #video_texture_id = glGenTextures(1)
    #glBindTexture(GL_TEXTURE_2D, video_texture_id)
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    #last_update_time = time.time()
    #update_interval = 1/30  # Actualizar la textura del video 30 veces por segundo
    #################

    #print(textures)
    while True:
        #######
        #current_time = time.time()
        #if current_time - last_update_time >= update_interval:
        #    update_video_texture(video_player, video_texture_id)
        #    last_update_time = current_time
        #######
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Botón izquierdo del mouse
                    dragging = True
                    mouse_x, mouse_y = event.pos
                    vertex_index = get_vertex_under_mouse(mouse_x, mouse_y, vertices)
                    print(f"Vertex under mouse click: {vertex_index}")
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:  # Botón izquierdo del mouse
                    dragging = False
                    vertex_index = -1 
            elif event.type == MOUSEMOTION:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    vertex = update_vertex_with_mouse_drag(vertices, vertex_index, mouse_x, mouse_y)
                    print(f"Mouse coordinates while dragging: {mouse_x}, {mouse_y}")
                    print(f"Updated vertex while dragging: {vertex}")
                    print(vertices)
    

        #glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_cube()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()