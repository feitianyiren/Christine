#! /usr/bin/env python
# -*- coding: utf-8 -*-
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
# @category  Multimedia
# @package   Christine
# @author    Marco Antonio Islas Cruz <markuz@islascruz.org>
# @copyright 2006-2007 Christine Development Group
# @license   http://www.gnu.org/licenses/gpl.txt

from optparse import OptionParser
from libchristine.pattern.Singleton import Singleton


class options(Singleton):
    def __init__(self):
        '''
        Constructor. Parsea los valores que vienen en sys.argv[1:] y almacena
        los valores en self.options.
        
        Utiliza optparse para parsear las opciones.
        
        Las opciones disponibles son:
        
        self.options.debug (-v , --debug)
        self.options.daemon (-D, --daemon)
        '''
        usage ='%prog [args]'
        version = '%prog' 
        parser = OptionParser(usage = usage,version=version)
        parser.add_option("-d","--devel", dest="debug",action='store_true',
                  help="If christine must run in devel mode")
        parser.add_option("-v","--verbose", dest="verbose",action='store',
                type="string",
                  help="Force christine to dump the logs to the stdout")
        parser.add_option("-q","--quit", dest="quit",action='store_true',
                 help="Force christine to quit after startup")
        parser.add_option("-o","--use-new-main-window", dest="use_new_main_window",action='store_true',
                 help="Force christine to use the new mainWindow ")
        parser.add_option("-p","--append-podcast", dest="append_podcast",action='store',
                type='string', help="Append a podcast to the db.")
        parser.add_option("-g","--get-podcasts", dest="get_podcast",action='store_true',
                help="Prints the podcast")

        self.options, self.args = parser.parse_args()
        
    
