#!/usr/bin/env python

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#                                                                             #
# LiveClone will create a LiveCD or a LiveUSB key out of a Live CD            #
# or out of a running environment.                                            #
#                                                                             #
# Copyright Pierrick Le Brun <akuna at free.fr>.                              #
#                                                                             #
# This program is free software; you can redistribute it and/or               #
# modify it under the terms of the GNU General Public License                 #
# as published by the Free Software Foundation; either version 2              #
# of the License, or (at your option) any later version.                      #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program; if not, write to the Free Software                 #
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. #
#                                                                             #
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# version='0.5'# -  Adapted LiveClone '0.4.5' to Salix environment.
#                   Modified logo
#                   Migrated from libglade to gtkbuilder
#                   Improved contextual Help

import os
import shutil
import subprocess
import commands
import time
import gtk
import gtk.glade
import gobject

# Internationalization
import locale
import gettext
locale.setlocale(locale.LC_ALL, "")
gettext.bindtextdomain("liveclone", "/usr/share/locale")
gettext.textdomain("liveclone")
gettext.install("liveclone", "/usr/share/locale", unicode=1)
gtk.glade.bindtextdomain("liveclone", "/usr/share/locale")
gtk.glade.textdomain("liveclone")

class LiveClone:
    """
    Main application class.
    """
    def __init__(self):
        """
        Initializes the application.
        """
        builder = gtk.Builder()
        if os.path.exists("liveclone.glade") :
            builder.add_from_file("liveclone.glade")
        elif os.path.exists("/usr/share/liveclone/liveclone.glade") :
            builder.add_from_file("/usr/share/liveclone/liveclone.glade")
        elif os.path.exists("../share/liveclone/liveclone.glade") :
            builder.add_from_file("../share/liveclone/liveclone.glade")

        # Get a handle on the glade file widgets we want to interact with
        self.window = builder.get_object("liveclone_main")
        self.help_dialog = builder.get_object("help_dialog")
        self.about_dialog = builder.get_object("about_dialog")
        self.about_dialog.set_transient_for(self.window)
        self.progress_dialog = builder.get_object("progress_dialog")
        self.progress_bar = builder.get_object("progressbar1")
        self.cdworkdir_chooser = builder.get_object("cdworkdir")
        self.cdrom_apply_button = builder.get_object("cdrom_apply_button")
        self.livecd_label = builder.get_object("cdrom_label")
        self.usbworkdir_chooser = builder.get_object("usbworkdir")
        self.usb_apply_button = builder.get_object("usb_apply_button")
        self.liveusb_label = builder.get_object("usb_label")
        self.unmodified_check = builder.get_object("unmodified_check")
        self.running_environment_check = builder.get_object("running_environment_check")
        self.use_persistence = builder.get_object("check_persistence")
        self.persistence_size_label = builder.get_object("size_label")
        self.persistence_size = builder.get_object("persist_size")

        # Connect signals
        builder.connect_signals(self)

        def initialize_checkboxes():
            """
            Ungreys the USB unmodified checkbox if we are in a LiveCD environment
            """
            if os.path.exists("/mnt/live/memory/changes") is True :
                self.unmodified_check.set_sensitive(True)
            else :
                pass


        initialize_checkboxes()

        def common_base(self, *args):
                """
                Common to either a LiveCD or LiveUSB
                """
                self.window.hide()
                self.progress_dialog.show()
                self.progress_bar.set_text(_("LiveClone in progress..."))
                self.progress_bar.set_fraction(0.03)
                # there's more work, return True
                yield True

                # First we prepare the working directory & we populate the LiveCD skeleton
                os.makedirs(live_workdir + "/salixlive/base")
                os.makedirs(live_workdir + "/salixlive/modules")
                os.makedirs(live_workdir + "/salixlive/optional")
                os.makedirs(live_workdir + "/salixlive/rootcopy")
                shutil.copy("/usr/share/liveclone/liveskel/salixlive/livecd.sgn", live_workdir + "/salixlive/")
                shutil.copy("/usr/share/liveclone/liveskel/salixlive/make_iso.sh", live_workdir + "/salixlive/")

                self.progress_bar.set_text(_("LiveClone in progress..."))
                self.progress_bar.set_fraction(0.06)
                # there's more work, return True
                yield True

                # Let's check if we are in a Live environment or not
                if os.path.exists("/mnt/live/memory/changes") is True :
                    # we are in a LiveCD environment
                    os.chmod("/etc/rc.d/rc.live", 0744)
                    shutil.copytree("/boot", live_workdir + "/boot", symlinks=False)
                else :
                    # we are not in a LiveCD environment
                    # first we need to fetch the needed modified files to use for the live device we are creating
                    shutil.copytree("/usr/share/salixlive/moded/etc", live_workdir + "/salixlive/rootcopy/etc", symlinks=False)
                    # then rc.live will have to be blacklisted from the service list
                    pass
                    # finally we need to add the live boot files (kernel + initrd)
                    pass

                self.progress_bar.set_text("LiveClone in progress...")
                # there's more work, return True
                yield True

                # Better clear /var/packages
                subprocess.call("rm -rf /var/packages/*", shell=True)

                # In case the user wants to use SalixLive unmodified:
                if self.unmodified_check.get_active() == 1 :
                        # Creating the persistent file
                        if self.use_persistence.get_active() == 1 :
                                self.progress_bar.set_text(_("Creating persistent file..."))
                                self.progress_bar.set_fraction(0.09)
                                # there's more work, return True
                                yield True
                                subprocess.call("dd if=/dev/zero of=" + live_workdir + "/slxsave.xfs bs=1M count=" + slxsave_size, shell=True)
                                subprocess.call("/sbin/mkfs.xfs " + live_workdir + "/slxsave.xfs", shell=True)
                        self.progress_bar.set_text(_("Creating Module..."))
                        self.progress_bar.set_fraction(0.3)
                        # there's more work, return True
                        yield True
                        subprocess.call("cp /mnt/live/mnt/*/salixlive/base/* " + live_workdir + "/salixlive/base/", shell=True)

                else :
                        self.progress_bar.set_text(_("Creating Module..."))
                        self.progress_bar.set_fraction(0.8)
                        # there's more work, return True

                        # Else we build LiveClone main module out of the running environment
                        os.makedirs(live_workdir + "/salixlive/rootcopy/media")
                        subprocess.call("mksquashfs /bin /etc /home /lib /root /sbin /usr /var " + live_workdir + "/salixlive/base/01-clone.lzm -keep-as-directory -b 256K -lzmadic 256K", shell=True)
                        os.chmod(live_workdir + "/salixlive/base/01-clone.lzm", 0444)

                self.progress_bar.set_text(_("Module created..."))
                self.progress_bar.set_fraction(0.8)

                # there's more work, return True
                yield True

                if "/liveclone" in live_workdir :
                        self.progress_bar.set_text(_("Building the iso file..."))
                        self.progress_bar.set_fraction(0.9)
                        subprocess.call(live_workdir + "/salixlive/make_iso.sh " + live_workdir + "/" + liveclone_name + ".iso", shell=True)

                # there's more work, return True
                yield True

                self.progress_bar.set_text(_("Live device succesfully created..."))
                self.progress_bar.set_fraction(1.0)
                subprocess.call("sync", shell=True)
                time.sleep(3)

                # there's more work, return True
                yield True

                time.sleep(3)
                self.progress_dialog.hide()
                info_dialog(_("Your Live CD-ROM or USB key has been successfully created and is ready! You can now exit LiveClone program."))
                self.window.show()

                # no more work, return False
                yield False


### Callback signals waiting in a constant loop: ###

### WINDOWS MAIN SIGNALS ###

    # What to do when the exit X on the main window upper right is clicked
    def gtk_main_quit(self, widget, data=None):
        gtk.main_quit()

    # What to do when the quit button is clicked
    def on_main_window_destroy(self, widget, data=None):
        gtk.main_quit()

    # What to do when the about button is clicked
    def on_about_button_clicked(self, widget, data=None):
        self.about_dialog.show()

    # What to do when the about quit button is clicked
    def on_about_dialog_close(self, widget, data=None):
        self.about_dialog.hide()
        return True

    def on_cdrom_apply_button_clicked(self, *args):
        """
        Called by the CD-ROM Execute button, generates the CD-ROM LiveClone
        """
        global live_workdir
        live_workdir = self.cdworkdir_chooser.get_filename() + "/liveclone"
        global liveclone_name
        liveclone_name = self.livecd_label.get_text()
        # Let's make sure that the working directory is not in the /home directory
        if "/home/" in live_workdir :
            error_dialog(_("Sorry, you must choose another work directory!\n \nSince your Home directory will be included in your LiveClone, your work directory should obviously not be located inside of it.\n \nThe ideal is to choose or create a subdirectory either from another partition or from an external hard drive!"))
        else :
            shutil.rmtree(live_workdir, ignore_errors=True)
            # Better deactivate all Execute buttons
            self.usb_apply_button.set_sensitive(False)
            self.cdrom_apply_button.set_sensitive(False)
            task = self.common_base()
            gobject.idle_add(task.next)

    def on_usb_apply_button_clicked(self, *args):
        """
        Called by the USB Execute button, generates the USB LiveClone
        """
        global live_workdir
        live_workdir = self.usbworkdir_chooser.get_filename()
        global liveclone_name
        liveclone_name = self.liveusb_label.get_text()
        global slxsave_size
        slxsave_size = self.persistence_size.get_text()
        # Let's make sure this is really an external usb disk
        if "/media/" in live_workdir :
            warning_dialog(_("All the data present on your USB key will be permanently erased!\n \nAre you sure you want to continue?"))
            if result_warning == gtk.RESPONSE_YES:
                usb_device_cli = 'mount | grep ' + live_workdir + ' | cut -f1 -d " "'
                usb_device = commands.getoutput(usb_device_cli)
                subprocess.call("umount " + usb_device, shell=True)
                subprocess.call("mkdosfs -F 16 -n " + liveclone_name + " " + usb_device, shell=True)
                subprocess.call("syslinux -f " + usb_device, shell=True)
                subprocess.call("rm -rf " + live_workdir, shell=True)
                live_workdir = "/media/" + liveclone_name
                subprocess.call("mkdir " + live_workdir, shell=True)
                subprocess.call("mount " + usb_device + " " + live_workdir, shell=True)

                # Better deactivate all Execute buttons
                self.usb_apply_button.set_sensitive(False)
                self.cdrom_apply_button.set_sensitive(False)

                task = self.common_base()
                gobject.idle_add(task.next)

            if result_warning == gtk.RESPONSE_NO:
                    pass
        else :
            error_dialog(_("Sorry, you may have selected an invalid USB key path!\n \nUsually a valid path to a USB key starts with /media.\n \nPlease, try again."))

    def on_running_environment_check_toggled(self, *args):
        """
        Called when USB 'running environment' checkbox is toggled
        """
        if self.running_environment_check.get_active() == 1 :
            self.unmodified_check.set_active(False)
        if self.running_environment_check.get_active() == 0 :
            if os.path.exists("/mnt/live/memory/changes") is True :
                self.unmodified_check.set_active(True)
            else:
                self.unmodified_check.set_active(False)

    def on_unmodified_check_toggled(self, *args):
        """
        Called when USB 'unmodified zenwalk live' checkbox is toggled
        """
        if self.unmodified_check.get_active() == 1 :
            self.running_environment_check.set_active(False)
        if self.unmodified_check.get_active() == 0 :
            self.running_environment_check.set_active(True)

    def on_check_persistence_toggled(self, *args):
        """
        Called when USB 'use persistence' checkbox is toggled
        """
        if self.use_persistence.get_active() == 1 :
            self.persistence_size.set_sensitive(True)
            self.persistence_size_label.set_sensitive(True)

        if self.use_persistence.get_active() == 0 :
            self.persistence_size.set_sensitive(False)
            self.persistence_size_label.set_sensitive(False)

# Info window skeleton:
def info_dialog(message, parent = None):
    """
    Display an information message.

    """
    dialog = gtk.MessageDialog(parent = parent, type = gtk.MESSAGE_INFO, buttons = gtk.BUTTONS_OK, flags = gtk.DIALOG_MODAL)
    dialog.set_markup(message)
    global result_info
    result_info = dialog.run()
    dialog.destroy()

# Warning window skeleton:
def warning_dialog(message, parent = None):
    """
    Display a warning message.

    """
    dialog = gtk.MessageDialog(parent = parent, type = gtk.MESSAGE_WARNING, buttons = gtk.BUTTONS_NONE, flags = gtk.DIALOG_MODAL)
    dialog.add_buttons(gtk.STOCK_YES, gtk.RESPONSE_YES)
    dialog.add_buttons(gtk.STOCK_NO, gtk.RESPONSE_NO)
    dialog.set_default_response(gtk.RESPONSE_NO)
    dialog.set_markup(message)
    global result_warning
    result_warning = dialog.run()
    dialog.destroy()

# Error window skeleton:
def error_dialog(message, parent = None):
    """
    Displays an error message.
    """
    dialog = gtk.MessageDialog(parent = parent, type = gtk.MESSAGE_ERROR, buttons = gtk.BUTTONS_CLOSE, flags = gtk.DIALOG_MODAL)
    dialog.set_markup(message)
    dialog.set_icon_from_file("/usr/share/icons/gnome-colors-common/scalable/actions/gtk-stop.svg")
    global result_error
    result_error = dialog.run()
    dialog.destroy()

# Launch the application
if __name__ == '__main__':
    # If no root privilege, displays error message & exit
    if os.getuid() != 0:
        error_dialog(_("<b>Sorry!</b> \n\nRoot privileges are required to run this program. "))
        sys.exit(1)
    # If root privilege, show the gui & wait for signals
    LiveClone()
    gtk.main()