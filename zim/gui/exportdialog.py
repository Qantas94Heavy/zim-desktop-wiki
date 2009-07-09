# -*- coding: utf-8 -*-

# Copyright 2008 Jaap Karssenberg <pardus@cpan.org>

'''FIXME'''

import gtk

from zim.fs import *
from zim.gui import Dialog, ProgressBarDialog
from zim.exporter import Exporter
import zim.formats
import zim.templates

class ExportDialog(Dialog):
	'''FIXME'''

	def __init__(self, ui):
		Dialog.__init__(self, ui, _('Export'))
		#~ self.set_resizable(False)
		self.set_help('ExportDialog')

		# Pages ------------------------
		vbox = gtk.VBox(0, 5)
		vbox.set_border_width(12)
		self._add_with_frame(vbox, '<b>'+_('Pages')+'</b>')

		all_pages_radio = gtk.RadioButton(None, _('_Complete notebook'))
		selection_radio = gtk.RadioButton(all_pages_radio, _('_Selection'))
		#~ recursive_box = gtk.CheckButton('Recursive')
		vbox.add(all_pages_radio)
		vbox.add(selection_radio)
		selection_radio.set_sensitive(False)
		vbox.add(gtk.Label('TODO: selection input'))
		#~ vbox.add(recursive_box)
		#~ recursive_box.set_sensitive(False)

		self.uistate.setdefault('pages', 'all')
		self.uistate.setdefault('selection', '')
		#~ self.uistate.setdefault('recursive_selection', False)
		# FIXME wire these

		# Output ------------------------
		table = gtk.Table(5, 3)
		table.set_border_width(12)
		table.set_row_spacings(5)
		table.set_col_spacings(12)
		self._add_with_frame(table, '<b>'+_('Output')+'</b>')

		# Format
		table.attach(gtk.Label(_('Format')+': '), 0,1, 0,1)
		formats_combobox = gtk.combo_box_new_text()
		export_formats = zim.formats.list_formats(zim.formats.EXPORT_FORMAT)
		for name in export_formats:
			formats_combobox.append_text(name)
		table.attach(formats_combobox, 1,2, 0,1)
		self.inputs['format'] = formats_combobox

		self.uistate.setdefault('format', 'HTML')
		try:
			i = export_formats.index(self.uistate['format'])
			formats_combobox.set_active(i)
		except ValueError:
			pass

		# Template
		def set_templates(formats_combobox, templates_combobox):
			format = formats_combobox.get_active_text()
			# TODO clear templates_combobox
			template_dict = zim.templates.list_templates(format)
			templates = sorted(template_dict.keys())
			for name in templates:
				templates_combobox.append_text(name)
			templates_combobox.append_text(_('Other...'))
			templates_combobox.set_sensitive(True)
			template = self.uistate['template']
			if template == _('Other...'):
				templates_combobox.set_active(len(templates))
			else:
				try:
					i = templates.index(template)
					templates_combobox.set_active(i)
				except ValueError:
					pass

		table.attach(gtk.Label(_('Template')+': '), 0,1, 1,2)
		templates_combobox = gtk.combo_box_new_text()
		templates_combobox.set_sensitive(False)
		formats_combobox.connect('changed', set_templates, templates_combobox)
		table.attach(templates_combobox, 1,2, 1,2)
		self.inputs['template'] = templates_combobox
		self.uistate.setdefault('template', 'Default')

		other_template_selector = gtk.FileChooserButton(_('Please select a template file'))
		other_template_selector.set_sensitive(False)
		templates_combobox.connect('changed',
			lambda o: other_template_selector.set_sensitive(
							o.get_active_text() == _('Other...')) )
		table.attach(other_template_selector, 1,2, 2,3)
		self.inputs['template_file'] = other_template_selector
		self.uistate.setdefault('template_file', '')
		if self.uistate['template_file']:
			try:
				other_template_selector.set_filename(
					self.uistate['template_file'])
			except:
				pass

		set_templates(formats_combobox, templates_combobox)

		# Folder
		table.attach(gtk.Label(_('Output folder')+': '), 0,1, 3,4)
		output_folder_selector = gtk.FileChooserButton(_('Please select a folder'))
		output_folder_selector.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
		table.attach(output_folder_selector, 1,2, 3,4)
		self.inputs['output_folder'] = output_folder_selector
		self.uistate.setdefault('output_folder', '')
		if self.uistate['output_folder']:
			try:
				output_folder_selector.set_filename(
					self.uistate['output_folder'])
			except:
				pass

		# Index
		self.inputs['index_page'] = gtk.Entry()
		table.attach(gtk.Label(_('Index page')+': '), 0,1, 4,5)
		table.attach(self.inputs['index_page'], 1,2, 4,5)
		self.uistate.setdefault('index_page', '')
		self.inputs['index_page'].set_text(self.uistate['index_page'])

		# Documents ----------------------
		vbox = gtk.VBox(0, 5)
		vbox.set_border_width(12)
		self._add_with_frame(vbox, '<b>'+_('Documents')+'</b>')

		document_root_url_box = gtk.CheckButton(_('Map document root to URL')+': ')
		document_root_url_entry = gtk.Entry()
		document_root_url_entry.set_sensitive(False)
		if self.ui.notebook.get_document_root():
			document_root_url_box.connect('toggled',
				lambda o: document_root_url_entry.set_sensitive(o.get_active()) )
		else:
			document_root_url_box.set_sensitive(False)
		self.inputs['use_document_root_url'] = document_root_url_box
		self.inputs['document_root_url'] = document_root_url_entry
		self.uistate.setdefault('use_document_root_url', False)
		self.uistate.setdefault('document_root_url', '')
		self.inputs['use_document_root_url'].set_active(self.uistate['use_document_root_url'])
		self.inputs['document_root_url'].set_text(self.uistate['document_root_url'])

		include_documents_box = gtk.CheckButton(_('Include a copy of linked documents'))
		self.inputs['include_documents'] = include_documents_box
		self.uistate.setdefault('include_documents', False)
		self.inputs['include_documents'].set_active(self.uistate['include_documents'])

		hbox = gtk.HBox(0, 5)
		hbox.add(document_root_url_box)
		hbox.add(document_root_url_entry)
		vbox.add(hbox)
		vbox.add(include_documents_box)

	def _add_with_frame(self, widget, title):
		frame = gtk.Frame()
		label = gtk.Label()
		label.set_markup(title)
		frame.set_label_widget(label)
		frame.add(widget)
		self.vbox.add(frame)

	def do_response_ok(self):
		self.uistate['format'] = self.inputs['format'].get_active_text()
		self.uistate['template'] = self.inputs['template'].get_active_text()
		self.uistate['template_file'] = self.inputs['template_file'].get_filename()
		self.uistate['output_folder'] = self.inputs['output_folder'].get_filename()
		self.uistate['index_page'] = self.inputs['index_page'].get_text()
		self.uistate['use_document_root_url'] = self.inputs['use_document_root_url'].get_active()
		self.uistate['document_root_url'] = self.inputs['document_root_url'].get_text()
		self.uistate['include_documents'] = self.inputs['include_documents'].get_active()


		for k in ('format', 'template', 'output_folder'):
			if not self.uistate[k]: # ignore empty string as well
				logger.warn('Option %s not set', k)
				return False

		dir = Dir(self.uistate['output_folder'])

		options = {}
		for k in ('format', 'template', 'index_page', 'include_documents'):
			if self.uistate[k]: # ignore empty string as well
				options[k] = self.uistate[k]

		if options['template'] == _('Other...'):
			options['template'] = self.uistate['template_file']

		if self.uistate['use_document_root_url'] and self.uistate['document_root_url']:
			options['document_root_url'] = self.uistate['document_root_url']

		exporter = Exporter(self.ui.notebook, **options)

		dialog = ProgressBarDialog(self, _('Exporting notebook'))
		dialog.show_all()
		exporter.export_all(dir, callback=lambda p: dialog.pulse(p.name))
		dialog.destroy()
		return True
