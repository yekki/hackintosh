// configuration data for other SSDTs in this pack

DefinitionBlock("", "SSDT", 2, "Yekki", "T440P", 0)
{
    Device(RMCF)
    {
        Name(_ADR, 0)   // do not remove

        Method(HELP)
        {
            Store("BKLT indicates the type of backlight control. 0: IntelBacklight, 1: AppleBacklight", Debug)
            Store("LMAX indicates max for IGPU PWM backlight. Ones: Use default, other values must match framebuffer", Debug)
        }

        // BKLT: Backlight control type
        //
        // 0: Using IntelBacklight.kext
        // 1: Using AppleBacklight.kext + AppleBacklightInjector.kext
        Name(BKLT, 1)

        // LMAX: Backlight PWM MAX.  Must match framebuffer in use.
        //
        // Ones: Default will be used (0x710 for Ivy/Sandy, 0xad9 for Haswell/Broadwell)
        // Other values: must match framebuffer
        Name(LMAX, 0xad9)
    }
    //14 files
    #include "SSDT-PluginType1.dsl"
    #include "SSDT-XOSI.dsl"
    #include "SSDT-ALC292.dsl"
    #include "SSDT-LPC.dsl"
    #include "SSDT-HDAU.dsl"
    #include "SSDT-HDEF.dsl"
    #include "SSDT-IMEI.dsl"
    #include "SSDT-PNLF.dsl"
    #include "SSDT-KBD.dsl"
    #include "SSDT-ESEL.dsl"
    #include "SSDT-USB.dsl"
    #include "SSDT-Disable_EHCI.dsl"
    #include "SSDT-ALS0.dsl"
    #include "SSDT-BAT.dsl"
    #include "SSDT-PTS.dsl"
    

}
//EOF
