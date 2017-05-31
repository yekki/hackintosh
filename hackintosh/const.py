class _const:
    class ConstError(TypeError): pass
    class ConstCaseError(ConstError): pass

    def __setattr__(self, key, value):
        if key in self.__dict__.keys():
            raise self.ConstError
        if not key.isupper():
            raise  self.ConstCaseError

        self.__dict__[key] = value

import sys

sys.modules[__name__] = _const()