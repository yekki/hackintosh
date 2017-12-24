//Custom SSDT for Codec Commander Override of Realtek ALC292 Codec

//DefinitionBlock ("", "SSDT", 1, "Yekki", "ALC292", 0x00000000)
//{
    External (_SB_.PCI0.HDEF, DeviceObj)    // (from opcode)

    Name (_SB.PCI0.HDEF.RMCF, Package (0x02)
    {
        "CodecCommander", 
        Package (0x08)
        {
            "Custom Commands", 
            Package (0x06)
            {
                Package (0x00) {}, 
                Package (0x08)
                {
                    "Command", 
                    Buffer (0x04)
                    {
                         0x01, 0xA7, 0x07, 0x24                         
                    }, 

                    "On Init", 
                    ">y", 
                    "On Sleep", 
                    ">n", 
                    "On Wake", 
                    ">y"
                }, 

                Package (0x08)
                {
                    "Command", 
                    Buffer (0x04)
                    {
                         0x01, 0x57, 0x08, 0x83                         
                    }, 

                    "On Init", 
                    ">y", 
                    "On Sleep", 
                    ">n", 
                    "On Wake", 
                    ">y"
                }, 

                Package (0x08)
                {
                    "Command", 
                    Buffer (0x04)
                    {
                         0x00, 0x17, 0xFF, 0x00                         
                    }, 

                    "On Init", 
                    ">y", 
                    "On Sleep", 
                    ">n", 
                    "On Wake", 
                    ">n"
                }, 

                Package (0x08)
                {
                    "Command", 
                    Buffer (0x04)
                    {
                         0x00, 0x17, 0xFF, 0x00                         
                    }, 

                    "On Init", 
                    ">y", 
                    "On Sleep", 
                    ">n", 
                    "On Wake", 
                    ">n"
                }, 

                Package (0x08)
                {
                    "Command", 
                    Buffer (0x04)
                    {
                         0x00, 0x17, 0x05, 0x03                         
                    }, 

                    "On Init", 
                    ">y", 
                    "On Sleep", 
                    ">n", 
                    "On Wake", 
                    ">n"
                }
            }, 

            "Perform Reset", 
            ">y", 
            "Send Delay", 
            0x0A, 
            "Sleep Nodes", 
            ">n"
        }
    })
//}
//EOF