#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  king_phisher/client/windows/plugin_manager.py
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of the project nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from king_phisher.client import gui_utilities
from king_phisher.client.widget import managers

from gi.repository import Gtk

__all__ = ('PluginManagerWindow',)

class PluginManagerWindow(gui_utilities.GladeGObject):
	dependencies = gui_utilities.GladeDependencies(
		children=(
			'treeview_plugins',
		)
	)
	top_gobject = 'window'
	def __init__(self, *args, **kwargs):
		super(PluginManagerWindow, self).__init__(*args, **kwargs)
		treeview = self.gobjects['treeview_plugins']
		self.treeview_manager = managers.TreeViewManager(treeview, cb_refresh=self.load_plugins)
		toggle_renderer = Gtk.CellRendererToggle()
		toggle_renderer.connect('toggled', self.signal_renderer_toggled)
		self.treeview_manager.set_column_titles(
			('Enabled', 'Plugin'),
			column_offset=1,
			renderers=(toggle_renderer, Gtk.CellRendererText())
		)
		self._model = Gtk.ListStore(str, bool, str)
		self._model.set_sort_column_id(2, Gtk.SortType.DESCENDING)
		treeview.set_model(self._model)
		self.load_plugins()
		self.window.show()

	def load_plugins(self):
		store = self._model
		store.clear()
		pm = self.application.plugin_manager
		pm.load_all()
		for plugin in pm.loaded_plugins.values():
			store.append((
				plugin.name,
				plugin.name in pm.enabled_plugins,
				plugin.title
			))

	def signal_renderer_toggled(self, _, path):
		pm = self.application.plugin_manager
		name = self._model[path][0]
		if self._model[path][1]:
			pm.disable(name)
			self._model[path][1] = False
			self.config['plugins.enabled'].remove(name)
		else:
			pm.enable(name)
			self._model[path][1] = True
			self.config['plugins.enabled'].append(name)
