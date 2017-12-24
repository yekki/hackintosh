// Overriding _PTS

//DefinitionBlock("", "SSDT", 2, "T440P", "PTS", 0)
//{
    External(ZPTS, MethodObj)
    External(_SB.PCI0.XHC.PMEE, FieldUnitObj)
    // In DSDT, native _PTS is renamed to ZPTS
    // As a result, calls to this method land here.
    Method(_PTS, 1)
    {
        ZPTS(Arg0)
        If (5 == Arg0)
        {
            // fix "auto start after shutdown"
            \_SB.PCI0.XHC.PMEE = 0
        }
    }
//}
//EOF