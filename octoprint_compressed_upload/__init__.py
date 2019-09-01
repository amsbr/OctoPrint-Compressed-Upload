# coding=utf-8
from __future__ import absolute_import

__author__ = "Anderson Silva <ams.bra@gmail.com>"
__license__ = "GNU Affero General Public License http://www.gnu.org/licenses/agpl.html"
__copyright__ = "Copyright (C) 2019 Anderson Silva - AGPLv3 License"

import os
import octoprint.events
import octoprint.plugin
import octoprint.filemanager
import octoprint.filemanager.util
import bz2
import gzip
import zipfile
import tarfile

class Compressed_UploadPlugin(octoprint.plugin.EventHandlerPlugin,
                  octoprint.plugin.StartupPlugin):

    def on_after_startup(self):
        self._logger.info("Compressed Upload Started")

    def compressed_extension_tree(self, *args, **kwargs):
        return dict(
            model=dict(
                zip=["zip"],
                gzip=["gz", "tgz", "tar.gz"],
                bzip2=["bz2", "tbz2", "tar.bz2"],
                tar=["tar"]
            )
        )

    def uncompress_file(self, path, file_object, links=None, printer_profile=None, allow_overwrite=True, *args, **kwargs):
        file_ext = path.split(".")
        if (not ("zip" in file_ext)) and (not ("gz" in file_ext)) and (not ("bz2" in file_ext)) and (not ("tgz" in file_ext)) and (not ("tbz2" in file_ext)) and (not ("tar" in file_ext)):
            print("return")
            return file_object

        print("uncompress")
        destination = octoprint.filemanager.destinations.FileDestinations.LOCAL
        if ("zip" in file_ext):
            if (zipfile.is_zipfile(file_object.path)):
                self._logger.info("Compressed Upload is zip")
                
                extract_path = self._file_manager.path_on_disk(destination, path).replace(path, "")
                compressed_file = zipfile.ZipFile(file_object.path)
                compressed_file.extractall(path=extract_path)

                #compressed_file = zipfile.ZipFile(file_object.path)
                #for file_extract in compressed_file.namelist():
                #    fextract = compressed_file.open(file_extract)
                #    file_content = fextract.read()
                    
                #    extract_path = self._file_manager.path_on_disk(destination, file_extract)
                #    upload_file = open(extract_path, "wb")
                #    upload_file.write(file_content)
                #    upload_file.close()
                    
                return None

        elif ("tar" in file_ext) or ("tgz" in file_ext) or ("tbz2" in file_ext):
            if (tarfile.is_tarfile(file_object.path)):
                self._logger.info("Compressed Upload is tar")
                
                extract_path = self._file_manager.path_on_disk(destination, path).replace(path, "")
                compressed_file = tarfile.open(file_object.path)
                compressed_file.extractall(path=extract_path)
                    
                return None
            
        elif ("gz" in file_ext) and not ("tar" in file_ext):
            print("Compressed Upload is gz")
                
            fextract = gzip.open(file_object.path, "rb")
            file_content = fextract.read()

            extract_path = self._file_manager.path_on_disk(destination, path.replace(".gz", ""))
            upload_file = open(extract_path, "wb")
            upload_file.write(file_content)
            upload_file.close()
                    
            return None

        elif ("bz2" in file_ext) and not ("tar" in file_ext):
            print("Compressed Upload is bz2")
                
            fextract = bz2.BZ2File(file_object.path, "r")
            file_content = fextract.read()

            extract_path = self._file_manager.path_on_disk(destination, path.replace(".bz2", ""))
            upload_file = open(extract_path, "wb")
            upload_file.write(file_content)
            upload_file.close()
                    
            return None
        
    #def get_settings_defaults(self):
    #    return dict(
    #      compressed_zip=True,
    #      compressed_gzip=True,
    #      compressed_bzip2=True,
    #      compressed_tar=True,
    #      )

    #def get_template_configs(self):
    #    return [
    #        dict(type="settings", custom_bindings=False)
    #    ]

    def on_event(self, event, payload):
        """
        Callback for general OctoPrint events.
        """
        
        if event == octoprint.events.Events.UPLOAD or event == "FileAdded":
            if payload["path"] != None:
                file = payload["path"]
            elif payload["file"] != None:
                file = payload["file"]
            else:
                file = ""

            file_ext = file.split(".")

            if (("zip" in file_ext)) or (("gz" in file_ext)) or (("bz2" in file_ext)) or (("tgz" in file_ext)) or (("tbz2" in file_ext)) or (("tar" in file_ext)):
                if (event == "FileAdded"):
                    target = payload["storage"]
                else:
                    target = payload["target"]

                if (target == "local"):
                    octoprint_target = octoprint.filemanager.FileDestinations.LOCAL
                else:
                    octoprint_target = octoprint.filemanager.FileDestinations.SDCARD
                    
                name = payload["name"]
            
                if (file != "") and (target == "local"):
                    self._file_manager.remove_file(octoprint_target, file)


    ##~~ Softwareupdate hook
    def get_update_information(self):
        return dict(
            stats=dict(
                displayName="Compressed Upload",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="amsbr",
                repo="OctoPrint-Compressed-Upload",
                current=self._plugin_version,

                # update method: pip w/ dependency links
                pip="https://github.com/amsbr/OctoPrint-Compressed-Upload/archive/{target_version}.zip"
            )
        )


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Compressed Upload"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Allow upload compressed files"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Compressed_UploadPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.filemanager.extension_tree": __plugin_implementation__.compressed_extension_tree,
        "octoprint.filemanager.preprocessor": __plugin_implementation__.uncompress_file
    }
