/*
 * View model for OctoPrint-UartControl
 *
 * Author: Andrew O'Shei
 * License: AGPLv3
 */


$(function () {
    function UartControlViewModel(parameters) {
        var self = this;
        self.settings = parameters[0];
        self.uartButtons = ko.observableArray();
        self.uartConfigurations = ko.observableArray();


        self.onBeforeBinding = function () {
            self.uartConfigurations(self.settings.settings.plugins.uartcontrol.uart_configurations.slice(0));
            self.updateUartButtons();
        };


        self.onSettingsShown = function () {
            self.uartConfigurations(self.settings.settings.plugins.uartcontrol.uart_configurations.slice(0));
            self.updateIconPicker();
            self.setSerialOptions();
        };


        self.onSettingsHidden = function () {
            self.uartConfigurations(self.settings.settings.plugins.uartcontrol.uart_configurations.slice(0));
            self.updateUartButtons();
        };


        self.onSettingsBeforeSave = function () {
            self.settings.settings.plugins.uartcontrol.uart_configurations(self.uartConfigurations.slice(0));
        };


        self.addUartConfiguration = function () {
            self.uartConfigurations.push({
                icon: "fas fa-plug",
                name: "",
                message: "",
                serial_port: "",
                baud_rate: "",
                trig_action: "",
            });
            self.updateIconPicker();
            self.addSerialOptions();
        };


        self.removeUartConfiguration = function (configuration) {
            self.uartConfigurations.remove(configuration);
        };


        self.updateIconPicker = function () {
            $('.iconpicker').each(function (index, item) {
                $(item).iconpicker({
                    placement: "bottomLeft",
                    hideOnSelect: true,
                });
            });
        };

        
        self.setSerialOptions = function () {
            OctoPrint.simpleApiGet("uartcontrol").then(function (ports) {
                var port_list = ports.port_list
                var port_sel = ports.port_sel
                $('.serial-select').each(function (index, item) {
                    var len = port_list.length;
                    for (var i = 0; i < len; i++) {
                        $(this).append($('<option>', {
                            value: port_list[i],
                            text: port_list[i]
                        }));
                    };
                    $(this).val(port_sel[index]);
                    $(this).trigger('change');
                });
            });
        };
        
        
        self.addSerialOptions = function () {
            OctoPrint.simpleApiGet("uartcontrol").then(function (ports) {
                var port_list = ports.port_list
                var len = port_list.length;
                for (var i = 0; i < len; i++) {
                    $('.serial-select:last').append($('<option>', {
                        value: port_list[i],
                        text: port_list[i]
                    }));
                };
                $('.serial-select:last').val('Dummy');
                $('.serial-select:last').trigger('change');
            });
        };


        self.updateUartButtons = function () {
            self.uartButtons(ko.toJS(self.uartConfigurations).map(function (item) {
                return {
                    icon: item.icon,
                    name: item.name,
                    message: item.message,
                    serial_port: item.serial_port,
                    baud_rate: item.baud_rate,
                    trig_action: item.trig_action,
                };
            }));
        };


        self.sendUartMessage = function () {
            OctoPrint.simpleApiCommand("uartcontrol", "sendUartMessage", {id: self.uartButtons.indexOf(this)});
        };
    };


    OCTOPRINT_VIEWMODELS.push({
        construct: UartControlViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_uartcontrol", "#sidebar_plugin_uartcontrol"]
    });
});


