import glm

class Ray:
    def __init__(self, o: glm.vec3, d: glm.vec3):
        self.origin = o
        self.direction = d

    def getDistance(self, point: glm.vec3):
        return glm.length(point - self.origin)

    def getPoint(self, t: float):
        return self.origin + self.direction * t

class Material:
    def __init__(self, name: str, diffuse: glm.vec3, specular: glm.vec3, shininess: float):
        self.name = name
        self.diffuse = diffuse      # kd diffuse coefficient
        self.specular = specular    # ks specular coefficient
        self.shininess = shininess  # specular exponent        

class Light:
    def __init__(self, ltype: str, name: str, colour: glm.vec3, vector: glm.vec3, attenuation: glm.vec3):
        self.name = name
        self.type = ltype       # type is either "point" or "directional"
        self.colour = colour    # colour and intensity of the light
        self.vector = vector    # position, or normalized direction towards light, depending on the light type
        self.attenuation = attenuation # attenuation coeffs [quadratic, linear, constant] for point lights

class Intersection:
    def __init__(self, t: float, normal: glm.vec3, position: glm.vec3, material: Material):
        self.t = t # The distance along the ray to the intersection point
        self.normal = normal # The normal vector at the intersection point
        self.position = position # The exact position of the intersection in 3D space
        self.mat = material # The material of the object being intersected 

    @staticmethod
    def default(): # create an empty intersection record with t = inf
        t = float("inf")
        normal = None 
        position = None 
        mat = None 
        return Intersection(t, normal, position, mat)
