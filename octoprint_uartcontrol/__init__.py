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

    target_serial = None
    target_port = "/dev/Dummy0"

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
        self.populate_actions()
        self.on_event('Startup', None)


    def populate_actions(self):
        try:
            for controller in self._settings.get(["uart_controllers"]):
                if controller["trig_action"] != "Manual":
                    self.action_map[controller["trig_action"]].append({
                        'message': controller["message"]
                    })
        except Exception as e:
            self._logger.warning("Exception: {}".format(e))
            self._logger.warning("Failed to populate action map")


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
            ), ]


    def get_assets(self):
        return dict(
            js=["js/uartcontrol.js", "js/fontawesome-iconpicker.min.js"],
            css=["css/uartcontrol.css", "css/fontawesome-iconpicker.min.css"],
        )


    def get_settings_defaults(self):
        return dict(
            uart_interface=dict(
                serial_port="None",
                baud_rate="9600",
                byte_size="EIGHTBITS",
                parity="PARITY_NONE",
                stop_bits="STOP_BITS_ONE",
                flow_control="None"
            ),
            uart_controllers=[]
        )


    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.target_port = self._settings.get(["uart_interface"])["serial_port"]
        self.clear_actions()
        self.populate_actions()


    def on_after_startup(self):
        self._logger.info("UART Control Start")
        for controller in self._settings.get(["uart_controllers"]):
            self._logger.info(
                "Startup Controller: Name: {}, Message: {}".format(
                    controller["name"],
                    controller["message"],
                ))
        interface = self._settings.get(["uart_interface"])
        self.open_serial_port(interface)

    ''' SEND MESSAGE IF CONTROLLER ACTION FOUND '''


    def open_serial_port(self, interface):
        self.target_port = interface["serial_port"]
        self._logger.info(
                "Serial Port Start: {}".format(
                    str(interface)))

    def on_event(self, event, payload):
        self._logger.info(
            "UART Control caught event: {}, {}".format(str(event), str(payload)))

        try:
            for action in self.action_map[event]:
                self.send_to_serial(action['message'])
        except KeyError:
            pass


    def get_api_commands(self):
        return dict(sendUartMessage=["id"],
                    testUartMessage=["message",
                                     "port",
                                     "baud",
                                     "size",
                                     "parity",
                                     "stop",
                                     "flow"])

    ''' SEND MESSAGE IF USER TRIGGERS MANUAL '''


    def on_api_command(self, command, data):
        if not user_permission.can():
            return flask.make_response("Insufficient rights", 403)

        if command == "testUartMessage":
            self._logger.info("{}".format(str(data)))
            if data["port"] == "None":
                return flask.jsonify({"result": "none"})
            #self._logger.info("Message: {}".format(data["message"]))
            #return {"result": "fail"} if serial cannot send
            return flask.jsonify({"result": "good"})

        if command == "sendUartMessage":
            controller = self._settings.get(["uart_controllers"])[int(data["id"])]
            message = controller["message"]
            self._logger.info("Test send")
            #self.send_to_serial(message)


    def on_api_get(self, request):
        port_dict = {"unavailable": ""}
        port_list = ["None"]
        # Get all available serial ports
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            port_list.append(p.device)
        self._logger.info("Available Ports: {}".format(str(port_list)))
        # If saved port is not available add to list anyways
        if self.target_port not in port_list:
            port_dict["unavailable"] = self.target_port
            port_list.append(self.target_port)
        # Send to front end
        port_dict["list"] = port_list

        return flask.jsonify(port_dict)


    def send_to_serial(self, message):
        if target_serial != "None":
            try:
                message, i = codecs.unicode_escape_decode(message)
                target_serial.write(message.encode('utf-8'))

            except serial.SerialException:
                self._logger.info(
                    "UART Control failed to send message: {}".format(
                        message))
                self._logger.info(
                    "Target {}: Is busy or does not exist".format(self.target_port))
                return

        self._logger.info(
            "UART Control send: {}, \'{}\'".format(
                self.target_port, message))


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


__plugin_name__ = "UART Control"
__plugin_pythoncompat__ = ">=2.7,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = UartControlPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
