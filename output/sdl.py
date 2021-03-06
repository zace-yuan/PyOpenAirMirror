import config

from output.FrameSink import FrameSink

try:
	import sdl2
	import ctypes

	class SDL2Renderer(FrameSink):

		cmdLineKey = "sdl"

		def __c(self, s):
			return ctypes.cast(ctypes.create_string_buffer(s, len(s)), ctypes.POINTER(ctypes.c_ubyte))

		def start(self):
			sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
			self.window = None

		def handle(self, frame, timestamp):
			if self.window is None:
				self.setupWindow(frame.width, frame.height)

			sdl2.SDL_UpdateYUVTexture(self.texture, None,
					self.__c(frame.y), frame.width,
					self.__c(frame.u), frame.width / 2,
					self.__c(frame.v), frame.width / 2)
			sdl2.render.SDL_RenderClear(self.renderer)
			sdl2.render.SDL_RenderCopy(self.renderer, self.texture, None, None)
			sdl2.render.SDL_RenderPresent(self.renderer)
			sdl2.SDL_PollEvent(None)

		def finish(self):
			if self.window:
				sdl2.SDL_DestroyTexture(self.texture)
				sdl2.SDL_DestroyRenderer(self.renderer)
				sdl2.SDL_DestroyWindow(self.window)
			sdl2.SDL_Quit()

		def setupWindow(self, width, height):
			self.window = sdl2.SDL_CreateWindow("%s: %s" % (config.sdl_window_caption, self.clientName), sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED, width, height, sdl2.SDL_WINDOW_SHOWN)

			self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_ACCELERATED)
			self.texture = sdl2.SDL_CreateTexture(self.renderer, sdl2.SDL_PIXELFORMAT_YV12, sdl2.SDL_TEXTUREACCESS_STREAMING, width, height)

except ImportError:
	import pygame

	class PyGameRenderer(FrameSink):

		cmdLineKey = "sdl"

		def start(self):
			pygame.init()
			pygame.display.set_caption("%s: %s" % (config.sdl_window_caption, self.clientName))
			self.clock = pygame.time.Clock()
			self.window = None

		def handle(self, frame, timestamp):
			if self.window is None:
				self.setupWindow(frame)

			# No idea why I need to keep that, but otherwise overlay.display crashes
			dummyBufBecauseItSucks = "%s%s%s" % (frame.y, frame.u, frame.v)
			self.overlay.display((frame.y, frame.u, frame.v))
			dummyBufBecauseItSucks = ""
			pygame.event.get()
			#self.clock.tick(10)

		def finish(self):
			pygame.display.quit()

		def setupWindow(self, frame):
			self.window = pygame.display.set_mode((frame.width, frame.height))
			self.overlay = pygame.Overlay(pygame.YV12_OVERLAY, (frame.width, frame.height))
