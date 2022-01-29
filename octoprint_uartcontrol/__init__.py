# coding=utf-8
from __future__ import absolute_import, print_function
from octoprint.server import user_permission

import octoprint.plugin
from octoprint.events import eventManager, Events
import flask
import serial
import serial.tools.list_ports
import codecs

class UartControlPlugin(
        octoprint.plugin.StartupPlugin,
        octoprint.plugin.EventHandlerPlugin,
        octoprint.plugin.TemplatePlugin,
        octoprint.plugin.AssetPlugin,
        octoprint.plugin.SettingsPlugin,
        octoprint.plugin.SimpleApiPlugin,
        octoprint.plugin.RestartNeedingPlugin,
):

        #ser = serial.Serial("/dev/ttyS0", 9600)

        used_ports = []

        action_map = {'Startup': [],
                      'Shutdown': [],
                      'UserLoggedIn': [],
                      'UserLoggedOut': [],
                      'Error': [],
                      'Connected': [],
                      'Disconnected': [],
                      'PrintStarted': [],
                      'PrintFailed': [],
                      'PrintDone': [],
                      'PrintCancelled': [],
                      'PrintPaused': [],
                      'PrintResumed': [],
                      'PowerOn': [],
                      'PowerOff': [],
                      'Home': [],
                      'Cooling': [],
                      'Alert': [],
                      'EStop': [],
                      'FilamentChange': [],
                      'CaptureStart': [],
                      'CaptureDone': [],
                      'CaptureFailed': [],
                      'MovieRendering': [],
                      'MovieDone': [],
                      'MovieFailed': []}


        def on_startup(self, *args, **kwargs):
            self._logger.info("UART Control Start")
            for configuration in self._settings.get(["uart_configurations"]):
                self._logger.info(
                    "Startup UART {}: ( {}, {} )".format(
                        configuration["name"],
                        configuration["serial_port"],
                        configuration["baud_rate"]
                    ))
                self.add_port(configuration["serial_port"])
            self.populate_actions()
            self.on_event('Startup', None)
                    
                    
        def populate_actions(self):
            for configuration in self._settings.get(["uart_configurations"]):
                if configuration["trig_action"] != "Manual":
                    self.action_map[configuration["trig_action"]].append({
                        'port': configuration["serial_port"],
                        'baud': configuration["baud_rate"],
                        'message': configuration["message"]
                    })


        def clear_actions(self):
            for value in self.action_map.values():
                del value[:]


        def get_template_configs(self):
                return [
                        dict(type="settings", custom_bindings=True),
                        dict(
                                type="sidebar",
                                custom_bindings=True,
                                template="uartcontrol_sidebar.jinja2",
                                icon="map-signs"
                        ),]


        def get_assets(self):
                return dict(
                           js=["js/uartcontrol.js", "js/fontawesome-iconpicker.min.js"],
                           css=["css/uartcontrol.css", "css/fontawesome-iconpicker.min.css"],
                       )


        def get_settings_defaults(self):
                return dict(uart_configurations=[])


        def on_settings_save(self, data):
                self.used_ports.clear()
                self.clear_actions()

                octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
                self.populate_actions()
                
                for configuration in self._settings.get(["uart_configurations"]):
                        self._logger.info(
                                "Reconfigured UART {}: ( {}, {} )".format(
                                        configuration["name"],
                                        configuration["serial_port"],
                                        configuration["baud_rate"]
                                ))
                        self.add_port(configuration["serial_port"])
               

        def on_after_startup(self):
                for configuration in self._settings.get(["uart_configurations"]):
                        self._logger.info(
                                "Configured UART {}: ( {}, {} )".format(
                                        configuration["name"],
                                        configuration["serial_port"],
                                        configuration["baud_rate"]
                                ))
                        self.add_port(configuration["serial_port"])
                            

        def on_event(self, event, payload):
                self._logger.info(
                    "UART Control caught event: {}, {}".format(str(event), str(payload)))
                
                try:
                    for action in self.action_map[event]:
                        self.send_to_serial(action['port'], action['baud'], action['message'])
                except KeyError:
                    pass
                    

        def get_api_commands(self):
                return dict(sendUartMessage=["id"])


        def on_api_command(self, command, data):
                if not user_permission.can():
                        return flask.make_response("Insufficient rights", 403)

                configuration = self._settings.get(["uart_configurations"])[int(data["id"])]
                message = configuration["message"]
                port = configuration["serial_port"]
                baud = configuration["baud_rate"]
				
                if command == "sendUartMessage":
                    self.send_to_serial(port, baud, message)


        def on_api_get(self, request):
            self._logger.info("Request: {}".format(request))
            port_list = ["Dummy", "Billy"]
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                port_list.append(p.device)
            
            self._logger.info("Available Ports: {}".format(str(port_list)))
            
            self._logger.info(
                    "Used Ports: {}".format(str(self.used_ports)))
            
            for p in self.used_ports:
                if p not in port_list:
            	    port_list.append(p)
            
            ports = {}
            ports['port_list'] = port_list
            ports['port_sel'] = self.used_ports
            
            return flask.jsonify(ports)


        def send_to_serial(self, port, baud, message):
            if port != "Dummy":
                try:
                    ser = serial.Serial(port, baud)
                    ser.open()
                    message, i = codecs.unicode_escape_decode(message)
                    ser.write(message.encode('utf-8'))
                
                except serial.SerialException:
                    self._logger.info(
                        "UART Control failed to send message: ( {}, {} ) \'{}\'".format(
                        port, baud, message))
                    return
            
            self._logger.info(
                "UART Control send: ( {}, {} ) \'{}\'".format(
                port, baud, message))


        def get_update_information(self):
                return dict(
                        uartcontrol=dict(
                        displayName="UART Control",
                        displayVersion=self._plugin_version,
                        type="github_release",
                        user="GonzoDMX",
                        repo="OctoPrint-UartControl",
                        current=self._plugin_version,
                        stable_branch=dict(
                                name="Stable",
                                branch="master",
                                comittish=["master"],
                        ),
                        prerelease_branches=[
                        dict(
                                name="Prerelease",
                                branch="development",
                                comittish=["development", "master"],
                        )],
                        pip="https://github.com/GonzoDMX/OctoPrint-UartControl/archive/{target_version}.zip",
                        ))


        def add_port(self, p):
                self.used_ports.append(p)


__plugin_name__ = "UART Control"
__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
        global __plugin_implementation__
        __plugin_implementation__ = UartControlPlugin()

        global __plugin_hooks__
        __plugin_hooks__ = {
                "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
        }

