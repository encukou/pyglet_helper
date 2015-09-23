# Copyright (c) 2000, 2001, 2002, 2003 by David Scherer and others.
# Copyright (c) 2004 by Jonathan Brandmeyer and others.
# See the file vpython_license.txt for vpython license terms.
# See the file vpython_authors.txt for a list of vpython contributors.
# Ported to pyglet in 2015 by Catherine Holloway
from pyglet.gl import *
from pygletHelper.objects.rectangular import rectangular
from pygletHelper.util.rgba import rgb
from pygletHelper.util.vector import vector
from pygletHelper.util.tmatrix import gl_matrix_stackguard

class box(rectangular):
    def __init__(self, width=1.0, height=1.0, length=1.0, color=rgb(),pos = vector(0,0,0)):
        super(box, self).__init__(width=width, height=height, color=color, length=length, pos=pos)

    # True if the box should not be rendered.
    # bool degenerate();
    # static displaylist model;
    # static void init_model(displaylist& model, bool skip_right_face);
    def init_model(self, scene, skip_right_face=False):
        # Note that this model is also used by arrow!
        scene.box_model.gl_compile_begin()
        glEnable(GL_CULL_FACE)
        glBegin(GL_TRIANGLES)

        s = 0.5
        vertices = [ \
            [[+s, +s, +s], [+s, -s, +s], [+s, -s, -s], [+s, +s, -s]],  # Right face
            [[-s, +s, -s], [-s, -s, -s], [-s, -s, +s], [-s, +s, +s]],  # Left face
            [[-s, -s, +s], [-s, -s, -s], [+s, -s, -s], [+s, -s, +s]],  # Bottom face
            [[-s, +s, -s], [-s, +s, +s], [+s, +s, +s], [+s, +s, -s]],  # Top face
            [[+s, +s, +s], [-s, +s, +s], [-s, -s, +s], [+s, -s, +s]],  # Front face
            [[-s, -s, -s], [-s, +s, -s], [+s, +s, -s], [+s, -s, -s]]  # Back face
            ]
        normals = [[+1, 0, 0], [-1, 0, 0], [0, -1, 0], [0, +1, 0], [0, 0, +1], [0, 0, -1]]
        # Draw inside (reverse winding and normals)
        for f in range(skip_right_face, 6):
            glNormal3f(-normals[f][0], -normals[f][1], -normals[f][2])
            for v in range(0, 3):
                glVertex3f(GLfloat(vertices[f][3 - v][0]), GLfloat(vertices[f][3 - v][1]),
                            GLfloat(vertices[f][3 - v][2]))
            for v in (0,2,3):
                glVertex3f(GLfloat(vertices[f][3 - v][0]), GLfloat(vertices[f][3 - v][1]),
                            GLfloat(vertices[f][3 - v][2]))
        # Draw outside
        for f in range(skip_right_face, 6):
            glNormal3f(GLfloat(normals[f][0]), GLfloat(normals[f][1]), GLfloat(normals[f][2]))
            for v in range(0, 3):
                glVertex3f(GLfloat(vertices[f][v][0]), GLfloat(vertices[f][v][1]), GLfloat(vertices[f][v][2]))
            for v in (0,2,3):
                glVertex3f(GLfloat(vertices[f][v][0]), GLfloat(vertices[f][v][1]), GLfloat(vertices[f][v][2]))
        glEnd()
        glDisable(GL_CULL_FACE)
        scene.box_model.gl_compile_end()
        # check_gl_error()

        # virtual void gl_pick_render( const view&);

    def gl_pick_render(self, scene):
        self.gl_render(scene)

    def gl_render(self, scene):
        if not scene.box_model.compiled():
            self.init_model(scene, False)
        self.color.gl_set(self.opacity)
        guard = gl_matrix_stackguard()
        self.apply_transform(scene)
        scene.box_model.gl_render()
        #check_gl_error()

    def grow_extent(self, e):
        tm = self.model_world_transform(1.0, vector(self.axis.mag(), self.height, self.width) * 0.5)
        e.add_box(tm, vector(-1, -1, -1), vector(1, 1, 1))
        e.add_body()
        return e

    def get_material_matrix(self, out):
        out.translate(vector(.5, .5, .5))
        scale = vector(self.axis.mag(), self.height, self.width)
        out.scale(scale * (1.0 / max(scale.x, max(scale.y, scale.z))))
        return out