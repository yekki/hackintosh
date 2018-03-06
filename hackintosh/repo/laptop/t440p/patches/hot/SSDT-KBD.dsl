// Re-Map FN Buttons (F4,F5,F6,F7,F8,F9,F10,F11,F12)

//DefinitionBlock("", "SSDT", 2, "Yekki", "KBD", 0)
//{
    External (_SB_.PCI0.LPC.EC__, DeviceObj)    // (from opcode)
    External (_SB_.PCI0.LPC.KBD_, DeviceObj)    // (from opcode)
    External (KBD_, UnknownObj)    // (from opcode)

    Scope (_SB.PCI0.LPC.EC)
    {
        Method (_Q14, 0, NotSerialized)  // Brightness Up
        {
            Notify (KBD, 0x0406)
            Notify (KBD, 0x0486)
        }

        Method (_Q15, 0, NotSerialized)  // Brightness Down
        {
            Notify (KBD, 0x0405)
            Notify (KBD, 0x0485)
        }

        Method (_Q28, 0, NotSerialized)  // Microphone Mute - Mapped to Siri (SysPrefs>Keyboard>Shortcuts)
        {
            Notify (KBD, 0x0368)
            Notify (KBD, 0x03E8)
        }

        Method (_Q19, 0, NotSerialized)  // Projector / Mirror mode
        {
            Notify (KBD, 0x046E)
            Notify (KBD, 0x04EE)
        }

        Method (_Q2A, 0, NotSerialized)  // Wireless ON/OFF - Mapped to Notification Center (SysPrefs>Keyboard>Shortcuts)
        {
            Notify (KBD, 0x0369)
            Notify (KBD, 0x03E9)
        }

        Method (_Q66, 0, NotSerialized)  // Settings - Mapped to System Preferences (SysPrefs>Keyboard>Shortcuts)
        {
            Notify (KBD, 0x0364)
            Notify (KBD, 0x03E4)
        }

        Method (_Q67, 0, NotSerialized)  // Windows Search (Cortana) - Mapped to Spotlight Search (SysPrefs>Keyboard>Shortcuts)
        {
            Notify (KBD, 0x036A)
            Notify (KBD, 0x03EA)
        }

        Method (_Q68, 0, NotSerialized)  // ALT+TAB Menu - Disabled (No Function Left to Assign)
        {
            Notify (KBD, 0x036B)
            Notify (KBD, 0x03EB)
        }

        Method (_Q69, 0, NotSerialized)  // Start Menu - Mapped to Launchpad (SysPrefs>Keyboard>Shortcuts)
        {
            Notify (KBD, 0x0367)
            Notify (KBD, 0x03E7)
        }
    }
//}
//EOF