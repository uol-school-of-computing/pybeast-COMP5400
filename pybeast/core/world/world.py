# Built-in
import time
from typing import TYPE_CHECKING, List, Optional, Union, TypeVar
from types import SimpleNamespace
# From Third-party
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
# From pybeast
from pybeast.core.world.worldobject import WorldObject
from pybeast.core.agents.animat import Animat
from pybeast.core.utils.colours import ColourPalette, ColourType
from pybeast.core.world.collisions import Collisions, Collision
from pybeast.core.utils.vector2D import Vector2D
from pybeast.core.utils.vector3D import Vector3D
from pybeast.core.agents.animatmonitor import AnimatMonitor
from pybeast.core.evolve.population import Population, Group

if TYPE_CHECKING:
    from pybeast.core.simulation import Simulation

SIZE = 512
WORLD_WIDTH = 800.0
WORLD_HEIGHT = 600.0
# World dimensions
TWO = 0
THREE = 1

WORLD_DISPLAY_TYPE =  SimpleNamespace(**{
"DISPLAY_NONE": 0,  # Nothing is displayed at all.
"DISPLAY_NONE": 1,  # Animats are displayed.
"DISPLAY_WORLDOBJECTS": 2,  # WorldObjects are displayed.
"DISPLAY_ANIMATS": 2,  # WorldObjects are displayed.
"DISPLAY_TRAILS": 4,  # Trails are displayed.
"DISPLAY_SENSORS": 8,  # Sensors are displayed.
"DISPLAY_COLLISIONS": 0,  # Set to nonzero (16) to display collisions.
"DISPLAY_MONITOR": 32,  # The monitor is displayed.
"DISPLAY_ALL": 65535  # Everything is displayed.
})

WORLD_DISP_PARAM = SimpleNamespace(**{
    "width": 800.0,
    "height": 600.0,
    "winWidth": 800.0,
    "winHeight": 600.0,
    "config": 65535,
    "colour": [1.0, 1.0, 1.0],
    "dimension": 0
})


T = TypeVar('T', bound=Union[WorldObject, Animat])

class World:
    def __init__(self, simulation: "Simulation"):
        """
        Initializes the World object.

        Configures the monitor and collisions classes, sets the color,
        and initializes eye, look, and up vectors.
        """

        self.mySimulation = simulation
        self.animats: List[Animat] = []
        self.animatQueue: List[Animat] = []
        self.worldobjects: List[WorldObject] = []
        self.worldobjectQueue: List[WorldObject] = []
        self.collisions: Collisions = Collisions()
        self.monitor: AnimatMonitor = AnimatMonitor(self.animats.copy())
        self.updateInProgress: bool = False
        self.worldDisplayType: dict = WORLD_DISPLAY_TYPE

        self.mouse = SimpleNamespace(**{
            "location": Vector2D(0.0, 0.0),
            "staticLocation": Vector2D(0.0, 0.0),
            "left": False,
            "right": False,
            "current": None,
            "selected": None
        })

        self.disp = WORLD_DISP_PARAM

        self.key = SimpleNamespace(**{
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "add": False,
            "sub": False,
            "wxLeft": 0,
            "wxRight": 0,
            "wxUp": 0,
            "wxDown": 0
        })

        self.eye = Vector3D(0.5 * self.disp.width, self.disp.height, 100.0)
        self.look = Vector3D(self.disp.width / 2.0, self.disp.height / 2.0, 0.0)
        self.up = Vector3D(0.0, 0.0, 1.0)

    # -----------------------------------------------------------------------------------------------------------------
    # Initialize World
    # -----------------------------------------------------------------------------------------------------------------

    def Init(self):
        """
        Calls Init on every Animat and WorldObject in the World. Usually called at
        the start of a simulation, to allow objects to be set up correctly (e.g.
        defining display lists and performing configuration which can't be done until
        an object knows which World it's in.
        See Also:
            - Animat.Init
            - WorldObject.Init
        """

        for worldobject in self.worldobjects:
            worldobject.Init()
        for animat in self.animats:
            animat.Init()

    def InitGL(self):
        """
        Sets up GL with the correct background color, projection mode, and blend
        function.
        """
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

        # Lights - for 3D mode
        glEnable(GL_COLOR_MATERIAL)  # Use glColor functions to change material properties
        # Light parameters
        global_ambient = [0.3, 0.3, 0.3, 1.0]
        diffuse = [1.0, 1.0, 1.0, 1.0]
        specular = [1.0, 1.0, 1.0, 1.0]

        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, global_ambient)
        position = [0.0, self.disp.height / 2, self.disp.width / 2, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, position)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular)
        glEnable(GL_LIGHT0)

        glShadeModel(GL_SMOOTH)  # Gouraud shading

        glClearColor(self.disp.colour[0], self.disp.colour[1], self.disp.colour[2], 1.0)

        glMatrixMode(GL_PROJECTION)
        gluOrtho2D(0, self.disp.width, 0, self.disp.height)
        # glFrustum(0.0, 100000.0, 0.0, 80000.0, -0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # For sensors

        return

    # -----------------------------------------------------------------------------------------------------------------
    # Populate World
    # -----------------------------------------------------------------------------------------------------------------

    def Add(self, r: WorldObject):
        """
        Adds an Animat to the World's animat container, sets the Animat's world to
        this one, and adds a pointer to the Animat to the monitor object.

        :param r: A pointer to the Animat to be added.
        """

        if isinstance(r, list):
            for v in r:
                self.Add(v)
        elif isinstance(r, Animat):
            if not self.updateInProgress:
                self.animats.append(r)
            else:
                self.animatQueue.append(r)
            self.monitor.Append(r)
        elif isinstance(r, WorldObject):
            if not self.updateInProgress:
                self.worldobjects.append(r)
            else:
                self.worldobjectQueue.append(r)

        r.SetWorld(self)

    def AddCollision(self, pv: Vector2D):
        """
        Adds a collision to the collisions object.

        :param pv:
        """
        c = Collision(pv, visible=bool(self.worldDisplayType.DISPLAY_COLLISIONS))
        self.collisions.Append(c)

    def Remove(self, T: Optional[WorldObject]):
        """
        Removes all objects of the specified type from the World.

        This method removes all objects of the specified type from the World instance.
        It should be noted that this operation should not be performed during the
        World update process, as indicated by the warning.

        Warning:
            This method will not work during the World update process (World::Update).
            It is recommended to use this method only between assessments.

        Returns:
            None
        """
        if self.updateInProgress:
            return

        removed_worldobjects = []

        for wo in reversed(self.worldobjects[:]):
            if not isinstance(wo, T):
                self.worldobjects.remove(wo)
                removed_worldobjects.append(wo)

        removed_animats = []

        for ani in reversed(self.animats[:]):
            if not isinstance(ani, T):
                self.animats.remove(wo)
                removed_animats.append(wo)

        for ani in reversed(self.monitor.animats[:]):
            if not isinstance(ani, T):
                self.monitor.animats.remove(ani)

        return removed_worldobjects + removed_animats

    # -----------------------------------------------------------------------------------------------------------------
    # Life cycle functions
    # -----------------------------------------------------------------------------------------------------------------


    def Clear(self):
        # TODO: For testing, remove later
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def Display(self):
        """
        Calls the Display method of every object in the world, depending on this
        World's DisplayInfo struct.

        This method iterates through all objects in the world and invokes their
        Display method based on the World's DisplayInfo struct. This struct
        likely contains information about which objects should be displayed
        and how they should be rendered.

        See Also:
            DisplayInfo: A struct containing information about object display.
            WorldDisplayType: Enumerated type defining different display options.
        """

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # For 3D world must be drawn differently in order to get depth testing done for Animats and WorldObjects,
        # but to disable depth testing on collisions and mouse selections.
        if self.disp.dimension == THREE:

            glViewport(0, 0, self.disp.winWidth, self.disp.winHeight)
            self.SetColour(1.0, 1.0, 1.0)

            # camera stuff
            # glTranslatef(100.0, 0.0, 0.0)
            self.MoveEye()
            gluLookAt(self.eye.x, self.eye.y, self.eye.z, self.look.x, self.look.y, self.look.z, self.up.x, self.up.y,
                      self.up.z)

            glColor4fv(ColourPalette[ColourType.COLOUR_DARK_PURPLE])

            glEnable(GL_LIGHTING)
            # table second - want everything to appear on top of this
            glBegin(GL_QUADS)
            glNormal3f(0.0, 0.0, 1.0)
            glVertex3f(0.0, 0.0, 0.0)
            glVertex3f(0.0, self.disp.height, 0.0)
            glVertex3f(self.disp.width, self.disp.height, 0.0)
            glVertex3f(self.disp.width, 0.0, 0.0)
            glEnd()
            glDisable(GL_LIGHTING)

            # next - collisions
            if self.disp.config & self.worldDisplayType.DISPLAY_COLLISIONS != 0:
                self.collisions.Display()

            # look at location marker
            glColor4fv(ColourPalette[ColourType.COLOUR_BLACK])
            glBegin(GL_QUADS)
            glVertex3f(self.look.x - 1, self.look.y + 10, 0.0)
            glVertex3f(self.look.x + 1, self.look.y + 10, 0.0)
            glVertex3f(self.look.x + 1, self.look.y - 10, 0.0)
            glVertex3f(self.look.x - 1, self.look.y - 10, 0.0)
            glVertex3f(self.look.x - 10, self.look.y - 1, 0.0)
            glVertex3f(self.look.x - 10, self.look.y + 1, 0.0)
            glVertex3f(self.look.x + 10, self.look.y + 1, 0.0)
            glVertex3f(self.look.x + 10, self.look.y - 1, 0.0)
            glEnd()

            # finally, mouse choices
            if self.mouse.selected is not None:
                glColor4fv(ColourPalette[ColourType.COLOUR_SELECTION])
                pos = self.mouse.selected.get_location()
                glEnable(GL_BLEND)
                glPushMatrix()
                Disk = gluNewQuadric()
                gluQuadricDrawStyle(Disk, GLU_FILL)
                glTranslated(pos.x, pos.y, 0.0)
                gluDisk(Disk, 0, self.mouse.selected.get_radius() + 5.0, 16, 1)
                gluDeleteQuadric(Disk)
                glPopMatrix()
                glDisable(GL_BLEND)

            # then just do world objects and animats using depth testing
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)

            if self.disp.config & self.worldDisplayType.DISPLAY_WORLDOBJECTS != 0:
                for obj in self.worldobjects:
                    obj.Display()

            if self.disp.config & self.worldDisplayType.DISPLAY_ANIMATS != 0:
                for animat in self.animats:
                    animat.Display()

            glDisable(GL_LIGHTING)
            glDisable(GL_DEPTH_TEST)

        # If 2D World
        else:
            self.SetColour(*ColourPalette[ColourType.COLOUR_DARK_PURPLE][:3])
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            if self.disp.config & self.worldDisplayType.DISPLAY_WORLDOBJECTS != 0:
                for obj in self.worldobjects:
                    obj.Display()

            if self.disp.config & self.worldDisplayType.DISPLAY_ANIMATS != 0:
                for animat in self.animats:
                    animat.Display()

            if self.mouse.selected is not None:
                glColor4fv(ColourPalette[ColourType.COLOUR_SELECTION])
                pos = self.mouse.selected.get_location()
                glEnable(GL_BLEND)
                glPushMatrix()
                Disk = gluNewQuadric()
                gluQuadricDrawStyle(Disk, GLU_FILL)
                glTranslated(pos.x, pos.y, 0.0)
                gluDisk(Disk, 0, self.mouse.selected.get_radius() + 5.0, 16, 1)
                gluDeleteQuadric(Disk)
                glPopMatrix()
                glDisable(GL_BLEND)

            if self.disp.config & self.worldDisplayType.DISPLAY_COLLISIONS != 0:
                self.collisions.Display()
            if self.disp.config & self.worldDisplayType.DISPLAY_MONITOR != 0:
                # TODO: Fix later
                #self.monitor.Display()
                pass

    def DrawObjects(self):
        """
        Draws objects in the world if the corresponding display flag is set.

        This method checks if the DISPLAY_WORLDOBJECTS flag is set in the
        display configuration of the World instance. If the flag is set, it
        draws each object in the world using OpenGL setup.

        OpenGL setup is assumed, including clearing the color and depth buffers,
        setting the modelview matrix, setting the view using gluLookAt, loading
        names for object picking, and flushing the OpenGL pipeline.

        Note:
            This method assumes the availability of OpenGL functions and
            appropriate setup.
        """

        if (self.disp.config & self.worldDisplayType.DISPLAY_WORLDOBJECTS) != 0:
            # Assuming OpenGL setup
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            gluLookAt(self.eye.x, self.eye.y, self.eye.z, self.look.x, self.look.y, self.look.z, self.up.x, self.up.y,
                      self.up.z)
            for i in range(1, len(self.worldobjects) + 1):
                glLoadName(i)
                self.worldobjects[i - 1].Display()

            glFlush()

    def Update(self):
        """
        Called every frame and responsible for calling Update on every WorldObject
        and Animat in the World.
        See Also:
            - WorldObject.Update
            - Animat.Update
        """

        self.updateInProgress = True
        self.UpdateMouse()

        # Update every object in the world.
        for wo in self.worldobjects:
            wo.Update()

        for a in self.animats:
            a.Update()

        # Remove dead world objects and animats.
        for wo in reversed(self.worldobjects[:]):
            if wo.dead:
                self.worldobjects.remove(wo)

        for ani in reversed(self.animats[:]):
            if ani.dead:
                self.animats.remove(ani)

        if self.mySimulation.profile:
            startTimeInteract = time.time()
            self.mySimulation.profiler.functionsToProfile['animat.Interact']['count'] +=1

        # Animats interact with everything else:
        if self.animats:
            if self.mySimulation.profile:
                startTime = time.time()
                self.mySimulation.profiler.functionsToProfile['animat.Interact.withObjects']['count'] += 1

            for wo in self.worldobjects:
                # Each Animat interacts with each Worldobject
                for animat in self.animats:
                    animat.Interact(wo)

            if self.mySimulation.profile:
                endTime = time.time()
                self.mySimulation.profiler.functionsToProfile['animat.Interact.withObjects']['times'].append(endTime - startTime)

            if self.mySimulation.profile:
                startTime = time.time()
                self.mySimulation.profiler.functionsToProfile['animat.Interact.withAnimats']['count'] += 1

            # Each Animat interacts with each Animat.
            for i, animat1 in enumerate(self.animats):
                for j, animat2 in enumerate(self.animats):
                    if j != i:
                        animat1.Interact(animat2)

            if self.mySimulation.profile:
                endTime = time.time()
                self.mySimulation.profiler.functionsToProfile['animat.Interact.withAnimats']['times'].append(endTime - startTime)

        if self.mySimulation.profile:
            endTime = time.time()
            self.mySimulation.profiler.functionsToProfile['animat.Interact']['times'].append(endTime - startTimeInteract)

        self.collisions.Update()
        self.updateInProgress = False
        self.UpdateQueues()

    def UpdateQueues(self):

        self.animats.extend(self.animatQueue)
        self.animatQueue.clear()

        self.worldobjects.extend(self.worldobjectQueue)
        self.worldobjectQueue.clear()



    def UpdateQueues(self):
        """
         Updates the queues of animats and world objects by transferring all items
         from the temporary queues to the main lists and then clears the temporary
         queues.

         This method is typically called to finalize the update process by
         transferring items from temporary queues to main lists.
         """
        self.animats.extend(self.animatQueue)
        self.animatQueue.clear()

        self.worldobjects.extend(self.worldobjectQueue)
        self.worldobjectQueue.clear()

    def CleanUp(self):
        """
        Clears all containers in this World.

        This method clears all containers within the World instance,
        ensuring that the World is empty and ready for new data.
        """

        self.animats.clear()
        self.worldobjects.clear()

        self.collisions.Clear()
        self.monitor.Clear()
        self.mouse.current = None
        self.mouse.selected = None

    #------------------------------------------------------------------------------------------------------------------
    # Events

    def UpdateMouse(self):
        if self.mouse.current is None:
            return

        if self.mouse.left and self.disp.dimension == TWO:
            if self.mouse.right:
                orientation = (self.mouse.location - self.mouse.current.GetLocation()).GetAngle()
                self.mouse.current.SetOrientation(orientation)
                self.mouse.current.SetLocation(self.mouse.staticLocation)
            else:
                self.mouse.current.SetLocation(self.mouse.location)

    def OnMouseLDown(self, x, y):

        if self.mouse.right:
            return

        self.mouse.left = True
        self.mouse.location = self.WindowXY(x, y)

        # If world is three-dimensional
        if self.disp.dimension == THREE:
            select_buf = (GLint * SIZE)()
            hits = GLint()
            viewport = (GLint * 4)()

            glGetIntegerv(GL_VIEWPORT, viewport)
            glSelectBuffer(SIZE, select_buf)
            glRenderMode(GL_SELECT)

            glInitNames()
            glPushName(0)

            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluPickMatrix(GLdouble(x), GLdouble(viewport[3] - y), 5.0, 5.0, viewport)
            if self.disp.width <= self.disp.height:
                gluPerspective(45.0, self.disp.winHeight / self.disp.winWidth, 0.1, 10000.0)
            else:
                gluPerspective(45.0, self.disp.winWidth / self.disp.winHeight, 0.1, 10000.0)

            glMatrixMode(GL_MODELVIEW)
            self.DrawObjects()

            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glFlush()

            hits = glRenderMode(GL_RENDER)
            glMatrixMode(GL_MODELVIEW)

            ptr = select_buf
            if hits > 0:
                closest_hit = WorldObject(Vector2D(10000, 10000))
                closest_len = (Vector3D(closest_hit.GetLocation().x, closest_hit.GetLocation().y,
                                        0.0) - self.eye).GetLength()

                for i in range(hits):
                    names = ptr[0]
                    ptr += 3
                    for j in range(names):
                        v_new = (Vector3D(self.worldobjects[ptr[0] - 1].GetLocation().x,
                                          self.worldobjects[ptr[0] - 1].GetLocation().y, 0.0) - self.eye).GetLength()
                        if v_new < closest_len:
                            closest_len = v_new
                            closest_hit = self.worldobjects[ptr[0] - 1]
                        ptr += 1

                if closest_hit.IsMoveable():
                    self.mouse.current = closest_hit
                if closest_hit.IsSelectable():
                    self.mouse.selected = closest_hit

        # If world is two-dimensional
        else:
            for animat in self.animats:
                if animat.IsInside(self.mouse.location):
                    animat.OnClick()
                    if animat.IsMoveable():
                        self.mouse.current = animat
                    if animat.IsSelectable():
                        self.mouse.selected = animat
                    if animat.IsMoveable() or animat.IsSelectable():
                        break

            if self.mouse.current is None:
                for obj in self.worldobjects:
                    if obj.IsInside(self.mouse.location):
                        obj.OnClick()
                        if obj.IsMoveable():
                            self.mouse.current = obj
                        if obj.IsSelectable():
                            self.mouse.selected = obj
                        if obj.IsMoveable() or obj.IsSelectable():
                            break

        if self.mouse.current is None:
            self.mouse.selected = None
        else:
            self.mouse.current.OnSelect()

    def OnMouseRDown(self, x, y):
        self.mouse.right = True

        if self.mouse.current is not None:
            self.mouse.staticLocation = self.mouse.location

    def OnMouseLUp(self, x, y):
        self.mouse.left = False
        self.mouse.location = self.WindowXY(x, y)

        if self.mouse.current is not None:
            if not self.mouse.right and self.disp.dimension == TWO:
                self.mouse.current.SetLocation(self.mouse.location)
            self.mouse.current = None

    def OnMouseRUp(self, x, y):
        self.mouse.right = False

        if self.mouse.left:
            self.mouse.current = None

    def OnMouseMove(self, x, y):

        if self.disp.dimension == THREE and self.mouse.right:
            new_loc = self.WindowXY(x, y)

            diff = new_loc - self.mouse.location
            direction = diff.GetAngle()
            temp = self.eye - self.look
            rotate_z = Vector3D(0.0, 0.0, 1.0)
            norm = rotate_z.cross(self.look - self.eye)
            circ = 2 * np.pi * temp.GetLength()
            move = 0.02

            if direction >= 0.25 * np.pi and direction <= 0.75 * np.pi:
                move = -move
                temp.Rotate(move)
            elif direction >= 1.25 * np.pi or direction <= -0.25 * np.pi:
                temp.Rotate(move)
            elif direction < 1.25 * np.pi and direction > 0.75 * np.pi:
                temp.Rotate(move)
            elif direction > -0.25 * np.pi or direction < 0.25 * np.pi:
                move = -move
                temp.Rotate(move)

            self.eye = temp + self.look
            self.mouse.location = new_loc
        else:
            self.mouse.location = self.WindowXY(x, y)

    def OnSelectNext(self):

        a = None

        if self.mouse.selected is not None:
            for a in self.animats:
                if a == self.mouse.selected:
                    break
            self.mouse.selected = a

        if a is None:
            for a in self.animats:
                if a.IsSelectable:
                    break
        if a is not None:
            index = self.animats.index(a)
            index += 1
            if index == len(self.animats):
                index = self.mouse.selected
            while not self.animats[index].IsSelectable:
                index += 1
                if index == len(self.animats):
                    index = 0
            self.mouse.selected = self.animats[index]
        else:
            self.mouse.selected = a
    def OnSelectPrevious(self):

        a = None

        if self.mouse.selected is not None:
            # Search for the selected animat in reverse
            for a in reversed(self.animats):
                if a == self.mouse.selected:
                    a = a
                    break

        if a is None:
            # If no selected animat found, search for the first selectable animat in reverse
            for a in reversed(self.animats):
                if a.isSelectable:
                    a = a
                    break

        if a is not None:
            # If a selectable animat is found, iterate to the previous selectable animat
            index = self.animats.index(a)
            index -= 1
            if index < 0:
                index = len(self.animats) - 1
            while not self.animats[index].isSelectable:
                index -= 1
                if index < 0:
                    index = len(self.animats) - 1
            self.mouse.selected = self.animats[index]
        else:
            self.mouse.selected = None

    def OnKeyDown(self, k, c, shift):
        if k == self.key.wxLeft:
            self.key.left = True
        elif k == self.key.wxRight:
            self.key.right = True
        elif k == self.key.wxUp:
            self.key.up = True
        elif k == self.key.wxDown:
            self.key.down = True
        elif (c == '=' and shift) or c == '+':
            self.key.add = True
        elif c == '-' and not shift:
            self.key.sub = True

    def OnKeyUp(self, k, c, shift):
        if k == self.key.wxLeft:
            self.key.left = False
        elif k == self.key.wxRight:
            self.key.right = False
        elif k == self.key.wxUp:
            self.key.up = False
        elif k == self.key.wxDown:
            self.key.down = False
        elif c == '=' or c == '+':
            self.key.add = False
        elif c == '-':
            self.key.sub = False

    # -----------------------------------------------------------------------------------------------------------------
    # Mutators:

    def SetWidth(self, w):
        self.disp.width = w

    def SetHeight(self, h):
        self.disp.height = h

    def Toggle(self, t):
        self.disp.config ^= t
    def SetWindow(self, w, h):
        self.disp.winWidth = w
        self.disp.winHeight = h

    # def SetColour(self, c):
    #     self.SetColour(c[0], c[1], c[2])

    def SetColour(self, r, g, b):
        self.disp.colour = [r, g, b]
        glClearColor(r, g, b, 1.0)

    def SetWXKLeft(self, k):
        self.key.wxLeft = k

    def SetWXKRight(self, k):
        self.key.wxRight = k

    def SetWXKUp(self, k):
        self.key.wxUp = k

    def SetWXKDown(self, k):
        self.key.wxDown = k

    # ------------------------------------------------------------------------------------------------------------------
    # Accessors
    def GetWidth(self) -> float:
        """
        Returns the current width of the world.
        """

        return self.disp.width

    def GetHeight(self) -> float:
        """
        Returns the hight of the world.
        """
        return self.disp.height

    def GetWinWidth(self) -> int:
        """
        Returns window width in pixel.
        """
        return int(self.disp.winWidth)

    def GetWinHeight(self) -> int:
        """
        Returns window height in pixel.
        """
        return int(self.disp.winHeight)

    def GetDispConfig(self) -> SimpleNamespace:
        """
        Returns display config
        """
        return self.disp.config

    def GetWorldDimensions(self) -> int:
        """
        Returns world dimension (2D, 3D)
        """
        return self.disp.dimension

    def IsUpdating(self) -> bool:
        """
        Returns true if world is udpating
        """
        return self.updateInProgress

    def GetSelected(self) -> Union[WorldObject, None]:
        """
        Get selected object
        """

        return self.mouse.selected

    def Get(self, T: "T") -> List[Union[WorldObject, Animat]]:
        """
        :param T: object type
        :return: List of all worldobject and animats of requested type
        """
        return [ani for ani in self.animats if isinstance(ani, T)] + [wo for wo in self.worldobjects if isinstance(wo, T)]

    # -----------------------------------------------------------------------------------------------------------------
    # Helpers:
    # -----------------------------------------------------------------------------------------------------------------

    def Centre(self):
        return Vector2D(self.disp.width / 2.0, self.disp.height / 2.0)

    def RandomLocation(self):
        return Vector2D(self.disp.width * np.random.rand(), self.disp.height * np.random.rand())

    def WindowXY(self, x, y):

        x = x / self.disp.winWidth * self.disp.width
        y = ((self.disp.winHeight - y) / self.disp.winHeight) * self.disp.height

        return Vector2D(x,y)

    def MoveEye(self):
        if self.key.left and not self.key.right:
            c2 = Vector3D(0.0, 0.0, 1.0)
            norm = c2.Cross(self.look - self.eye)
            norm.normalise()
            self.eye += norm * 6
            self.look += norm * 6
        elif not self.key.left and self.key.right:
            c2 = Vector3D(0.0, 0.0, 1.0)
            norm = c2.Cross(self.look - self.eye)
            norm.normalise()
            self.eye -= norm * 6
            self.look -= norm * 6

        if self.key.up and not self.key.down:
            dir = Vector2D(self.look.x - self.eye.x, self.look.y - self.eye.y)
            dir.Normalize()
            xChange = dir.x * 6
            yChange = dir.y * 6
            self.eye.x += xChange
            self.eye.y += yChange
            self.look.x += xChange
            self.look.y += yChange
        elif not self.key.up and self.key.down:
            dir = Vector2D(self.look.x - self.eye.x, self.look.y - self.eye.y)
            dir.Normalize()
            xChange = dir.x * 6
            yChange = dir.y * 6
            self.eye.x -= xChange
            self.eye.y -= yChange
            self.look.x -= xChange
            self.look.y -= yChange

        if self.key.add and not self.key.sub:
            dir = self.look - self.eye
            dir.normalise()
            self.eye += (dir * 6)
        elif not self.key.add and self.key.sub:
            dir = self.look - self.eye
            dir.normalise()
            self.eye -= (dir * 6)

        if self.look.x < 0.0:
            self.look.x = 0.0
        elif self.look.x > self.disp.width:
            self.look.x = self.disp.width

        if self.look.y < 0.0:
            self.look.y = 0.0
        elif self.look.y > self.disp.height:
            self.look.y = self.disp.height

    # -----------------------------------------------------------------------------------------------------------------
    # TODO: Don't know what this is about
    # -----------------------------------------------------------------------------------------------------------------
    def World2D(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.disp.width, 0, self.disp.height)
        glMatrixMode(GL_MODELVIEW)
        self.disp.dimension = TWO

        self.Display()

    def World3D(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        if self.disp.width <= self.disp.height:
            gluPerspective(45.0, self.disp.winHeight / self.disp.winWidth, 0.1, 10000.0)
        else:
            gluPerspective(45.0, self.disp.winWidth / self.disp.winHeight, 0.1, 10000.0)

        glMatrixMode(GL_MODELVIEW)
        self.disp.dimension = THREE

        self.Display()





