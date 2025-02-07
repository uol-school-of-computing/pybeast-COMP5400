
# Third-party
import wx
from wx.glcanvas import GLCanvas, GLContext

from OpenGL.GL import *
#from OpenGL.GLUT import *
# Pybeast
from pybeast.core.world.world import World

class WorldGLCanvas(GLCanvas):
    """
    WorldGLCanvas class.

    The GL canvas for the main visualization window.

    m_pWorld (World): The world object associated with the canvas.
    """

    def __init__(self, parent: wx.Window, size: wx.Size, world: World):

        """
        Initialize WorldGLCanvas.

        :param world: The world object associated with the canvas.
        :param parent (wx.Window): The parent window.
        :param id (wx.WindowID): The window identifier.
        :param pos (wx.Point): The window position.
        :param size (wx.Size): The window size.
        :param style (long): The window style.
        :param name (str): The window name.
        """

        super().__init__(parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=size, style=wx.WANTS_CHARS,
            name="WorldGLCanvas")

        self.context = None
        self.init = False
        self.world = world
        self.InitGL()

        self.BindEvents()

    #================================================================================================
    # Initialization
    #================================================================================================

    def BindEvents(self):
        """
        Binds events
        """
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        # self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        # self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        # self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        # self.Bind(wx.EVT_RIGHT_UP, self.OnMouseRightUp)
        # self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        # self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        # self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

    def InitGL(self):
        """Initialize OpenGL."""
        self.context = GLContext(self)
        self.SetCurrent(self.context)

        #self.SetCurrent(self.context)
        size = self.GetSize()

        glViewport(0, 0, size.width, size.height)
        glFinish()

        self.world.InitGL()
        # Makes sure that all OpenGL commands have been completed before rendering loop starts
        glFinish()

        self.init = True

    #================================================================================================
    # Class interface
    #================================================================================================

    def Display(self):
        """Display the GL canvas."""
        self.SetCurrent(self.context)
        self.world.Display()
        glFinish()
        self.SwapBuffers()


    def CleanUp(self):
        """
        Clean up OpenGL resources
        """
        self.SetCurrent(self.context)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    #================================================================================================
    # Event handlers
    #================================================================================================

    def OnPaint(self, event):
        """Handle paint event."""
        if not self.init:
            self.InitGL()

        wx.PaintDC(self)
        self.Display()


    def OnSize(self, event):
        """Handle size event."""

        # Adjust canvas size to new size of the main frame
        width, height = event.GetSize()
        self.SetSize(width, height)

        # Sync OpenGL with new canvas size
        self.SetCurrent(self.context)
        glViewport(0, 0, width, height)
        glFinish()

    #================================================================================================
    # Setter and Getters
    #================================================================================================

    def SetWorld(self, world):
        self.world = world


    # def OnEraseBackground(self, event):
    #     """Handle erase background event."""
    #     pass  # Do nothing to avoid flashing
    #
    # def OnMouseLeftDown(self, event):
    #     """Handle left mouse button down event."""
    #     self.world.OnMouseLDown(event.GetX(), event.GetY())
    #
    # def OnMouseLeftUp(self, event):
    #     """Handle left mouse button up event."""
    #     self.world.OnMouseLUp(event.GetX(), event.GetY())
    #
    # def OnMouseRightDown(self, event):
    #     """Handle right mouse button down event."""
    #     self.world.OnMouseRDown(event.GetX(), event.GetY())
    #
    # def OnMouseRightUp(self, event):
    #     """Handle right mouse button up event."""
    #     self.world.OnMouseRUp(event.GetX(), event.GetY())
    #
    # def OnMouseMove(self, event):
    #     """Handle mouse move event."""
    #     self.world.OnMouseMove(event.GetX(), event.GetY())
    #
    # def OnKeyDown(self, event):
    #     """Handle key down event."""
    #     self.world.OnKeyDown(event.GetKeyCode(), event.GetUnicodeKey(), event.ShiftDown())
    #
    # def OnKeyUp(self, event):
    #     """Handle key up event."""
    #     self.world.OnKeyUp(event.GetKeyCode(), event.GetUnicodeKey(), event.ShiftDown())

