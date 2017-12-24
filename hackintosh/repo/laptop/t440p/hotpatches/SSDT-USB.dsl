// Custom Active USB Port Injector SSDT for Lenovo ThinkPad T440P

//DefinitionBlock ("", "SSDT", 2, "Yekki", "USB", 0)
//{
    Device(UIAC)
    {
        Name(_HID, "UIA00000")

        Name(RMCF, Package()
        {
            "8086_8c31", Package()
            {
                "port-count", Buffer() { 21, 0, 0, 0 },
                "ports", Package()
                {
                    "HS01", Package()
                    {
                        "UsbConnector", 0,
                        "port", Buffer() { 1, 0, 0, 0 },
                    },
                    "HS02", Package()
                    {
                        "UsbConnector", 0,
                        "port", Buffer() { 2, 0, 0, 0 },
                    },
                    "HS03", Package() //USB3 Device
                    {
                        "UsbConnector", 3,
                        "port", Buffer() { 3, 0, 0, 0 },
                    },
                    "HS06", Package() //USB3 Device
                    {
                        "UsbConnector", 3,
                        "port", Buffer() { 6, 0, 0, 0 },
                    },
                    "HS07", Package() //Unknown (Propably Intel WIFI)
                    {
                        "UsbConnector", 255,
                        "port", Buffer() { 7, 0, 0, 0 },
                    },
                    "HS11", Package() //Bluetooth
                    {
                        "UsbConnector", 255,
                        "port", Buffer() { 11, 0, 0, 0 },
                    },
                    "HS12", Package() //Camera
                    {
                        "UsbConnector", 255,
                        "port", Buffer() { 12, 0, 0, 0 },
                    },
                    "SSP1", Package() //USB3 Device
                    {
                        "UsbConnector", 3,
                        "port", Buffer() { 16, 0, 0, 0 },
                    },
                    "SSP2", Package() //USB3 Device
                    {
                        "UsbConnector", 3,
                        "port", Buffer() { 17, 0, 0, 0 },
                    },
                },
            },
        })
    }
//}
//EOF
