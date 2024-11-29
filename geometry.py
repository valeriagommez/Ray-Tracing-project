import helperclasses as hc
import glm
import igl

class Geometry:
    def __init__(self, name: str, gtype: str, materials: list[hc.Material]):
        self.name = name
        self.gtype = gtype
        self.materials = materials

    def intersect(self, ray: hc.Ray, intersect: hc.Intersection):
        return intersect

class Sphere(Geometry):
    def __init__(self, name: str, gtype: str, materials: list[hc.Material], center: glm.vec3, radius: float):
        super().__init__(name, gtype, materials)
        self.center = center
        self.radius = radius

    def intersect(self, ray: hc.Ray, intersect: hc.Intersection):

        # TODO: Create intersect code for Sphere
        # Find t
        # p = ray.origin
        # d = ray.direction
        # a = glm.dot(d, d)
        # b = 2 * glm.dot(d, p)
        # c = glm.dot(p, p) - self.radius * self.radius

        # p = ray.origin - self.center  # Vector from sphere center to ray origin
        p = ray.origin                # Vector from sphere center to ray origin
        d = ray.direction             # Ray direction (assumed normalized or normalize it)

        a = glm.dot(d, d)             
        b = 2 * glm.dot(d, p)         
        c = glm.dot(p, p) - self.radius * self.radius  # Sphere equation

        discriminant = b*b - 4 * a * c

        # print(f"self.center : {self.center}")
        # print(f"Ray Origin (p) : {p}")
        # print(f"Ray Direction (d) : {d}")
        # print(f"a : {a}")
        # print(f"b : {b}")
        # print(f"c : {c}")
        # print("discriminant : ", discriminant)

        if discriminant < 0 :
            return hc.Intersection(float("inf"), None, None, None)
    
        t1 = (-b + glm.sqrt(discriminant)) / (2*a)
        t2 = (-b - glm.sqrt(discriminant)) / (2*a)

        # print("t1 : ", t1)
        # print("t2 : ",t2)

        if t1 > 0 and t2 > 0 :
            t = min(t1, t2)
        elif t1 > 0 : 
            t = t1
            # print("t1 was chosen!")
        elif t2 > 0 : 
            t = t2
            # print("t2 was chosen!")
        else : 
            return hc.Intersection(float("inf"), None, None, None)

        # print("t : ", t)

        # Find the position of the intersection
        position = p + t * d
        
        # Find the normal (n)
        n = glm.normalize(position - self.center) # The normal equals to the vector from the origin to the point of intersection
        
        # Find the material of the object at that position
        return hc.Intersection(t1, n, position, self.materials[0])

class Plane(Geometry):
    def __init__(self, name: str, gtype: str, materials: list[hc.Material], point: glm.vec3, normal: glm.vec3):
        super().__init__(name, gtype, materials)
        self.point = point
        self.normal = normal

    def intersect(self, ray: hc.Ray, intersect: hc.Intersection):
        # TODO: Create intersect code for Plane

        p = ray.origin                # Vector from sphere center to ray origin
        d = ray.direction             # Ray direction (assumed normalized or normalize it)

        p0 = self.point
        n = self.normal

        A = n[0]
        B = n[1]
        C = n[2]
        D = -( A*p0[0] + B*p0[1] + C*p0[2])

        # print()
        # print("A : ", A)
        # print("B : ", B)
        # print("C : ", C)
        # print("D : ", D)
        
        denominator = A*d[0] + B*d[1] + C*d[2]

        # print("denominator : ", denominator)
        
        if denominator == 0  :
            return hc.Intersection(float("inf"), None, None, None)

        t = -(A*p[0] + B*p[1] + C*p[2] + D) / denominator

        if t < 0 : 
            return hc.Intersection(float("inf"), None, None, None)
        
        position = p + t * d

        # print("t : ", t)
        # print("position : ", position)

        if len(self.materials) == 2 :
            # print("TWO MATERIALS")
            truncX = int(position[0])
            truncZ = int(position[2])
            # print("truncX : ", truncX)
            # print("truncZ : ", truncZ)

            if ((position[0] > 0) and (position[2] > 0)) or ((position[0] < 0) and (position[2] < 0)) :
                if ((truncX % 2 == 0) and (truncZ % 2 == 0)) or ((truncX % 2 != 0) and (truncZ % 2 != 0)):
                # print("FIRST MATERIAL")
                    # print(intersectionFound.t)
                    # print(intersectionFound.normal)
                    # print(intersectionFound.position)
                    # print(intersectionFound.mat)
                    return hc.Intersection(t, n, position, self.materials[0])
                else :
                # print("SECOND MATERIAL")
                # print(intersectionFound.t)
                # print(intersectionFound.normal)
                # print(intersectionFound.position)
                # print(intersectionFound.mat)
                    return hc.Intersection(t, n, position, self.materials[1])
            
            else :
                if ((truncX % 2 == 0) and (truncZ % 2 == 0)) or ((truncX % 2 != 0) and (truncZ % 2 != 0)):
                    return hc.Intersection(t, n, position, self.materials[1])
                else : 
                    return hc.Intersection(t, n, position, self.materials[0])


        else : 
            # print("ONE MATERIAL")
            # print(intersectionFound.t)
            # print(intersectionFound.normal)
            # print(intersectionFound.position)
            # print(intersectionFound.mat)
            return hc.Intersection(t, n, position, self.materials[0])



class AABB(Geometry):
    def __init__(self, name: str, gtype: str, materials: list[hc.Material], minpos: glm.vec3, maxpos: glm.vec3):
        # dimension holds information for length of each size of the box
        super().__init__(name, gtype, materials)
        self.minpos = minpos
        self.maxpos = maxpos

    def intersect(self, ray: hc.Ray, intersect: hc.Intersection):
        pass
        # TODO: Create intersect code for Cube

class Mesh(Geometry):
    def __init__(self, name: str, gtype: str, materials: list[hc.Material], translate: glm.vec3, scale: float,
                 filepath: str):
        super().__init__(name, gtype, materials)
        verts, _, norms, self.faces, _, _ = igl.read_obj(filepath)
        self.verts = []
        self.norms = []
        for v in verts:
            self.verts.append((glm.vec3(v[0], v[1], v[2]) + translate) * scale)
        for n in norms:
            self.norms.append(glm.vec3(n[0], n[1], n[2]))

    def intersect(self, ray: hc.Ray, intersect: hc.Intersection):
        pass
        # TODO: Create intersect code for Mesh

class Node(Geometry):
    def __init__(self, name: str, gtype: str, M: glm.mat4, materials: list[hc.Material]):
        super().__init__(name, gtype, materials)        
        self.children: list[Geometry] = []
        self.M = M
        self.Minv = glm.inverse(M)

    def intersect(self, ray: hc.Ray, intersect: hc.Intersection):
        pass
        # TODO: Create intersect code for Node
