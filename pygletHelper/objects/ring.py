# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pyglet.graphics.vertexbuffer import create_buffer

from numpy import zeros, asarray

from pygletHelper.objects.axial import axial
from pygletHelper.util.rgba import rgb
from pygletHelper.util.vector import vector
from pygletHelper.util.tmatrix import rotation, gl_matrix_stackguard
from pygletHelper.util.gl_enable import gl_enable_client

from math import sqrt, pi


class model(object):
    def __init__(self):
        self.indices = zeros(0)
        self.vertex_pos = zeros(0)
        self.vector_normal = zeros(0)

    @property
    def vertex_pos(self):
        return self._vertex_pos
    @vertex_pos.setter
    def vertex_pos(self, n_vertex_pos):
        '''
        # if the input is not a numpy array, parse it as an array
        if type(n_vertex_pos).__module__ is not type(zeros(3)).__module__:
            n_vertex_pos = asarray(n_vertex_pos)
        self._vertex_pos = n_vertex_pos
        if not hasattr(self, 'vertex_pos_vbo'):
            self.vertex_pos_vbo = create_buffer(self.vertex_pos.nbytes)
            self.vertex_pos_vbo.bind()
        self.vertex_pos_vbo.set_data(self._vertex_pos.ctypes.data)
        #print "vertex_pos "+str(self._vertex_pos.ctypes.data)
        '''
        self._vertex_pos = []
        for i in range(0,len(n_vertex_pos)):
            self._vertex_pos.append(n_vertex_pos[i].x)
            self._vertex_pos.append(n_vertex_pos[i].y)
            self._vertex_pos.append(n_vertex_pos[i].z)
        self.vertices_gl = (GLfloat * len(self._vertex_pos))(*self._vertex_pos)


    @property
    def vector_normal(self):
        return self._vector_normal
    @vector_normal.setter
    def vector_normal(self, n_vector_normal):
        # if the input is not a numpy array, parse it as an array
        '''
        if type(n_vector_normal).__module__ is not type(zeros(3)).__module__:
            n_vector_normal = asarray(n_vector_normal)
        self._vector_normal = n_vector_normal
        if not hasattr(self, 'vector_normal_vbo'):
            self.vector_normal_vbo = create_buffer(self.vector_normal.nbytes)
            self.vector_normal_vbo.bind()
        print "vector_normal "+str(self._vector_normal)
        self.vector_normal_vbo.set_data(self._vector_normal.ctypes.data)
        print self.vector_normal
        self.normals_gl = (GLfloat * len(self._vector_normal))(*self._vector_normal)
        '''
        self._vector_normal = []
        for i in range(0,len(n_vector_normal)):
            self._vector_normal.append(n_vector_normal[i].x)
            self._vector_normal.append(n_vector_normal[i].y)
            self._vector_normal.append(n_vector_normal[i].z)
        self.normals_gl = (GLfloat * len(self._vector_normal))(*self._vector_normal)

    @property
    def indices(self):
        return self._indices
    @indices.setter
    def indices(self, n_indices):
        self._indices = [int(i) for i in n_indices]
        self.indices_gl = (GLuint * len(self._indices))(*self._indices)


class ring(axial):
    def __init__(self, thickness=0.0, model_rings=-1, radius=1.0, color=rgb(), pos=vector(0, 0, 0),
                 axis=vector(1, 0, 0)):
        super(ring, self).__init__(radius=radius, color=color, pos=pos, axis=axis)
        self.axis = axis
        # The radius of the ring's body.  If not specified, it is set to 1/10 of
        # the radius of the body.
        self.thickness = thickness
        self.PRIMITIVE_TYPEINFO_DECL = ring
        self.model = model()
        self.model_rings = model_rings
        self.model_bands = 0
        self.model_radius = 0
        self.model_thickness = 0
        self.pos = pos

    @property
    def thickness(self):
        return self._thickness

    @thickness.setter
    def thickness(self, t):
        self._thickness = t

    @property
    def material_matrix(self, out):
        out.translate(vector(.5, .5, .5))
        out.scale(vector(self.radius, self.radius, self.radius) * (.5 / (self.radius + self.thickness)))
        return out

    @property
    def degenerate(self):
        return self.radius == 0.0

    def gl_pick_render(self, scene):
        self.gl_render(scene)

    def gl_render(self, scene):
        if self.degenerate:
            return
        # Level of detail estimation.  See sphere::gl_render().

        # The number of subdivisions around the hoop's radial direction.
        if self.thickness:
            band_coverage = scene.pixel_coverage(self.pos, self.thickness)
        else:
            band_coverage = scene.pixel_coverage(self.pos, self.radius * 0.1)
        if (band_coverage < 0):
            band_coverage = 1000
        bands = sqrt(band_coverage * 4.0)
        bands = clamp(4, bands, 40)
        # The number of subdivions around the hoop's tangential direction.
        ring_coverage = scene.pixel_coverage(self.pos, self.radius)
        if (ring_coverage < 0):
            ring_coverage = 1000
        rings = sqrt(ring_coverage * 4.0)
        rings = clamp(4, rings, 80)

        if self.model_rings != rings or self.model_bands != bands or self.model_radius != self.radius or self.model_thickness != self.thickness:
            self.model_rings = rings
            self.model_bands = bands
            self.model_radius = self.radius
            self.model_thickness = self.thickness
            self.model = self.create_model(rings, bands)

        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        self.model_world_transform(scene.gcf, vector(self.radius, self.radius, self.radius)).gl_mult()
        #print "model vertex-pos: "+str(self.model._vertex_pos)
        #print "model vector-normal: "+str(self.model._vector_normal)
        self.color.gl_set(self.opacity)
        '''
        glVertexPointer(3, GL_FLOAT, 0, self.model.vertex_pos_vbo.ptr)
        glNormalPointer(GL_FLOAT, 0, self.model.vector_normal_vbo.ptr)
        glDrawElements(GL_TRIANGLES, self.model.indices.size, GL_UNSIGNED_SHORT, 0)
        '''
        glVertexPointer(3, GL_FLOAT, 0, self.model.vertices_gl)
        glNormalPointer(GL_FLOAT, 0, self.model.normals_gl)
        glDrawElements(GL_TRIANGLES, len(self.model.indices), GL_UNSIGNED_SHORT, self.model.indices_gl)
        glPopClientAttrib()

    def grow_extent(self, world):
        if self.degenerate:
            return
        # TODO: Not perfectly accurate (a couple more circles would help)
        a = self.axis.norm()
        if self.thickness:
            t = self.thickness
        else:
            t = self.radius * .1
        world.add_circle(self.pos, a, self.radius + t)
        world.add_circle(self.pos + a * t, a, self.radius)
        world.add_circle(self.pos - a * t, a, self.radius)
        world.add_body()
        return world

    def create_model(self, rings, bands):
        # In Visual 3, rendered thickness was (incorrectly) double what was documented.
        # The documentation said that thickness was the diameter of a cross section of
        # a solid part of the ring, but in fact ring.thickness was the radius of the
        # cross section. Presumably we have to maintain the incorrect Visual 3 behavior
        # and change the documentation.
        scaled_radius = 1.0
        scaled_thickness = 0.2
        if self.thickness != 0.0:
            scaled_thickness = 2 * self.thickness / self.radius

        # First generate a circle of radius thickness in the xy plane
        if (bands > 80):
            raise ValueError("ring create_model: More bands than expected.")
        circle = [vector()] * 80
        circle[0] = vector(0, scaled_thickness * 0.5, 0)
        rotator = rotation(2.0 * pi / bands, vector(0, 0, 1), vector(0, 0, 0))
        for i in range(1, bands):
            circle[i] = rotator * circle[i - 1]
        m = model()
        vertexes = [vector()]*int(rings * bands)
        normals = [vector()]*int(rings * bands)

        # ... and then sweep it in a circle around the x axis
        radial = vector(0, 1, 0)
        i = 0
        rotator = rotation(2.0 * pi / rings, vector(1, 0, 0), vector(0, 0, 0))
        for r in range(0, int(rings)):
            for b in range(0, int(bands)):
                tmp_vertex = vector()
                tmp_normal = vector()
                tmp_normal.x = circle[b].x
                tmp_normal.y = radial.y * circle[b].y
                tmp_normal.z = radial.z * circle[b].y
                normals[i] = tmp_normal
                tmp_vertex.x = normals[i].x
                tmp_vertex.y = normals[i].y + radial.y
                tmp_vertex.z = normals[i].z + radial.z
                vertexes[i] = tmp_vertex
                i += 1
                #if i==50:
                #print "vertex: "+str(i)+" "+str(vertexes[i])+" "+str(tmp_vertex)
            radial = rotator * radial
            #print "radial: "+str(radial)
        print "vertexes :"+str(vertexes)
        m.vector_normal = normals
        m.vertex_pos = vertexes

        # Now generate triangle indices... could do this with triangle strips but I'm looking
        # ahead to next renderer design, where it would be nice to always use indexed tris
        m.indices = zeros(int(rings * bands * 6))
        ind = m.indices
        i = 0
        ind_ind = 0
        for r in range(0, int(rings)):
            for b in range(0, int(bands)):
                ind[ind_ind+0] = i
                ind[ind_ind+1] = i + bands
                ind[ind_ind+2] = i + 1
                ind[ind_ind+3] = i + bands
                ind[ind_ind+4] = i + bands + 1
                ind[ind_ind+5] = i + 1
                i += 1
                # not 100% sure what this does...
                ind_ind+= 6
            ind[ind_ind+2 - 6] -= bands
            ind[ind_ind+4 - 6] -= bands
            ind[ind_ind+5 - 6] -= bands
        ind_ind -= 6 * bands
        for b in range(0, bands):
            ind[ind_ind+1] -= rings * bands
            ind[ind_ind+3] -= rings * bands
            ind[ind_ind+4] -= rings * bands
            ind_ind += 6
        m.indices = ind
        return m

def clamp(lower, value, upper):
    if lower > value:
        return lower
    if upper < value:
        return upper
    return value