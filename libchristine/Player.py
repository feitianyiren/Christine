# -*- coding: latin-1 -*-
#
# This file is part of the Christine project
#
# Copyright (c) 2006-2007 Marco Antonio Islas Cruz
#
# Christine is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Christine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# @category  libchristine
# @package   Player
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @author    Miguel Vazquez Gocobachi <demrit@gnu.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt
import os
import pygst; pygst.require('0.10')
import gtk
import gobject
import cairo
import gst
import gst.interfaces

from libchristine.GtkMisc import GtkMisc,error
from libchristine.GstBase import *
from libchristine.Validator import *
from libchristine.christineConf import christineConf
import logging

BORDER_WIDTH = 0

#
# Player for manager play files
#
class Player(gtk.DrawingArea, GtkMisc, christineConf, object):
	"""
	Player for manage play files
	"""
	#
	# Constructor
	#
	def __init__(self):
		"""
		 Constructor
		"""
		self.__Logger = logging.getLogger('Player')
		GtkMisc.__init__(self)
		christineConf.__init__(self)
		gtk.DrawingArea.__init__(self)

		self.__ShouldShow = False
		self.__Type       = 'sound'

		self.set_property('events',
				gtk.gdk.ENTER_NOTIFY_MASK|
				gtk.gdk.LEAVE_NOTIFY_MASK|
				gtk.gdk.KEY_PRESS_MASK|
				gtk.gdk.KEY_RELEASE_MASK)
		events = self.get_property('events')
		self.connect('destroy',
				lambda x: self.VideoSink.set_xwindow_id(0L))
		self.connect('expose-event', self.exposeCallback)
		self.connect('event', self.__eventHandler)

		self.__createPlaybin()
		gobject.timeout_add(5000, self.__checkScreenSaver)

	def __eventHandler(self,widget,event):
		'''
		Catch the event
		'''
		return False

	#
	# Check if screensaver is active/desactive
	#
	# @return boolean
	def __checkScreenSaver(self):
		"""
		Check if we are whatching something with the player,
		if true, then deactivate the screensaver by resetting
		the idle time
		"""
		if self.__ShouldShow:
			a = os.popen('xscreensaver-command -deactivate 2&>/dev/null')
			b = os.popen('gnome-screensaver-command -d 2&> /dev/null')
		return True

	#
	# Creates playbin
	#
	# @return void
	def __createPlaybin(self):
		"""
		Create the playbin
		"""
		self.__Logger.info("Creating the Player")
		self.__PlayBin = self.__elementFactoryMake('playbin')
		self.__elementSetProperty(self.__PlayBin,'delay', GST_DELAY)

		self.play = self.__PlayBin
		self.bus  = self.__PlayBin.get_bus()

		self.__updateAudioSink()
		self.__updateVideoSink()
		self.__updateAspectRatio()

		self.notifyAdd('backend/audiosink',    self.__updateAudioSink)
		self.notifyAdd('backend/videosink',    self.__updateVideoSink)
		self.notifyAdd('backend/aspect-ratio', self.__updateAspectRatio)

		self.__updateAudioSink()
		self.__updateVideoSink()

		active = self.getBool("ui/visualization")
		if active:
			self.setVisualization(False)
		self.setVisualization(active)


		self.__connect()

		self.query_duration = self.__PlayBin.query_duration
		self.query_position = self.__PlayBin.query_position

	#
	# Connect
	#
	# @return void
	def __connect(self):
		"""
		Connect
		"""
		self.__Logger.info("Connecting sinks")
		self.__elementSetProperty(self.__PlayBin,'audio-sink', self.__AudioSinkPack)
		self.__elementSetProperty(self.__PlayBin,'video-sink', self.VideoSink)

	#
	# Updates audio sink
	#
	# @return void
	def __updateAudioSink(self, client = '', cnx_id = '', entry = '', userdata = ''):
		"""
		Updates audio sink
		"""
		self.__Logger.info("__updateAudioSink")
		state = self.getState()[1]
		self.__AudioSinkPack = self.__elementFactoryMake('bin')

		if (not isNull(self.getLocation())):
			self.pause()

		asink = self.getString('backend/audiosink')

		self.__AudioSink = self.__elementFactoryMake(asink)
		self.__AudioSinkPack.add(self.__AudioSink)

		self.audio_ghost = gst.GhostPad('sink', self.__AudioSink.get_pad('sink'))
		self.__AudioSinkPack.add_pad(self.audio_ghost)

		self.__elementSetProperty(self.__PlayBin,'audio-sink', self.__AudioSinkPack)

		if (asink == 'alsasink'):
			self.__AudioSink.set_property('device', 'default')

		if (gst.State(gst.STATE_PLAYING) == state):
			self.playIt()

	#
	# Updates video sink
	#
	# @return void
	def __updateVideoSink(self, client = '', cnx_id = '', entry = '', userdata = ''):
		"""
		Updates video sink
		"""
		state = self.getState()[1]

		if (not isNull(self.getLocation())):
			self.pause()

		vsink = self.getString('backend/videosink')

		self.VideoSink = self.__elementFactoryMake(vsink)
		self.__elementSetProperty(self.__PlayBin,'video-sink', self.VideoSink)

		if (vsink in ['xvimagesink', 'ximagesink']):
			self.VideoSink.set_property('force-aspect-ratio', True)

		if (gst.State(gst.STATE_PLAYING) == state):
			self.playIt()
			#self.exposeCallback()

	#
	# Updates aspect ratio
	#
	# @return void
	def __updateAspectRatio(self, client = '', cnx_id = '', entry = '', userdata = ''):
		"""
		Updates aspect ratio
		"""
		aspect_ratio = self.getString('backend/aspect-ratio')

		if (not isNull(aspect_ratio)):
			self.VideoSink.set_property('pixel-aspect-ratio', aspect_ratio)

	def __elementFactoryMake(self,element):
		'''
		Wrap the gst.element_factory_make, but add logging capabilities

		@param element: element to be created (str)
		'''
		self.__Logger.info("creatign a gst element %s"%element)
		return gst.element_factory_make(element)

	def __elementSetProperty(self,element,property,value):
		'''
		Wrap the self.(element).set_property, but add logging capabilities

		@parame element: gst.Element
		@param property: string Property
		@param value: property value
		'''
		self.__Logger.info("setting property '%s' with value '%s 'for element '%s'"%(property,repr(value),repr(element)))
		element.set_property(property,value)

	def emitExpose(self):
		self.exposeCallback()
		return False


	#
	# Draw the player
	#
	# @return void
	def exposeCallback(self, window = None, event = None):
		"""
		Draw the player
		"""
		# Drawing a black background because some
		# GTK themes (clearlooks) don't draw it

		(x, y, w, h) = self.allocation
		try:
			self.__Context = self.window.cairo_create()
		except:
			return False

		self.__Context.rectangle(BORDER_WIDTH, BORDER_WIDTH,
		                         w - 2 * BORDER_WIDTH,
		                         h - 2 * BORDER_WIDTH)
		self.__Context.clip()

		self.__Context.rectangle(BORDER_WIDTH, BORDER_WIDTH,
		                         w - 2 * BORDER_WIDTH,
		                         h - 2 * BORDER_WIDTH)

		self.__Context.set_source_rgba(0,0,0)
		self.__Context.fill_preserve()
		self.__Context.set_source_rgb(0,0,0)
		self.__Context.stroke()


		self.VideoSink.set_xwindow_id(self.window.xid)
		if self.__ShouldShow:
			self.show()
		return True


	#
	# Sets location
	#
	# @return string file
	# @return string
	def setLocation(self, file):
		self.__Tags = {}
		self.Tags = self.__Tags

		if self.__visualizationPlugin is not None:
			self.__elementSetProperty(self.__PlayBin,'vis-plugin', self.__visualizationPlugin)

		if (isFile(file)):
			self.__setState(gst.STATE_READY)
			nfile = 'file://' + file
			self.__elementSetProperty(self.__PlayBin,'uri', nfile)
			if self.isVideo():
				self.VideoSink.set_property('force-aspect-ratio', True)
		else:
			if (file.split(':')[0] in ['http', 'dvd', 'vcd']):
				self.__elementSetProperty(self.__PlayBin,'uri', file)
			else:
				error("file %s not found" % os.path.split(file)[1])

		self.getType()
		self.exposeCallback()

	#
	# Gets location
	#
	# @return string
	def getLocation(self):
		"""
		Gets location
		"""
		path = self.__PlayBin.get_property('uri')

		if (not isNull(path)):
			if (path.split(':')[0] == 'file'):
				path = path[7:]
			else:
				return path
		else:
			path = None
		return path

	#
	# Play the current song
	#
	# @return void
	def playIt(self):
		"""
		Play the current song
		"""
		self.__setState(gst.STATE_PLAYING)

	#
	# Pause it
	#
	# @return void
	def pause(self):
		"""
		Pause the current song
		"""
		self.__setState(gst.STATE_PAUSED)

	#
	# Stop the current song
	#
	# @return void
	def stop(self):
		"""
		Stop the current song
		"""
		self.__setState(gst.STATE_NULL)

	def __setState(self,state):
		'''
		Sets the state of the playtin to the state in
		the state param.
		Add loggin capabilites

		@param: state: gst.STATE
		'''
		self.__Logger.info("Setting the state of the Playbin to %s"%repr(state))
		self.__PlayBin.set_state(state)

	#
	# Sets visualization active or desactive
	#
	# @param  boolean active
	# @return boolean
	def setVisualization(self, active = False):
		"""
		Sets visualization active or desactive
		"""
		self.__Logger.info("Setting visualization to %s"%repr(active))
		if active:
			self.__visualizationPlugin = self.__elementFactoryMake(self.getString('backend/vis-plugin'))
			self.VideoSink.set_property('force-aspect-ratio', self.isVideo())
			self.__ShouldShow = True
			self.__elementSetProperty(self.__PlayBin,'vis-plugin', self.__visualizationPlugin)
		else:
			self.__visualizationPlugin = None
			self.VideoSink.set_property('force-aspect-ratio', True)
			self.__ShouldShow = False
			self.__elementSetProperty(self.__PlayBin,'vis-plugin', None)
		return True


	#
	# Sets volume value
	#
	# @return boolean
	def setVolume(self, volume):
		if (volume < 0):
			volume = 0.0
		elif (volume > 1):
			volume = 1.0
		self.__Logger.info("Setting volme to %f"%volume)
		self.__elementSetProperty(self.__PlayBin,'volume', volume)

	#
	# Gets a specific tag
	#
	# @param  string key
	# @return string
	def getTag(self, key):
		"""
		Gets a specific tag
		"""
		try:
			return self.__Tags[key]
		except:
			return ""

	#
	# Callback to found tags
	#
	# @return void
	def foundTagCallback(self, tags):
		"""
		Callback to found tags
		"""
		if (len(tags.keys()) > 0):
			for i in tags.keys():
				self.__Tags[i] = tags[i]

	#
	# Gets current state
	#
	# @return string
	def getState(self):
		"""
		Gets current state
		"""
		return self.__PlayBin.get_state()

	#
	# Sets file type
	#
	# @return void
	def getType(self):
		"""
		Sets file type
		"""
		if (self.isVideo()):
			self.__Type = 'video'
		elif (self.isSound()):
			self.__Type = 'sound'
		else:
			self.__Type = "Unknown"
		return self.__Type

	#
	# Returns nano secs format
	#
	# @return string
	def nano2str(self,nanos):
		"""
		Returns something like 00:00:00.000000
		"""
		ts = (nanos / gst.SECOND)
		return '%02d:%02d:%02d.%06d' % ((ts / 3600), (ts / 60), (ts % 60), (nanos % gst.SECOND))

	#
	# Seek to secs
	#
	# @return void
	def seekTo(self, sec):
		"""
		Seek to secs
		"""
		sec = (long(sec) * gst.SECOND)
		self.__PlayBin.seek(1.0,
		        gst.FORMAT_TIME,    gst.SEEK_FLAG_FLUSH,
				gst.SEEK_TYPE_SET,  sec,
				gst.SEEK_TYPE_NONE, -1)

	#
	# Check if it is video or not
	#
	# @return boolean
	def isVideo(self):
		"""
		Check if it is video or not
		"""
		if (isNull(self.getLocation())):
			return False

		ext = self.getLocation().split('.').pop().lower()

		if (('video-codec' in self.__Tags.keys()) or (ext in video)):
			self.__ShouldShow = True
			return True
		else:
			return False

	#
	# Check if it is sound or not
	#
	# @return boolean
	def isSound(self):
		"""
		Check if it is sound or not
		"""
		if (isNull(self.getLocation())):
			return False

		ext = self.getLocation().split('.').pop().lower()

		if (('audio-codec' in self.__Tags.keys()) or (ext in sound)):
			return True
		else:
			return False
