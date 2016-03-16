# coding: utf-8
# Copyright (c) 2011-2013 gocept gmbh & co. kg
# See also LICENSE.txt

import os
import datetime
import tempfile
import sys
import logging

import gobject
import gtk
import gtk.glade
import pango

from gocept.gtimelog.util import virtual_day, calc_progress
from gocept.gtimelog.util import format_duration, format_duration_short
from gocept.gtimelog.util import uniq
import gocept.gtimelog.bugtracker
import gocept.gtimelog.collmex
import gocept.gtimelog.core
import pygtk
pygtk.require('2.0')

resource_dir = os.path.dirname(os.path.realpath(__file__))
ui_file = os.path.join(resource_dir, "gtimelog.glade")
icon_file = os.path.join(resource_dir, "gtimelog-small.png")


log = logging.getLogger(__name__)


class LogWindowHandler(logging.Handler):

    def __init__(self, main_window):
        logging.Handler.__init__(self)
        self.main_window = main_window

    def emit(self, record):
        self.main_window.w_debug(record)


class TrayIcon(object):
    """Tray icon for gtimelog."""

    def __init__(self, gtimelog_window):
        self.gtimelog_window = gtimelog_window
        self.timelog = gtimelog_window.timelog
        self.trayicon = None
        try:
            import egg.trayicon
        except ImportError:
            # nothing to do here, move along
            # or install python-gnome2-extras
            return

        self.tooltips = gtk.Tooltips()
        self.eventbox = gtk.EventBox()
        hbox = gtk.HBox()
        icon = gtk.Image()
        icon.set_from_file(icon_file)
        hbox.add(icon)
        self.time_label = gtk.Label()
        hbox.add(self.time_label)
        self.eventbox.add(hbox)
        self.trayicon = egg.trayicon.TrayIcon("GTimeLog")
        self.trayicon.add(self.eventbox)
        self.last_tick = False
        self.tick(force_update=True)
        self.trayicon.show_all()
        tray_icon_popup_menu = gtimelog_window.tray_icon_popup_menu
        self.eventbox.connect_object("button-press-event", self.on_press,
                                     tray_icon_popup_menu)
        self.eventbox.connect("button-release-event", self.on_release)
        gobject.timeout_add(1000, self.tick)
        self.gtimelog_window.entry_watchers.append(self.entry_added)

    def on_press(self, widget, event):
        """A mouse button was pressed on the tray icon label."""
        if event.button != 3:
            return
        main_window = self.gtimelog_window.main_window
        if main_window.get_property("visible"):
            self.gtimelog_window.tray_show.hide()
            self.gtimelog_window.tray_hide.show()
        else:
            self.gtimelog_window.tray_show.show()
            self.gtimelog_window.tray_hide.hide()
        widget.popup(None, None, None, event.button, event.time)

    def on_release(self, widget, event):
        """A mouse button was released on the tray icon label."""
        if event.button != 1:
            return
        main_window = self.gtimelog_window.main_window
        if main_window.get_property("visible"):
            main_window.hide()
        else:
            main_window.present()

    def entry_added(self, entry):
        """An entry has been added."""
        self.tick(force_update=True)

    def tick(self, force_update=False):
        """Tick every second."""
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        if now != self.last_tick or force_update:  # Do not eat CPU too much
            self.last_tick = now
            last_time = self.timelog.window.last_time()
            if last_time is None:
                self.time_label.set_text(now.strftime("%H:%M"))
            else:
                self.time_label.set_text(
                    format_duration_short(now - last_time))
        self.tooltips.set_tip(self.trayicon, self.tip())
        return True

    def tip(self):
        """Compute tooltip text."""
        current_task = self.gtimelog_window.task_entry.get_text()
        if not current_task:
            current_task = "nothing"
        tip = "GTimeLog: working on %s" % current_task
        total_work, total_slacking, total_holidays = (
            self.timelog.window.totals())
        tip += "\nWork done today: %s" % format_duration(total_work)
        time_left = self.gtimelog_window.time_left_at_work(total_work)
        if time_left is not None:
            if time_left < datetime.timedelta(0):
                time_left = datetime.timedelta(0)
            tip += "\nTime left at work: %s" % format_duration(time_left)
        return tip


class TimelogStatusbar(object):
    """The Gtimelog Statusbar"""

    def __init__(self, tree):
        self.statusbar = tree.get_widget("statusbar")
        self.statusbarmsgids = []

    def post_message(self, msg):
        """Writes a msg to the statusbar"""
        print msg
        contextid = len(self.statusbarmsgids)
        msgid = self.statusbar.push(contextid, msg)
        self.statusbarmsgids.append(msgid)


class WorkProgressbar(object):
    """Progressbar to show easily how much worktime is todo."""

    def __init__(self, tree, settings, timelog):
        self.week_hours = settings.week_hours
        self.visibility_state = True
        self.timelog = timelog
        self.settings = settings
        self.from_week = timelog.day

        self.progressbar = tree.get_widget("workprogress")

        self.calendar_dialog = tree.get_widget("calendar_dialog")
        self.calendar = tree.get_widget("calendar")

        self.from_week_window_btn = tree.get_widget("from_week_window_button")
        self.from_week_window_btn.connect("clicked", self.set_from_week)

        self.update()

    def update(self):
        """Updates the progress bar.

        week_window = timedelta of the current week
        """
        min, max, weeks = self.get_timeframe()

        week_done, week_exp, week_todo = calc_progress(
            self.settings, self.timelog, (min, max))

        if week_exp == 0:
            percent = 0.0
        else:
            percent = week_done / week_exp
        if percent > 1.0:
            percent = 1.0
        self.progressbar.set_fraction(percent)
        work_text = (
            u"%s – %s: %s h still to work (%s h required, %s h done)" % (
                min.strftime('%Y-%m-%d'), max.strftime('%Y-%m-%d'), week_todo,
                int(week_exp), week_done))
        self.progressbar.set_text("%s" % work_text)

    def set_from_week(self, widget):
        self.from_week = self.get_clicked_calendar_day()
        self.update()

    def get_clicked_calendar_day(self):
        if self.calendar_dialog.run() == gtk.RESPONSE_OK:
            y, m1, d = self.calendar.get_date()
            date = datetime.date(y, m1 + 1, d)
        else:
            date = None
        self.calendar_dialog.hide()
        return date

    def get_timeframe(self):
        """Returns from dates and to dates used for calulating the
           weekly time-window. Addtionally the number of weeks is
           returned.

           Returns (min, max, weekcount)
        """
        day = self.from_week
        monday = day - datetime.timedelta(day.weekday())
        min = datetime.datetime.combine(monday,
                                        self.timelog.virtual_midnight)
        this_monday = (self.timelog.day -
                       datetime.timedelta(self.timelog.day.weekday()))
        max = datetime.datetime.combine(
            this_monday + datetime.timedelta(7), self.timelog.virtual_midnight)
        delta = max - min
        weeks = delta.days / 7
        if delta.days <= 0:
            # start in future
            weeks = abs(weeks) + 1
        return (min, max, weeks)

    def week_window(self, min, max):
        return self.timelog.window_for(min, max)

    def toggle_visibility(self):
        if self.visibility_state:
            self.progressbar.hide()
            self.from_week_window_btn.hide()
            self.visibility_state = False
        else:
            self.progressbar.show()
            self.from_week_window_btn.show()
            self.visibility_state = True


class MainWindow(object):
    """Main application window."""

    view = 'chronological'
    footer_mark = None

    # Try to prevent timer routines mucking with the buffer while we're
    # mucking with the buffer.  Not sure if it is necessary.
    lock = False

    def __init__(self, timelog, settings, tasks):
        """Create the main window."""
        self.timelog = timelog
        self.settings = settings
        self.tasks = tasks
        self.last_tick = None
        self.entry_watchers = []
        tree = gtk.glade.XML(ui_file)
        tree.signal_autoconnect(self)
        self.tray_icon_popup_menu = tree.get_widget("tray_icon_popup_menu")
        self.tray_show = tree.get_widget("tray_show")
        self.tray_hide = tree.get_widget("tray_hide")
        self.about_dialog = tree.get_widget("about_dialog")
        self.about_dialog_ok_btn = tree.get_widget("ok_button")
        self.about_dialog_ok_btn.connect("clicked", self.close_about_dialog)
        self.calendar_dialog = tree.get_widget("calendar_dialog")
        self.calendar = tree.get_widget("calendar")
        self.calendar.connect("day_selected_double_click",
                              self.on_calendar_day_selected_double_click)
        self.statusbar = TimelogStatusbar(tree)
        self.workprogressbar = WorkProgressbar(tree, settings, timelog)
        self.main_window = tree.get_widget("main_window")
        self.main_window.connect("delete_event", self.delete_event)
        self.log_view = tree.get_widget("log_view")
        self.set_up_log_view_columns()
        self.debug_view = tree.get_widget("debug_view")
        self.debug_buffer = self.debug_view.get_buffer()
        tasks.loading_callback = self.task_list_loading
        tasks.loaded_callback = self.task_list_loaded
        tasks.error_callback = self.task_list_error
        self.task_list = tree.get_widget("task_list")
        self.task_store = gtk.TreeStore(str, str)
        self.task_list.set_model(self.task_store)
        column = gtk.TreeViewColumn("Task", gtk.CellRendererText(), text=0)
        self.task_list.append_column(column)
        self.task_list.connect("row_activated", self.task_list_row_activated)
        self.task_list_popup_menu = tree.get_widget("task_list_popup_menu")
        self.task_list.connect_object("button_press_event",
                                      self.task_list_button_press,
                                      self.task_list_popup_menu)
        task_list_edit_menu_item = tree.get_widget("task_list_edit")
        if not self.settings.edit_task_list_cmd:
            task_list_edit_menu_item.set_sensitive(False)
        self.time_label = tree.get_widget("time_label")
        self.task_entry = tree.get_widget("task_entry")
        self.task_entry.connect("changed", self.task_entry_changed)
        self.task_entry.connect("key_press_event", self.task_entry_key_press)
        self.add_button = tree.get_widget("add_button")
        self.add_button.connect("clicked", self.add_entry)
        buffer = self.log_view.get_buffer()
        self.log_buffer = buffer
        buffer.create_tag('today', foreground='blue')
        buffer.create_tag('duration', foreground='red')
        buffer.create_tag('time', foreground='green')
        buffer.create_tag('slacking', foreground='gray')
        self.set_up_task_list()
        self.set_up_completion()
        self.set_up_history()
        self.populate_log()
        self.tick(True)
        gobject.timeout_add(1000, self.tick)

    def set_up_log_view_columns(self):
        """Set up tab stops in the log view."""
        pango_context = self.log_view.get_pango_context()
        em = pango_context.get_font_description().get_size()
        tabs = pango.TabArray(2, False)
        tabs.set_tab(0, pango.TAB_LEFT, 9 * em)
        tabs.set_tab(1, pango.TAB_LEFT, 12 * em)
        self.log_view.set_tabs(tabs)

    def w(self, text, tag=None):
        """Write some text at the end of the log buffer."""
        buffer = self.log_buffer
        if tag:
            buffer.insert_with_tags_by_name(buffer.get_end_iter(), text, tag)
        else:
            buffer.insert(buffer.get_end_iter(), text)

    def w_debug(self, record):
        """Write debug lines in the debug window."""
        self.debug_buffer.insert(
            self.debug_buffer.get_end_iter(), '%s\n' % record.getMessage())

    def populate_log(self):
        """Populate the log."""
        self.lock = True
        buffer = self.log_buffer
        buffer.set_text("")
        if self.footer_mark is not None:
            buffer.delete_mark(self.footer_mark)
            self.footer_mark = None
        today = virtual_day(datetime.datetime.now(),
                            self.timelog.virtual_midnight)
        today = today.strftime('%A, %Y-%m-%d (week %V)')
        self.w(today + '\n\n', 'today')
        if self.view == 'chronological':
            for item in self.timelog.window.all_entries():
                self.write_item(item)
        elif self.view == 'weekly':
            window = self.weekly_window()
            entries = iter(window.all_entries())
            entries.next()  # ignore first
            projects = {}
            for start, stop, dur, entry in entries:
                if '**' in entry:
                    continue
                project = entry.split(':')[0].lower()
                duration = projects.setdefault(project, datetime.timedelta())
                projects[project] = duration + dur
            total = sum(projects.values(), datetime.timedelta())
            total_seconds = (total.days * 24 * 60 * 60) + total.seconds
            for project, duration in sorted(
                    projects.items(), key=lambda x: x[1], reverse=True):
                if duration == datetime.timedelta():
                    continue
                duration_seconds = float(duration.days * 24 * 60 * 60 +
                                         duration.seconds)
                self.w(format_duration(duration), 'duration')
                self.w('\t')
                self.w('%0.2i%%' % ((duration_seconds / total_seconds) * 100),
                       'time')
                self.w('\t%s\n' % project)
        elif self.view == 'grouped':
            work, slack, hold = self.timelog.window.grouped_entries()
            for start, entry, duration in work + slack:
                self.write_group(entry, duration)
            where = buffer.get_end_iter()
            where.backward_cursor_position()
            buffer.place_cursor(where)
        self.add_footer()
        self.scroll_to_end()
        self.lock = False

    def delete_footer(self):
        buffer = self.log_buffer
        buffer.delete(buffer.get_iter_at_mark(self.footer_mark),
                      buffer.get_end_iter())
        buffer.delete_mark(self.footer_mark)
        self.footer_mark = None

    def add_footer(self):
        buffer = self.log_buffer
        self.footer_mark = buffer.create_mark('footer', buffer.get_end_iter(),
                                              True)
        total_work, total_slacking, total_holidays = (
            self.timelog.window.totals())
        week_total_work, week_total_slacking, week_total_holidays = (
            self.weekly_window().totals())
        work_days_this_week = self.weekly_window().count_days()

        self.w('\n')
        self.w('Total work done: ')
        self.w(format_duration(total_work), 'duration')
        self.w(' (')
        self.w(format_duration(week_total_work), 'duration')
        self.w(' this week')
        if work_days_this_week:
            per_diem = week_total_work / work_days_this_week
            self.w(', ')
            self.w(format_duration(per_diem), 'duration')
            self.w(' per day')
        self.w(')\n')
        self.w('Total slacking: ')
        self.w(format_duration(total_slacking), 'duration')
        self.w(' (')
        self.w(format_duration(week_total_slacking), 'duration')
        self.w(' this week')
        if work_days_this_week:
            per_diem = week_total_slacking / work_days_this_week
            self.w(', ')
            self.w(format_duration(per_diem), 'duration')
            self.w(' per day')
        self.w(')\n')
        time_left = self.time_left_at_work(total_work)
        if time_left is not None:
            time_to_leave = datetime.datetime.now() + time_left
            if time_left < datetime.timedelta(0):
                time_left = datetime.timedelta(0)
            self.w('Time left at work: ')
            self.w(format_duration(time_left), 'duration')
            self.w(' (till ')
            self.w(time_to_leave.strftime('%H:%M'), 'time')
            self.w(')')

    def time_left_at_work(self, total_work):
        """Calculate time left to work."""
        last_time = self.timelog.window.last_time()
        if last_time is None:
            return None
        now = datetime.datetime.now()
        current_task = self.task_entry.get_text()
        current_task_time = now - last_time
        if '**' in current_task:
            total_time = total_work
        else:
            total_time = total_work + current_task_time
        return datetime.timedelta(hours=self.settings.hours) - total_time

    def write_item(self, item):
        buffer = self.log_buffer
        start, stop, duration, entry = item
        self.w(format_duration(duration), 'duration')
        period = '\t(%s-%s)\t' % (start.strftime('%H:%M'),
                                  stop.strftime('%H:%M'))
        self.w(period, 'time')
        tag = '**' in entry and 'slacking' or None
        self.w(entry + '\n', tag)
        where = buffer.get_end_iter()
        where.backward_cursor_position()
        buffer.place_cursor(where)

    def write_group(self, entry, duration):
        self.w(format_duration(duration), 'duration')
        tag = '**' in entry and 'slacking' or None
        self.w('\t' + entry + '\n', tag)

    def scroll_to_end(self):
        buffer = self.log_view.get_buffer()
        end_mark = buffer.create_mark('end', buffer.get_end_iter())
        self.log_view.scroll_to_mark(end_mark, 0)
        buffer.delete_mark(end_mark)

    def set_up_task_list(self):
        """Set up the task list pane."""
        self.task_store.clear()
        for group_name, group_items in self.tasks.groups:
            t = self.task_store.append(None, [group_name, group_name + ': '])
            for item in group_items:
                if group_name == self.tasks.other_title:
                    task = item
                else:
                    task = group_name + ': ' + item
                self.task_store.append(t, [item, task])

    def set_up_history(self):
        """Set up history."""
        self.history = self.timelog.history
        self.filtered_history = []
        self.history_pos = 0
        self.history_undo = ''
        if not self.have_completion:
            return

        rev_history = self.history[:]
        rev_history.reverse()
        history = []
        for entry in rev_history:
            if entry not in history:
                history.insert(0, entry)
        self.completion_source = set(history)
        self._update_completion_choices()

    def _update_completion_choices(self):
        total = set()
        for line in self.completion_source:
            if line.endswith(' **'):
                line = line.replace(' **', '**')
            total.add(line)
        self.completion_choices.clear()
        for entry in sorted(total):
            self.completion_choices.append([entry])

    def set_up_completion(self):
        """Set up autocompletion."""
        if not self.settings.enable_gtk_completion:
            self.have_completion = False
            return
        self.have_completion = hasattr(gtk, 'EntryCompletion')
        if not self.have_completion:
            return
        self.completion_choices = gtk.ListStore(str)
        completion = gtk.EntryCompletion()
        completion.set_model(self.completion_choices)
        completion.set_text_column(0)

        def match_func(completion, key, iter):
            model = completion.get_model()
            text = model.get_value(iter, 0)
            text = text and text.lower() or ''
            for k in key.split():
                if k not in text:
                    break
            else:
                return True
            return False
        completion.set_match_func(match_func)
        self.task_entry.set_completion(completion)

    def add_history(self, entry):
        """Add an entry to history."""
        self.history.append(entry)
        self.history_pos = 0
        if not self.have_completion:
            return
        self.completion_source.add(entry)
        self._update_completion_choices()

    def delete_event(self, widget, data=None):
        """Try to close the window."""
        gtk.main_quit()
        return False

    def close_about_dialog(self, widget):
        """Ok clicked in the about dialog."""
        self.about_dialog.hide()

    def on_show_activate(self, widget):
        """Tray icon menu -> Show selected"""
        self.main_window.present()

    def on_hide_activate(self, widget):
        """Tray icon menu -> Hide selected"""
        self.main_window.hide()

    def on_quit_activate(self, widget):
        """File -> Quit selected"""
        gtk.main_quit()

    def on_about_activate(self, widget):
        """Help -> About selected"""
        self.about_dialog.show()

    def on_chronological_activate(self, widget):
        self.view = 'chronological'
        self.populate_log()

    def on_grouped_activate(self, widget):
        self.view = 'grouped'
        self.populate_log()

    def on_weekly_activate(self, widget):
        self.view = 'weekly'
        self.populate_log()

    def on_daily_report_activate(self, widget):
        """File -> Daily Report"""
        window = self.timelog.window
        self.mail(window.daily_report)

    def on_previous_day_report_activate(self, widget):
        """File -> Daily Report for Yesterday"""
        day = self.choose_date()
        if day:
            min = datetime.datetime.combine(
                day, self.timelog.virtual_midnight)
            max = min + datetime.timedelta(1)
            window = self.timelog.window_for(min, max)
            self.mail(window.daily_report)

    def on_workprogress_activate(self, widget):
        self.workprogressbar.toggle_visibility()

    def choose_date(self):
        """Pop up a calendar dialog.

        Returns either a datetime.date, or one.
        """
        if self.calendar_dialog.run() == gtk.RESPONSE_OK:
            y, m1, d = self.calendar.get_date()
            day = datetime.date(y, m1 + 1, d)
        else:
            day = None
        self.calendar_dialog.hide()
        return day

    def on_calendar_day_selected_double_click(self, widget):
        """Double-click on a calendar day: close the dialog."""
        self.calendar_dialog.response(gtk.RESPONSE_OK)

    def weekly_window(self, day=None):
        return self.timelog.weekly_window(day)

    def on_weekly_report_activate(self, widget):
        """File -> Weekly Report"""
        window = self.weekly_window()
        self.mail(window.weekly_report)

    def on_previous_week_report_activate(self, widget):
        """File -> Weekly Report for Last Week"""
        day = self.choose_date()
        if day:
            window = self.weekly_window(day=day)
            self.mail(window.weekly_report)

    def on_fill_collmex_activate(self, widget):
        day = self.choose_date()
        if not day:
            return
        window = self.weekly_window(day=day)
        try:
            collmex = gocept.gtimelog.collmex.Collmex(self.settings)
            collmex.report(window.all_entries())
        except Exception, err:
            log.error('Error filling collmex', exc_info=True)
            message = "Collmex: %s" % err
        else:
            message = "Collmex: success "
        self.statusbar.post_message(message)

    def on_fill_bugtrackers_activate(self, widget):
        day = self.choose_date()
        if not day:
            return
        window = self.weekly_window(day=day)
        try:
            trackers = gocept.gtimelog.bugtracker.Bugtrackers(self.settings)
            trackers.update(window)
            message = "Bugtrackers: success"
        except Exception, err:
            log.error('Error filling Bugtrackers', exc_info=True)
            message = "Bugtrackers: %s" % err
        self.statusbar.post_message(message)

    def on_edit_timelog_activate(self, widget):
        """File -> Edit timelog.txt"""
        self.spawn(self.settings.editor, '"%s"' % self.timelog.filename)

    def on_edit_tasks_activate(self, widget):
        """File -> Edit timelog.txt"""
        self.spawn(self.settings.editor, '"%s"' % self.tasks.filename)

    def mail(self, write_draft):
        """Send an email."""
        draftfn = tempfile.mktemp(suffix='gtimelog')  # XXX unsafe!
        draft = open(draftfn, 'w')
        write_draft(draft, self.settings.email, self.settings.name)
        draft.close()
        self.spawn(self.settings.mailer, draftfn)
        # XXX rm draftfn when done -- but how?

    def spawn(self, command, arg=None):
        """Spawn a process in background"""
        if arg is not None:
            if '%s' in command:
                command = command % arg
            else:
                command += ' ' + arg
        os.system(command + " &")

    def on_reread_activate(self, widget):
        """File -> Reread"""
        self.timelog.reread()
        self.reread()

    def reread(self):
        self.set_up_history()
        self.populate_log()
        self.tick(True)

    def on_deletelast_activate(self, widget):
        """File -> Delete last Entry"""
        last = self.timelog.pop()
        self.reread()
        self.task_entry.set_text(last[1])
        self.task_entry.set_position(-1)

    def task_list_row_activated(self, treeview, path, view_column):
        """A task was selected in the task pane -- put it to the entry."""
        model = treeview.get_model()
        task = model[path][1]
        self.task_entry.set_text(task)
        self.task_entry.grab_focus()
        self.task_entry.set_position(-1)
        # XXX: how does this integrate with history?

    def task_list_button_press(self, menu, event):
        if event.button == 3:
            menu.popup(None, None, None, event.button, event.time)
            return True
        else:
            return False

    def on_task_list_reload(self, event):
        self.tasks.reload()
        self.set_up_task_list()

    def on_task_list_edit(self, event):
        self.spawn(self.settings.edit_task_list_cmd)

    def task_list_loading(self):
        self.task_list_loading_failed = False
        self.statusbar.post_message("Loading...")
        # let the ui update become visible
        # while gtk.events_pending():
        #     gtk.main_iteration()

    def task_list_error(self):
        self.task_list_loading_failed = True
        self.statusbar.post_message("Could not get task list.")

    def task_list_loaded(self):
        if not self.task_list_loading_failed:
            self.statusbar.post_message("Task list successfully loaded.")

    def task_entry_changed(self, widget):
        """Reset history position when the task entry is changed."""
        self.history_pos = 0

    def task_entry_key_press(self, widget, event):
        """Handle key presses in task entry."""
        if event.keyval == gtk.gdk.keyval_from_name('Prior'):
            self._do_history(1)
            return True
        if event.keyval == gtk.gdk.keyval_from_name('Next'):
            self._do_history(-1)
            return True
        # XXX This interferes with the completion box.  How do I determine
        # whether the completion box is visible or not?
        if self.have_completion:
            return False
        if event.keyval == gtk.gdk.keyval_from_name('Up'):
            self._do_history(1)
            return True
        if event.keyval == gtk.gdk.keyval_from_name('Down'):
            self._do_history(-1)
            return True
        return False

    def _do_history(self, delta):
        """Handle movement in history."""
        if not self.history:
            return
        if self.history_pos == 0:
            self.history_undo = self.task_entry.get_text()
            self.filtered_history = uniq([l for l in self.history
                                          if l.startswith(self.history_undo)])
        history = self.filtered_history
        new_pos = max(0, min(self.history_pos + delta, len(history)))
        if new_pos == 0:
            self.task_entry.set_text(self.history_undo)
            self.task_entry.set_position(-1)
        else:
            self.task_entry.set_text(history[-new_pos])
            self.task_entry.select_region(0, -1)
        # Do this after task_entry_changed reset history_pos to 0
        self.history_pos = new_pos

    def add_entry(self, widget, data=None):
        """Add the task entry to the log."""
        entry = self.task_entry.get_text()
        if not entry:
            return
        self.add_history(entry)
        self.timelog.append(entry)
        if self.view == 'chronological':
            self.delete_footer()
            self.write_item(self.timelog.window.last_entry())
            self.add_footer()
            self.scroll_to_end()
        else:
            self.populate_log()
        self.task_entry.set_text("")
        self.task_entry.grab_focus()
        self.tick(True)
        for watcher in self.entry_watchers:
            watcher(entry)

    def tick(self, force_update=False):
        """Tick every second."""
        if self.tasks.check_reload():
            self.set_up_task_list()
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        if now == self.last_tick and not force_update:
            # Do not eat CPU unnecessarily
            return True
        self.last_tick = now
        last_time = self.timelog.window.last_time()
        if last_time is None:
            self.time_label.set_text(now.strftime("%H:%M"))
        else:
            self.time_label.set_text(format_duration(now - last_time))
            # Update "time left to work"
            if not self.lock:
                self.workprogressbar.update()
                self.delete_footer()
                self.add_footer()
        return True


def main(argv=None):
    """Run the program."""
    if argv is None:
        argv = sys.argv
    configdir = os.path.expanduser('~/.gtimelog')
    try:
        os.makedirs(configdir)  # create it if it doesn't exist
    except OSError:
        pass
    settings = gocept.gtimelog.core.Settings()
    settings_file = os.path.join(configdir, 'gtimelogrc')
    if not os.path.exists(settings_file):
        settings.save(settings_file)
    else:
        settings.load(settings_file)
    timelog = gocept.gtimelog.core.TimeLog(
        os.path.join(configdir, 'timelog.txt'), settings)
    if settings.collmex_customer_id:
        tasks = gocept.gtimelog.collmex.TaskList(
            os.path.join(configdir, 'tasks-collmex.txt'), settings)
    else:
        tasks = gocept.gtimelog.core.TaskList(
            os.path.join(configdir, 'tasks.txt'))
    main_window = MainWindow(timelog, settings, tasks)

    # Start logging
    log_handler = LogWindowHandler(main_window)
    logging.root.addHandler(log_handler)
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s'))
    logging.root.addHandler(stdout)
    logging.root.setLevel(settings.log_level)
    log.debug('Logging is set to level %s' % settings.log_level)

    # start gtimelog hidden to tray
    if "--start-hidden" in argv:
        main_window.on_hide_activate("")
    TrayIcon(main_window)
    try:
        gtk.main()
    except KeyboardInterrupt:
        pass
