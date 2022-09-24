from .ColourConverter import Converter, GamutA, GamutB, GamutC

Aconverter = Converter(GamutA)
Bconverter = Converter(GamutB)
Cconverter = Converter(GamutC)

defc = Bconverter