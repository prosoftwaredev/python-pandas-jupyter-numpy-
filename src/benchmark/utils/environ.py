from environ import Env as EnvironEnv

from .kms import string_or_b64kms


class Env(EnvironEnv):
    """Extends environ.Env with added AWS KMS encryption support."""

    def __call__(self, var, cast=None, default=EnvironEnv.NOTSET, parse_default=False):
        value = self.get_value(var, cast=cast, default=default, parse_default=parse_default)

        return string_or_b64kms(value)
