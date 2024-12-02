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

                numSamples = self.samples

                subPixel_sizeX = (right - left) / (self.width * numSamples)
                subPixel_sizeY = (top - bottom) / (self.height * numSamples)

                colour = glm.vec3(0, 0, 0)

                for sub_col in range(0, numSamples) :
                    for sub_row in range(0, numSamples): 

                        subpixel_x = left + (col + (sub_col + 0.5) / numSamples) * subPixel_sizeX
                        subpixel_y = bottom + (row + (sub_row + 0.5) / numSamples) * subPixel_sizeY

                        # Calculating the position in 3D of the pixel (in camera coordinates)
                        s = e + subpixel_x * u + -subpixel_y * vUnitVector - distance_to_plane * w
                        p = e
                        d = s - e   # goes from the eye to the pixel
                        d = glm.normalize(d)    # normalizing the direction vector
                        r = hc.Ray(p, d)

                        # TODO: Test for intersection with all objects

                        intersection = hc.Intersection(float("inf"), None, None, None)
                        closest_t = float("inf")
                        objectRendered = None

                        for sceneObject in self.objects : 
                            # print(obj.name)
                            curIntersection = sceneObject.intersect(r, hc.Intersection(float("inf"), None, None, None))
                            # print("curIntersection.t : ", curIntersection.t)
                            # print("curIntersection.n : ", curIntersection.normal)
                            
                            if curIntersection.t < closest_t :
                                closest_t = curIntersection.t
                                # print("closest_t : ", closest_t)
                                intersection = curIntersection
                                objectRendered = sceneObject
                                # print(obj.name, "was chosen to be rendered!") 

                            # Comment this??
                        if intersection.position != None :  # if there's an intersection found

                            # TODO: Perform shading computations on the closest intersection point
                            n = intersection.normal
                            curPixel = intersection.position
                            material = intersection.mat

                            v = self.eye_position - curPixel    # from the current pixel towards the camera
                            v = glm.normalize(v)

                            ambientLight = glm.vec3(0, 0, 0)
                            diffuseLight = glm.vec3(0, 0, 0)
                            blinnPhongLight = glm.vec3(0, 0, 0)

                            colour = glm.vec3(1, 1, 1)  # color = white IF there are intersections found

                            for light in self.lights : 
                                # print("\nlight.name: ", light.name)

                                lightPosition = light.vector

                                if light.type == "point" :  # Attenuate the light intensity if it's a point light
                                    distance = np.linalg.norm(lightPosition - curPixel) 
                                    k_c = light.attenuation[2]
                                    k_l = light.attenuation[1]
                                    k_q = light.attenuation[0]

                                    attenuationFactor = 1 / (k_c + k_l * distance + k_q * distance * distance)

                                    I = attenuationFactor * light.colour 

                                else : 
                                    I = light.colour # --> a vector with RGB components

                                l = lightPosition - curPixel    # light ray from pixel to light source
                                l = glm.normalize(l)
                                # print("l : ", l)

                                # Doing the shadow rays : 

                                dirToLight = glm.normalize(lightPosition - curPixel)
                                shadowRay = hc.Ray(curPixel + 0.01 * n , dirToLight)    # adding a bit of offset
                                inShadow = False

                                for obj in self.objects:
                                    if (obj.name != 'plane') : 
                                        shadowIntersect = obj.intersect(shadowRay, hc.Intersection(float("inf"), None, None, None))
                                        # print("objectRendered :", objectRendered.name)
                                        # print("obj :", obj.name)
                                        if (shadowIntersect.position != None) :   
                                            # print(objectRendered.name, "collided with ", obj.name, "when reaching", light.name)
                                            # print("inShadow!")
                                            # If an interception is found AND we're not intercepting our own object
                                            inShadow = True
                                
                                if not inShadow :
                                    v = - glm.normalize(r.direction)
                                    l = glm.normalize(lightPosition - curPixel)
                                    
                                # Calculating the Lambertian diffuse shading
                                    k_d = material.diffuse
                                    diffuseLight = diffuseLight + k_d * I * max(0, glm.dot(n, l))

                                    # Calculating the Blinn-Phong specular shading
                                    p_exponent = material.shininess 
                                    k_s = material.specular
                                    h = (v + l) / np.linalg.norm(v + l)     # this is the bissector between v and l

                                    blinnPhongLight = blinnPhongLight + k_s * I * math.pow(max(0, glm.dot(n, h)), p_exponent)

                                    ambientLight = ambientLight + self.ambient * material.diffuse

                            subPixelColour = ambientLight + diffuseLight + blinnPhongLight
                            
                            # print(objectRendered.name)
                            # print("Final colour : ", colour)
                            # print()

                        else : 
                            subPixelColour = glm.vec3(0, 0, 0)  # color = black 
                        
                        colour = colour + subPixelColour
                
                pixelColour = colour / (numSamples * numSamples)
                pixelColour = glm.vec3(
                    max(0.0, min(1.0, pixelColour.x)),
                    max(0.0, min(1.0, pixelColour.y)),
                    max(0.0, min(1.0, pixelColour.z)),
                )

                            
                image[row, col, 0] = max(0.0, min(1.0, pixelColour.x))
                image[row, col, 1] = max(0.0, min(1.0, pixelColour.y))
                image[row, col, 2] = max(0.0, min(1.0, pixelColour.z))
                    
                # if objectRendered != None : 
                #     print(objectRendered.name)
                #     print(image[row, col, 0])
                #     print(image[row, col, 1])
                #     print(image[row, col, 2])
                #     print()

        return image
