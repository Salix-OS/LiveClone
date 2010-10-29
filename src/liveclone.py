#!/usr/bin/env python

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
#                                                                             #
# LiveClone will create a LiveCD or a LiveUSB key out of a Live CD            #
# or out of a running environment.                                            #
#                                                                             #
# Copyright Pierrick Le Brun <akuna~at~salixos~dot~org>.                      #
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

# version = '0.10.13.1.1'

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
        self.cdworkdir_chooser.set_current_folder('/mnt')
        self.cdrom_apply_button = builder.get_object("cdrom_apply_button")
        self.livecd_label = builder.get_object("cdrom_label")
        self.usbworkdir_chooser = builder.get_object("usbworkdir")
        self.usbworkdir_chooser.set_current_folder('/media')
        self.usb_apply_button = builder.get_object("usb_apply_button")
        self.liveusb_label = builder.get_object("usb_label")
        self.unmodified_radiobutton = builder.get_object("unmodified_radiobutton")
        self.running_environment_radiobutton = builder.get_object("running_environment_radiobutton")
        self.use_persistence = builder.get_object("check_persistence")
        self.persistence_size_label = builder.get_object("size_label")
        self.persistence_size = builder.get_object("persist_size")
        self.context_help_label = builder.get_object("context_help_label")
        self.GrubRadioButton = builder.get_object("grub_radiobutton")
        self.SyslinuxRadioButton = builder.get_object("syslinux_radiobutton")
        self.CdGrubRadioButton = builder.get_object("cd_grub_radiobutton")
        self.IsolinuxRadioButton = builder.get_object("isolinux_radiobutton")

        # Connect signals
        builder.connect_signals(self)

        # Initialize diverse variables
        global live_environment
        live_environment = False
        global cdrom_tray
        cdrom_tray = False
        global usb_key
        usb_key = False
        # Initialize the contextual help box
        global context_intro
        context_intro = _("LiveClone will generate a Live CD/DVD iso image or a Live USB key, based on \
SalixLive or on your running environment, with or without persistent changes.")
        self.context_help_label.set_markup(context_intro)

        def initialize_checkboxes():
            """
            Ungreys the USB unmodified checkbox if we are in a LiveCD environment
            """
            if os.path.exists("/mnt/live/memory/changes") is True :
                self.unmodified_radiobutton.set_sensitive(True)
            else :
                pass

        initialize_checkboxes()
        self.persistence_size.set_value(256)
        self.persistence_size.set_sensitive(False)
### Callback signals waiting in a constant loop: ###

### WINDOWS MAIN SIGNALS ###

    # Contextual help:
    def on_about_button_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_text(_("About LiveClone."))
    def on_about_button_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_cd_tab_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_markup(_("Click on this tab if you want to \
create a Live CD/DVD iso image based on your running environment.\n\
You should therefore ensure that you have already added and/or removed any \
programs and/or any users, as well as performed any other system or aesthetic \
modifications which you want to be included in your customized Live CD/DVD.\n\
What you *<i>see</i>* in your running session is what you will get in your Live CD/DVD."))
    def on_cd_tab_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_usb_tab_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_text(_("Click on this tab if you want to create a Live USB \
based on SalixLive or on your running environment."))
    def on_usb_tab_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_cdrom_label_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_text(_("Please enter the name of your Live CD/DVD."))
    def on_cdrom_label_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_usb_label_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_text(_("Please enter the name of your Live USB."))
    def on_usb_label_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_choose_cdworkdir_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_text(_("This is the work directory where your Live CD/DVD \
iso image will be created & where you will be able to retrieve it to burn it unto a CD/DVD-ROM.\n\
The free space available should be more than twice the size of your future Live CD/DVD.\n\
It should be located on a separate partition, an external hardrive or a USB key \
but never -ever- in your home directory!"))
    def on_choose_cdworkdir_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_choose_usbdir_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_text(_("This is the path to your USB key. \
Please note that all present data it may contain will be permanently erased. "))
    def on_choose_usbdir_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_unmodified_radiobutton_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_markup(_("Check this option if you want to clone \
the <b>unmodified</b> SalixLive CD-ROM to a Live USB key (this option is only available if \
LiveClone is executed from a LiveCD)."))
    def on_unmodified_radiobutton_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_syslinux_radiobutton_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_markup(_("Choose this option if you want to use \
<b>Syslinux</b> as your boot manager."))
    def on_syslinux_radiobutton_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_grub_radiobutton_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_markup(_("Choose this option if you want to use \
<b>GRUB</b> as your boot manager."))
    def on_grub_radiobutton_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_isolinux_radiobutton_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_markup(_("Choose this option if you want to use \
<b>Isolinux</b> as your boot manager."))
    def on_isolinux_radiobutton_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_cd_grub_radiobutton_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_markup(_("Choose this option if you want to use \
<b>GRUB</b> as your boot manager."))
    def on_cd_grub_radiobutton_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_check_persistence_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_text(_("Check this option if you want your Live USB key to be \
able to record all changes & data from live sessions (same behaviour as an installed standard system)."))
    def on_check_persistence_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_running_environment_radiobutton_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_markup(_("Check this option if you want to clone your \
running personnalized environment to a Live USB key. \n\
You should therefore ensure that you have already added and/or removed any programs and/or \
any users, as well as performed any other system or aesthetic modifications \
which you want to be included in your customized Live USB key.\n\
What you *<i>see</i>* in your running session is what you will get in your Live USB key."))
    def on_running_environment_radiobutton_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_size_label_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_text(_("Set the size of your persistence file (It should \
be small enough to fit in your USB key while being large enough to fit as much data as possible)"))
    def on_size_label_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_apply_button_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_text(_("Click on this button once all your \
settings have been defined.\nYou will then need some patience as the creation of a customized live media \
can be quite long depending on the power of your computer.\nAt the end of the process, \
an information dialog will let you know if LiveClone succeeded or failed to create your customized live media."))
    def on_apply_button_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)
    def on_quit_button_enter_notify_event(self, widget, data=None):
        self.context_help_label.set_text(_("Exit LiveClone."))
    def on_quit_button_leave_notify_event(self, widget, data=None):
        global context_intro
        self.context_help_label.set_text(context_intro)

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
        global iso_dir
        iso_dir = self.cdworkdir_chooser.get_filename()
        global live_workdir
        live_workdir = iso_dir + "/liveclone"
        global liveclone_name
        liveclone_name = self.livecd_label.get_text()
        # Ensure that the working directory is not in the /home directory
        if live_workdir.startswith("/home/") == True :
            error_dialog(_("Sorry, you must not use a location that is a part of \
the live environment ! \n\nPlease select or create a subdirectory located on a \
physical hard drive (hint: access path usually starts with /mnt or /media)."))
        else :
            # this step will be removed once support for non-live environment is added
            self.check_environment()
            global live_environment
            if live_environment == True :
                global cdrom_tray
                cdrom_tray = True
                # Clean up eventual old work directories
                shutil.rmtree(live_workdir, ignore_errors=True)
                subprocess.call("mkdir -p " + live_workdir, shell=True)
                # LiveCD clone always use the running environment & never create persistent files
                self.use_persistence.set_active(False)
                self.running_environment_radiobutton.set_active(True)
                # Better deactivate the following USB options as well
                self.GrubRadioButton.set_active(False)
                self.SyslinuxRadioButton.set_active(False)
                # Better deactivate all Execute buttons
                self.usb_apply_button.set_sensitive(False)
                self.cdrom_apply_button.set_sensitive(False)
                if self.IsolinuxRadioButton.get_active() == True :
                    shutil.rmtree("/tmp/boot", ignore_errors=True)
                    shutil.copytree("/usr/share/liveclone/liveskel/boot", "/tmp/boot", symlinks=False)
                    warning_dialog(_("Would you like to personnalize Isolinux boot menu?"))
                    if result_warning == gtk.RESPONSE_YES:
                        # Open the isolinux conf file
                        if os.path.isfile("/usr/bin/geany") :
                            subprocess.call('/usr/bin/geany /tmp/boot/isolinux/isolinux.cfg 2>/dev/null', shell=True)
                        elif os.path.isfile("/usr/bin/leafpad") :
                            subprocess.call('/usr/bin/leafpad /tmp/boot/isolinux/isolinux.cfg 2>/dev/null', shell=True)
                        elif os.path.isfile("/usr/bin/gedit") :
                            subprocess.call('/usr/bin/gedit /tmp/boot/isolinux/isolinux.cfg 2>/dev/null', shell=True)
                        elif os.path.isfile("/usr/bin/kwrite") :
                            subprocess.call('/usr/bin/kwrite /tmp/boot/isolinux/isolinux.cfg 2>/dev/null', shell=True)
                        elif os.path.isfile("/usr/bin/mousepad") :
                            subprocess.call('/usr/bin/mousepad /tmp/boot/isolinux/isolinux.cfg 2>/dev/null', shell=True)
                        else :
                            subprocess.call('xdg-open /tmp/boot/isolinux/isolinux.cfg 2>/dev/null', shell=True)
                    # Ensure changes are taken into account
                    subprocess.call('sync', shell=True)
                    subprocess.call('rm -f /tmp/boot/isolinux/isolinux.cfg~ 2>/dev/null', shell=True)
                    # TODO convert isolinux.cfg file to appropriate ISO code...
                task = self.common_base()
                gobject.idle_add(task.next)

    def on_usb_apply_button_clicked(self, *args):
        """
        Called by the USB Execute button, generates the USB LiveClone
        """
        # Better deactivate those CD-ROM options
        self.CdGrubRadioButton.set_active(False)
        self.IsolinuxRadioButton.set_active(False)
        global live_workdir
        live_workdir = self.usbworkdir_chooser.get_filename()
        global liveclone_name
        liveclone_name = self.liveusb_label.get_text()
        global slxsave_size
        slxsave_size = self.persistence_size.get_text()

        # this step will be removed once support for non-live environment is added
        self.check_environment()
        global live_environment
        if live_environment == True :
            # Let's make sure this is really an external usb disk
            if "/media/" in live_workdir : # Quick & dirty, needs something better as some (rare) folks might use /media to mount non removable media
                global usb_key
                usb_key = True
                warning_dialog(_("All the data present on your USB key will be permanently erased!\n \nAre you sure you want to continue?"))
                if result_warning == gtk.RESPONSE_YES:

                    usb_device_cli = 'mount | grep ' + live_workdir + ' | cut -f1 -d " "'
                    global usb_device
                    usb_device = commands.getoutput(usb_device_cli)
                    subprocess.call("umount " + live_workdir, shell=True)
                    # Format the partition
                    subprocess.call("mkdosfs -F 32 -n " + liveclone_name + " " + usb_device, shell=True)
                    global usb_dev_root
                    global usb_dev_part
                    if usb_device[-2:].isdigit() is True : # Highly unprobable but we never know...
                        usb_dev_root = usb_device[:-2]
                        usb_dev_part = usb_device[-2:]
                    elif usb_device[-1:].isdigit() is True :
                        usb_dev_root = usb_device[:-1]
                        usb_dev_part = usb_device[-1:]
                    # Ensure it has a boot flag
                    boot_flag_part = commands.getoutput("parted " + usb_dev_root + " unit s print | grep boot | awk '{print $1}'")
                    if boot_flag_part.isdigit() is False :
                        subprocess.call("parted " + usb_dev_root + " set " + usb_dev_part + " boot on", shell=True)
                    live_workdir = "/media/" + liveclone_name
                    subprocess.call("mkdir -p " + live_workdir, shell=True)
                    subprocess.call("mount " + usb_device + " " + live_workdir, shell=True)
                    os.chmod("/etc/rc.d/rc.live", 0744)

                    if self.SyslinuxRadioButton.get_active() == True :
                        shutil.rmtree("/tmp/boot", ignore_errors=True)
                        shutil.copytree("/usr/share/liveclone/liveskel/boot", "/tmp/boot", symlinks=False)
                        warning_dialog(_("Would you like to personnalize Syslinux boot menu?"))
                        if result_warning == gtk.RESPONSE_YES:
                            # Open the syslinux conf file
                            if os.path.isfile("/usr/bin/geany") :
                                subprocess.call('/usr/bin/geany /tmp/boot/syslinux/syslinux.cfg 2>/dev/null', shell=True)
                            elif os.path.isfile("/usr/bin/leafpad") :
                                subprocess.call('/usr/bin/leafpad /tmp/boot/syslinux/syslinux.cfg 2>/dev/null', shell=True)
                            elif os.path.isfile("/usr/bin/gedit") :
                                subprocess.call('/usr/bin/gedit /tmp/boot/syslinux/syslinux.cfg 2>/dev/null', shell=True)
                            elif os.path.isfile("/usr/bin/kwrite") :
                                subprocess.call('/usr/bin/kwrite /tmp/boot/syslinux/syslinux.cfg 2>/dev/null', shell=True)
                            elif os.path.isfile("/usr/bin/mousepad") :
                                subprocess.call('/usr/bin/mousepad /tmp/boot/syslinux/syslinux.cfg 2>/dev/null', shell=True)
                            else :
                                subprocess.call('xdg-open /tmp/boot/syslinux/syslinux.cfg 2>/dev/null', shell=True)
                        # Ensure changes are taken into account
                        subprocess.call('sync', shell=True)
                        subprocess.call('rm -f /tmp/boot/syslinux/syslinux.cfg~ 2>/dev/null', shell=True)
                        # TODO convert syslinux.cfg file to appropriate ISO code...

                    # Better deactivate all Execute buttons
                    self.usb_apply_button.set_sensitive(False)
                    self.cdrom_apply_button.set_sensitive(False)

                    task = self.common_base()
                    gobject.idle_add(task.next)

            else :
                error_dialog(_("Sorry, you may have selected an invalid USB key path!\n \nUsually a valid path to a USB key starts with /media.\n \nPlease, try again."))


    def check_environment(self, *args):
        """
        Check if we are in a Live environment or not
        """
        global live_environment
        if os.path.exists("/mnt/live/memory/changes") is False :
            # We are not in a LiveCD environment, ATM this option is not supported
            live_environment = False
            self.progress_dialog.hide()
            error_dialog(_("Sorry! At the moment, LiveClone can only be executed from SalixLive environment. \n\nSupport to run from a regular installed environment will be added in a future version of LiveClone."))
            self.window.show()
            # Reactivate all Execute buttons
            self.usb_apply_button.set_sensitive(True)
            self.cdrom_apply_button.set_sensitive(True)
        else :
            live_environment = True

    def common_base(self, *args):
        """
        Progress bar, common to either a LiveCD or LiveUSB
        """
        global live_workdir
        self.window.hide()
        self.progress_dialog.show()
        self.progress_bar.set_text(_("Customized live media creation in progress..."))
        self.progress_bar.set_fraction(0.05)
        time.sleep(3)
        # there's more work, return True
        yield True

        # First we prepare the working directory & we populate the LiveCD/USB skeleton
        try :
            shutil.copytree("/boot", live_workdir + "/boot", symlinks=False)
        except OSError :
            self.progress_dialog.hide()
            error_dialog(_("Sorry! Liveclone is not able to manage this \
directory or this partition, please choose another location for your work directory."))
            self.window.show()
            # Reactivate all Execute buttons
            self.usb_apply_button.set_sensitive(True)
            self.cdrom_apply_button.set_sensitive(True)
            # no more work, return False
            yield False

        os.makedirs(live_workdir + "/salixlive/base")
        os.makedirs(live_workdir + "/salixlive/modules")
        os.makedirs(live_workdir + "/salixlive/optional")
        os.makedirs(live_workdir + "/salixlive/rootcopy")
        os.makedirs(live_workdir + "/docs")
        shutil.copy("/usr/share/liveclone/liveskel/salixlive/livecd.sgn", live_workdir + "/salixlive/")
        shutil.copy("/usr/share/liveclone/liveskel/salixlive/make_iso.sh", live_workdir + "/salixlive/")
        subprocess.call("chmod +x " + live_workdir + "/salixlive/make_iso.sh", shell=True)
        subprocess.call("cp /mnt/live/mnt/*/docs/* " + live_workdir + "/docs/", shell=True)

        self.progress_bar.set_text(_("Customized live media creation in progress..."))
        self.progress_bar.set_fraction(0.1)
        # there's more work, return True
        yield True

        # Better clear packages
        subprocess.call("rm -rf /var/slapt-get/*", shell=True)

        # The user may want to create a persistent file on his USB key
        if self.use_persistence.get_active() == True :
            self.progress_bar.set_text(_("Creating persistent file..."))
            self.progress_bar.set_fraction(0.2)
            # there's more work, return True
            yield True
            subprocess.call("dd if=/dev/zero of=" + live_workdir + "/slxsave.xfs bs=1M count=" + slxsave_size, shell=True)
            subprocess.call("/sbin/mkfs.xfs -f " + live_workdir + "/slxsave.xfs", shell=True)

        # The user may want to use SalixLive unmodified:
        if self.unmodified_radiobutton.get_active() == True :
            self.progress_bar.set_text(_("Copying SalixLive Modules..."))
            self.progress_bar.set_fraction(0.5)
            # there's more work, return True
            yield True
            subprocess.call("cp /mnt/live/mnt/*/salixlive/base/* " + live_workdir + "/salixlive/base/", shell=True)
            subprocess.call("cp /mnt/live/mnt/*/salixlive/modules/* " + live_workdir + "/salixlive/modules/", shell=True)
            subprocess.call("cp /mnt/live/mnt/*/salixlive/optional/* " + live_workdir + "/salixlive/optional/", shell=True)
            subprocess.call("cp /mnt/live/mnt/*/salixlive/rootcopy/* " + live_workdir + "/salixlive/rootcopy/", shell=True)
            os.makedirs(live_workdir + "/packages")
            subprocess.call("cp -r /mnt/live/mnt/*/packages/* " + live_workdir + "/packages/", shell=True)
        # Else we build LiveClone main module out of the running environment
        else :
            self.progress_bar.set_text(_("Creating Custom Module..."))
            self.progress_bar.set_fraction(0.5)
            # there's more work, return True
            yield True
            os.makedirs(live_workdir + "/salixlive/rootcopy/media")
            subprocess.call("mksquashfs /bin /etc /home /lib /root /sbin /usr /var " + live_workdir + "/salixlive/base/01-clone.lzm -keep-as-directory -b 1M -comp lzma -wildcards -e '... *pid' '... wicd/*-settings.conf' ", shell=True)
            os.chmod(live_workdir + "/salixlive/base/01-clone.lzm", 0444)

        self.progress_bar.set_text(_("Module created..."))
        self.progress_bar.set_fraction(0.8)
        # there's more work, return True
        yield True

        if cdrom_tray is True :
            self.progress_bar.set_text(_("Building the iso file..."))
            self.progress_bar.set_fraction(0.9)
            # there's more work, return True
            yield True
            if self.IsolinuxRadioButton.get_active() == True :
                subprocess.call("cp -r /tmp/boot/isolinux " + live_workdir + "/boot/", shell=True)
                subprocess.call("cp /tmp/boot/vesamenu.c32 " + live_workdir + "/boot/", shell=True)
                shutil.rmtree("/tmp/boot", ignore_errors=True)
                subprocess.call(live_workdir + "/salixlive/make_iso.sh " + iso_dir + "/" + liveclone_name + ".iso", shell=True)
            if self.CdGrubRadioButton.get_active() == True :
                subprocess.call("cd " + live_workdir + "&& mkisofs -b boot/grub/i386-pc/eltorito.img -no-emul-boot -boot-load-size 4 -boot-info-table -o " + iso_dir + "/" + liveclone_name + ".iso -r -J .", shell=True)

            self.progress_bar.set_text(_("Iso file succesfully created..."))
            self.progress_bar.set_fraction(1.0)
            # there's more work, return True
            yield True
            subprocess.call("sync", shell=True)
            time.sleep(3)
### Add some basic check here
            info_dialog(_("Your Live CD image has been successfully created in the \
work directory you specified. You can now exit LiveClone and use Brasero or a similar \
program to burn the .iso file unto a CD-ROM."))

        # Clean up USB desktop icon and /media/xxx temp directory
        if usb_key is True :
            self.progress_bar.set_text(_("Setting the boot manager..."))
            self.progress_bar.set_fraction(0.9)
            # there's more work, return True
            yield True
            # Install Grub if applicable
            if self.GrubRadioButton.get_active() == True :
                # Ensure the post mbr gap is large enough for grub2
                post_mbr_gap = commands.getoutput("parted " + usb_dev_root + " unit s print | grep '^ 1' | awk '{print $2}'")
                # Enlarge it if necessary
                if int(post_mbr_gap[:-1]) < 63 :
                    end_sector = commands.getoutput("parted " + usb_dev_root + " unit s print | grep '^ 1' | awk '{print $3}'")
                    subprocess.call("parted " + usb_dev_root + " resize 1 63s " + end_sector, shell=True)
                # Install Grub2
                subprocess.call("dd if=/boot/grub_mbr of=" + usb_dev_root + " count=440 bs=1 conv=notrunc", shell=True)
                subprocess.call("dd if=/boot/grub_post_mbr_gap of=" + usb_dev_root + " count=62 bs=512 seek=1 conv=notrunc", shell=True)
            else :  # Install Syslinux
                subprocess.call("cp -r /tmp/boot/syslinux " + live_workdir + "/boot/", shell=True)
                subprocess.call("cp /tmp/boot/vesamenu.c32 " + live_workdir + "/boot/", shell=True)
                shutil.rmtree("/tmp/boot", ignore_errors=True)
                subprocess.call("syslinux -f " + usb_device, shell=True)
                subprocess.call("eject " + live_workdir, shell=True)
                subprocess.call("rm -rf " + live_workdir, shell=True)
                
            self.progress_bar.set_text(_("LiveUSB device succesfully created..."))
            self.progress_bar.set_fraction(1.0)
            # there's more work, return True
            yield True        
            subprocess.call("sync", shell=True)
            time.sleep(3)

### Add some basic check here
            info_dialog(_("Your Live USB key has been successfully created. \n\
You can now exit LiveClone program and unplug your customized live USB key, \
it is unmounted and ready for use "))

        self.progress_dialog.hide()

        self.window.show()

        # no more work, return False
        yield False

    def on_check_persistence_toggled(self, *args):
        """
        Called when USB 'use persistence' checkbox is toggled
        """
        if self.use_persistence.get_active() == True :
            self.persistence_size.set_sensitive(True)
            self.persistence_size_label.set_sensitive(True)

        if self.use_persistence.get_active() == False :
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
    dialog = gtk.MessageDialog(parent = parent, type = gtk.MESSAGE_WARNING, flags = gtk.DIALOG_MODAL)
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
