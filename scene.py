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
        vUnitVector = glm.cross(w, u)

        for col in tqdm(range(self.width)):
            for row in range(self.height):

                # TODO: Generate rays
                e = self.eye_position

                # Calculating the position in 2D of the pixel 
                pixelX = ((col + 0.5)/self.width) * (right - left) + left
                pixelY = ((row + 0.5)/self.height) * (top - bottom) + bottom

                # print("pixelX : ", pixelX)
                # print("pixelY : ", pixelY)

                # Calculating the position in 3D of the pixel (in camera coordinates)
                s = e + pixelX * u + -pixelY * vUnitVector - distance_to_plane * w
                p = e
                d = s - e   # goes from the eye to the pixel
                d = glm.normalize(d)    # normalizing the direction vector
                r = hc.Ray(p, d)

                # TODO: Test for intersection with all objects

                # print(r.origin)
                # print(r.direction)

                for obj in self.objects : 
                    intersection = obj.intersect(r, hc.Intersection(float("inf"), None, (0,0,0), None))

                    # Comment this??
                    if intersection.position != None :  # if there's an intersection found
                        # colour = glm.vec3(1, 1, 1)  # color = white

                        # TODO: Perform shading computations on the intersection point
                        n = intersection.normal
                        curPixel = intersection.position
                        material = intersection.mat

                        # Attenuate the light intensity if it's a point light
                        for light in self.lights : 
                            if light.type == "point" : 
                                lightPosition = light.vector
                                distance = np.linalg.norm(lightPosition - curPixel)    
                                k_c = light.attenuation[2]
                                k_l = light.attenuation[1]
                                k_q = light.attenuation[0]

                                attenuationFactor = 1 / (k_c + k_l * distance + k_q * distance * distance)
                                I = attenuationFactor * light.colour
                            else : 
                                I = light.colour # --> a vector with RGB components
                        

                        ambientLight = self.ambient
                        # print("I : ", I)
                        # print("ambientLight : " , ambientLight) # ambientLight :  vec3(          0.1,          0.1,          0.1 )
                        
                        v = self.eye_position - curPixel    # from the current pixel towards the camera
                        v = glm.normalize(v)
                        # print("v : ", v)

                        l = lightPosition - curPixel    # light ray from pixel to light source
                        l = glm.normalize(l)
                        # print("l : ", l)

                        # Calculating the Lambertian diffuse shading
                        k_d = material.diffuse
                        diffuseLight = k_d * I * max(0, glm.dot(n, l)) 
                        # print("k_d : ", k_d)    # k_d :  vec3( 1, 0, 0 )
                        # print()
                        # print("n : ", n)
                        # print("l : ", l)
                        # print("glm.dot(n, l): ", glm.dot(n, l))
                        # print("diffuseLight : ", diffuseLight)  # diffuseLight :  vec3(            0,            0,            0)

                        # Calculating the Blinn-Phong specular shading
                        p_exponent = material.shininess # 32
                        k_s = material.specular
                        h = (v + l) / np.linalg.norm(v + l)     # this is the bissector between v and l
                        blinnPhongLight = k_s * I * max(0, glm.dot(n, h))** p_exponent
                        
                        # print()
                        # print("n : ", n)
                        # print("h : ", h)
                        # print("glm.dot(n, h): ", glm.dot(n, h))
                        # print("k_s : ", k_s)    # k_s :  vec3(          0.8,          0.8,          0.8 )
                        # print("blinnPhongLight : ", blinnPhongLight)    # blinnPhongLight :  vec3(            0,            0,            0 ) 
                        
                        colour = ambientLight + diffuseLight + blinnPhongLight
                        # print("colour : ", colour)  # colour :  vec3(          0.1,          0.1,          0.1 ) --> only ambient

                    else : 
                        # colour = glm.vec3(0, 0, 0)  # color = black
                        colour = self.ambient
                    
                image[row, col, 0] = max(0.0, min(1.0, colour.x))
                image[row, col, 1] = max(0.0, min(1.0, colour.y))
                image[row, col, 2] = max(0.0, min(1.0, colour.z))

        return image
