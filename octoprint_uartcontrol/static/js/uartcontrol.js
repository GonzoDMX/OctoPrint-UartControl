/*
 * View model for OctoPrint-UartControl
 *
 * Author: Andrew O'Shei
 * License: AGPLv3
 */


$(function() {
    function UartControlViewModel(parameters) {
        var self = this;
        self.settings = parameters[0];
        self.uartButtons = ko.observableArray();
        self.uartControllers = ko.observableArray();
        self.uartInterface = ko.observableArray();

        self.onBeforeBinding = function() {
            self.uartControllers(self.settings.settings.plugins.uartcontrol.uart_controllers.slice(0));
            self.uartInterface(self.settings.settings.plugins.uartcontrol.uart_interface);
            self.updateUartButtons();
        };

        self.onSettingsShown = function() {
            self.uartControllers(self.settings.settings.plugins.uartcontrol.uart_controllers.slice(0));
            self.uartInterface(self.settings.settings.plugins.uartcontrol.uart_interface);
            self.updateIconPicker();
            self.setSerialList();
            self.setSerialConfig();
        };

        self.onSettingsHidden = function() {
            self.uartControllers(self.settings.settings.plugins.uartcontrol.uart_controllers.slice(0));
            self.uartInterface(self.settings.settings.plugins.uartcontrol.uart_interface);
            self.updateUartButtons();
        };

        self.onSettingsBeforeSave = function() {
            self.settings.settings.plugins.uartcontrol.uart_controllers(self.uartControllers.slice(0));
            self.settings.settings.plugins.uartcontrol.uart_interface.serial_port(self.uartInterface.serial_port);
            self.settings.settings.plugins.uartcontrol.uart_interface.baud_rate(self.uartInterface.baud_rate);
            self.settings.settings.plugins.uartcontrol.uart_interface.byte_size(self.uartInterface.byte_size);
            self.settings.settings.plugins.uartcontrol.uart_interface.parity(self.uartInterface.parity);
            self.settings.settings.plugins.uartcontrol.uart_interface.stop_bits(self.uartInterface.stop_bits);
            self.settings.settings.plugins.uartcontrol.uart_interface.flow_control(self.uartInterface.flow_control);
        };

        self.addUartController = function() {
            self.uartControllers.push({
                icon: "fas fa-plug",
                name: "",
                message: "",
                trig_action: "",
            });
            self.updateIconPicker();
        };

        self.removeUartController = function(configuration) {
            self.uartControllers.remove(configuration);
        };

        self.updateIconPicker = function() {
            $('.iconpicker').each(function(index, item) {
                $(item).iconpicker({
                    placement: "bottomLeft",
                    hideOnSelect: true,
                });
            });
        };


        self.setSerialList = function() {
            OctoPrint.simpleApiGet("uartcontrol").then(function(port_dict) {
                $('.serial-select').each(function(index, item) {
                    var port_list = port_dict.list
                    var len = port_list.length;
                    for (var i = 0; i < len; i++) {
                        var classID = "opt-available";
                        if (port_list[i] === port_dict.unavailable) {
                            classID = "opt-unavailable";
                        }
                        $(this).append($('<option>', {
                            value: port_list[i],
                            text: port_list[i],
                            class: classID
                        }));
                    };
                    $(this).val(self.settings.settings.plugins.uartcontrol.uart_interface.serial_port.v());
                    $(this).trigger('change');
                });
            });
        };

        self.setSerialConfig = function() {
            $('.baud-select').val(self.settings.settings.plugins.uartcontrol.uart_interface.baud_rate.v());
            $('.baud-select').trigger('change');
            $('.byte-select').val(self.settings.settings.plugins.uartcontrol.uart_interface.byte_size.v());
            $('.byte-select').trigger('change');
            $('.parity-select').val(self.settings.settings.plugins.uartcontrol.uart_interface.parity.v());
            $('.parity-select').trigger('change');
            $('.stop-select').val(self.settings.settings.plugins.uartcontrol.uart_interface.stop_bits.v());
            $('.stop-select').trigger('change');
            $('.flow-select').val(self.settings.settings.plugins.uartcontrol.uart_interface.flow_control.v());
            $('.flow-select').trigger('change');
        };

        self.updateUartButtons = function() {
            self.uartButtons(ko.toJS(self.uartControllers).map(function(item) {
                return {
                    icon: item.icon,
                    name: item.name,
                    message: item.message,
                    trig_action: item.trig_action,
                };
            }));
        };

        self.sendUartMessage = function() {
            OctoPrint.simpleApiCommand("uartcontrol", "sendUartMessage", {
                id: self.uartButtons.indexOf(this)
            });
        };

        self.testUartMessage = function() {
            var message = this.message;
            if (typeof message != "string") {
                message = this.message.v();
            };
            OctoPrint.simpleApiCommand(
                "uartcontrol", "testUartMessage", {
                    message: message,
                    port: self.uartInterface.serial_port,
                    baud: self.uartInterface.baud_rate,
                    size: self.uartInterface.byte_size,
                    parity: self.uartInterface.parity,
                    stop: self.uartInterface.stop_bits,
                    flow: self.uartInterface.flow_control
                }).then(async function (response) {
                  if (response.result === "good") {
                      alert("Success !" +
                          "\nMessage: \'" + message +
                          "\'\nSerial: " + self.uartInterface.serial_port +
                          ", " + self.uartInterface.baud_rate)
                  } else if (response.result === "none") {
                      alert("\nMessage: \'" + message +
                          "\'\nSerial: " + self.uartInterface.serial_port +
                          ", " + self.uartInterface.baud_rate +
                          "\n\nNote: Port \'None\' is a placeholder, no message was sent.")
                  } else {
                      alert("Failure !\nUnable to send message.")
                  }});
        };
    };

    OCTOPRINT_VIEWMODELS.push({
        construct: UartControlViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_uartcontrol", "#sidebar_plugin_uartcontrol"]
    });
});
