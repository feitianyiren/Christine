#! /usr/bin/env python
# -*- coding: latin-1 -*-

## Copyright (c) 2006 Marco Antonio Islas Cruz
## <markuz@islascruz.org>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


from libchristine.gui.GtkMisc import GtkMisc
from libchristine.Share import Share
from libchristine.Translator import  translate
from libchristine.libs_christine import lib_library
from christineLogger import christineLogger
from libchristine.Storage.sqlitedb import sqlite3db
import gtk

(LIST_NAME,
LIST_TYPE,
LIST_PIXBUF) = xrange(3)

class sources_list (GtkMisc):
	def __init__(self):
		GtkMisc.__init__(self)
		self.__logger = christineLogger('sources_list')
		self.__db = sqlite3db()
		idlist = self.__db.PlaylistIDFromName(list)
		if idlist != None:
			idlist = idlist['id']
		self.__Share = Share()
		self.xml = self.__Share.getTemplate('SourcesList','vbox')
		self.__gen_model()
		self.treeview = self.xml["treeview"]
		self.treeview.set_headers_visible(True)
		self.treeview.set_model(self.model)
		self.vbox = self.xml['vbox']
		addButton = self.xml['addSource']
		delButton = self.xml['delSource']

		addButton.connect('clicked', self.__addSource)
		delButton.connect('clicked', self.__delSource)
		self.__append_columns()

	def __gen_model(self):
		if not getattr(self,'model',False):
			self.model = gtk.ListStore(str,str,gtk.gdk.Pixbuf)
		else:
			self.model.clear()
		sources = self.__db.getPlaylists()
		#p = os.path.join(os.environ["HOME"],".christine","sources")
		#files = os.listdir(p)
		for source in sources:
			#file = os.path.join(os.environ["HOME"],".christine","sources",fname)
			#if os.path.isfile(os.path.join(file)):
			#fname = os.path.split(file)[-1]
			ltype = '1'
			iter = self.model.append()
			self.model.set(iter,
					LIST_NAME,source['name'],
					LIST_TYPE,ltype)

	def __append_columns(self):
		column = gtk.TreeViewColumn("Source")
		text = gtk.CellRendererText()
		pix= gtk.CellRendererPixbuf()
		column.pack_start(pix,False)
		column.pack_start(text,True)
		column.add_attribute(text,"text",LIST_NAME)
		column.add_attribute(pix,"pixbuf",LIST_PIXBUF)
		self.treeview.append_column(column)

	def __addSource(self,button):
		xml = self.__Share.getTemplate('NewSourceDialog')
		dialog = xml['dialog']
		entry = xml['entry']
		response = dialog.run()
		if response == 1:
			exists = False
			for row in self.model:
				print row, LIST_NAME
				name = row[LIST_NAME]
				if entry.get_text() != name:
					self.__db.addPlaylist(entry.get_text())
					self.__gen_model()
		dialog.destroy()


	def __delSource(self,button):
		xml = self.__Share.getTemplate('genericQuestion')
		dialog = xml['dialog']
		label = xml['label']
		label.set_text(translate('Are you sure\nThis cannot be undone'))
		response = dialog.run()
		if response == 1:
			selection = self.treeview.get_selection()
			model, iter = selection.get_selected()
			if iter != None:
				fname = model.get_value(iter, LIST_NAME)
				self.__db.removePlayList(fname)
			self.__gen_model()

		dialog.destroy()








