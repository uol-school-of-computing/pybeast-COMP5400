# OpenGL Dependencies

OS and version

- Red Hat Enterprise 8.10 64 bit

PyOpenGL: 3.1.6

PyOpenGL installs the Python package, which is a binding to the OpenGl API

It does **not** install the actual OpenGL libraries or drivers themselves

The PyOpenGL package depends on the OpenGL libraries and drivers provided by your operating system or GPU drivers 

- OpenGL library (e.g. libGL): These are provided by your operating system 
- GPU drivers: Provided by your graphics card manufacturer (NVIDIA, AMD, Intel). These drivers include the necessary libraries to interface wit your GPU and OpenGL

- **GLU**, **GLUT**, **GLEW**: While PyOpenGL covers the core OpenGL functionality, additional utilities like GLU (OpenGL Utility Library), GLUT (OpenGL Utility Toolkit) might be installed separately depending on your needs

Conclusion: Conda installs pyopengl just fine. Most likely the problem is that the code is not compatible with the OpenGL libraries and GPU drivers themselves

OpenGL libraries are OS specific and I should be able to create a docker which uses the same libraries than on my development environment

I can't do anything about the GPU drivers as they are hardware specific 

## OpenGl libraries

On **Linux**, OpenGl libraries are typically provided by the **Mesa** project or proprietary drivers from GPU manufacturers like NVDIA and AMD: 

1. libGL: This is the core OpenGL library that provides the OpenGL API. It includes the essential functions needed to interface with the GPU for rendering
2. libGLU: Provides higher-level drawing routines on top of the core OpenGL functions
3. libGLX: A library that facilitates the integration of OpenGL with the X Window System
4. libOSMesa: A special version of Mesa's OpenGL that allows rendering to an off-screen buffer rather than directly to display. Useful for headless rendering or server-side rendering
5. libEGL: Provides an interface between Khronos rendering APIs (like OpenGL ES) and the underlying native platform windowing system. Essential for setting up rendering contexts   

## Version numbers on development environment

mesa packages

- mesa-dri-drivers:
- mesa-filesystem

- **libGL**: version string: 4.6 (Compatibility Profile) Mesa 23.1.4
- **libGLU**: mesa-libGLU-9.0.0-15.el8.x84_64
- GLEW: not installed
- libGLX: mesa-libGL-23.1.4-2.el8.x84_64
- libOSMesa: not installed 
- GLUT: not installed
- **libEGL**: mesa-libEGL-23.1.4-2.el8.x86_64

## Running on Windows

When running a Python application that uses PyOpenGL on Windows, you won't be using Mesa or Wayland directly, as those are specific to Linux. Instead, you'll be relying on Windows-native libraries and drivers. Here's a guide to what you'll need on a Windows machine:

### 1. **OpenGL Implementation**
   - **Windows OpenGL Drivers**: Unlike Linux, where Mesa provides a software implementation of OpenGL, Windows relies on the GPU manufacturer's drivers (NVIDIA, AMD, or Intel) to provide hardware-accelerated OpenGL support. 
   - Ensure you have the latest drivers for your GPU installed. These drivers will include support for OpenGL, and you won't need to install separate libraries like mesa-libGL or mesa-libEGL.

### 2. **Equivalent Libraries for Windows**

   - **PyOpenGL**: This remains the same on both Windows and Linux. You can install it via pip:
     
     ```bash
     pip install PyOpenGL PyOpenGL_accelerate
     ```
     
   - **GLU (OpenGL Utility Library)**: PyOpenGL includes GLU functionality, so you don't need to install anything extra.

   - **GLUT (OpenGL Utility Toolkit)**: On Windows, you can use FreeGLUT, a free and open-source alternative to the original GLUT:
     
     - Download FreeGLUT from its [official website](http://freeglut.sourceforge.net/).
     - Add the FreeGLUT DLL to your system's PATH or the directory where your Python script resides.

### 3. **Wayland Alternative on Windows**
   - **Windows Native GUI**: Windows uses its own native windowing system, so Wayland is not applicable. PyOpenGL will work with Windows' native window management APIs via libraries like `pygame`, `Pyglet`, or `GLUT`.

   - If your application needs window creation, consider using:
     - **Pygame**: `pip install pygame`
     - **Pyglet**: `pip install pyglet`
     - **GLUT/FreeGLUT**: Used with PyOpenGL for window and context creation.

### 4. **Handling EGL and GBM**
   - **EGL and GBM**: These are specific to Linux (EGL for managing OpenGL contexts, GBM for buffer management). On Windows, OpenGL contexts and buffers are handled directly by the Windows drivers and the native OpenGL implementation provided by your GPU vendor.

### Summary of Steps to Set Up on Windows

1. **Install PyOpenGL**:
   ```bash
   pip install PyOpenGL PyOpenGL_accelerate
   ```

2. **Install FreeGLUT (if needed for window management)**:
   - Download and set up FreeGLUT from the official site or use a package manager like vcpkg to install it.

3. **Install the latest GPU drivers**:
   - Download the latest drivers from NVIDIA, AMD, or Intel, depending on your GPU.

4. **Use Windows-native libraries** for window and context management, such as `pygame`, `Pyglet`, or `FreeGLUT`.

This setup will allow your Python application that uses PyOpenGL to run on Windows, leveraging the native OpenGL support provided by the GPU drivers instead of the Mesa libraries used on Linux.

