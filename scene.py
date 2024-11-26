import math
import glm
import numpy as np
import geometry as geom
import helperclasses as hc
from tqdm import tqdm

class Scene:

    def __init__(self,
                 width: int,
                 height: int,
                 jitter: bool,
                 samples: int,
                 eye_position: glm.vec3,
                 lookat: glm.vec3,
                 up: glm.vec3,
                 fov: float,
                 ambient: glm.vec3,
                 lights: list[hc.Light],
                 objects: list[geom.Geometry]
                 ):
        self.width = width  # width of image
        self.height = height  # height of image
        self.aspect = width / height  # aspect ratio
        self.jitter = jitter  # should rays be jittered
        self.samples = samples  # number of rays per pixel
        self.eye_position = eye_position  # camera position in 3D
        self.lookat = lookat  # camera look at vector
        self.up = up  # camera up position
        self.fov = fov  # camera field of view
        self.ambient = ambient  # ambient lighting
        self.lights = lights  # all lights in the scene
        self.objects = objects  # all objects in the scene

    def render(self):

        image = np.zeros((self.height, self.width, 3)) # image with row,col indices and 3 channels, origin is top left

        cam_dir = self.eye_position - self.lookat
        distance_to_plane = 1.0
        top = distance_to_plane * math.tan(0.5 * math.pi * self.fov / 180)
        right = self.aspect * top
        bottom = -top
        left = -right

        w = glm.normalize(cam_dir)
        u = glm.cross(self.up, w)
        u = glm.normalize(u)
        v = glm.cross(w, u)

        print("w : ", w)
        print("u : ", u)
        print("v : ", v)

        for col in tqdm(range(self.width)):
            for row in range(self.height):

                # TODO: Generate rays
                e = self.eye_position

                # Calculating the position in 2D of the pixel 
                pixelX = ((col + 0.5)/self.width) * (right - left) + left
                pixelY = ((row + 0.5)/self.height) * (top - bottom) + bottom

                print("pixelX : ", pixelX)
                print("pixelY : ", pixelY)

                # Calculating the position in 3D of the pixel (in camera coordinates)
                s = e + pixelX * u + pixelY * v - distance_to_plane * w
                p = e
                d = s - e   # goes from the eye to the pixel
                d = glm.normalize(d)    # normalizing the direction vector
                r = hc.Ray(p, d)

                # TODO: Test for intersection with all objects

                print(r.origin)
                print(r.direction)

                for obj in self.objects : 
                    intersection = obj.intersect(r, hc.Intersection(float("inf"), None, (0,0,0), None))
                    
                    print(intersection.t)
                    print(intersection.normal)
                    print(intersection.position)
                    print(intersection.mat)
                    
                    if intersection.position != None :  # if there's an intersection found
                        colour = glm.vec3(1, 1, 1)  # color = white
                    else : 
                        colour = glm.vec3(0, 0, 0)  # color = black

                # TODO: Perform shading computations on the intersection point
 
                image[row, col, 0] = max(0.0, min(1.0, colour.x))
                image[row, col, 1] = max(0.0, min(1.0, colour.y))
                image[row, col, 2] = max(0.0, min(1.0, colour.z))

        return image
