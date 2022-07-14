import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SymbolPasswordValidator(object):
    allow_symbols = '~!@#$%^&*_-+=<>.'
    allow_symbol_patterns = ['~', '!', '@', '#', '$', '%', '^',
                             '&', '*', '_', '-', '+', '=', '<', '>', '.']

    def validate(self, password, user=None):
        if not re.findall('[~!@#$%^&*_\-+=<>.]', password):
            raise ValidationError(
                _('패스워드는 최소 특수문자 1개를 포함해야 합니다: ' +
                  self.allow_symbols),
                code='password_no_symbol',
            )

    def get_help_text(self):
        return _(
            '패스워드는 최소 특수문자 1개를 포함해야 합니다: ' +
            self.allow_symbols
        )


class NumberPasswordValidator(object):
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            raise ValidationError(
                _("패스워드는 최소 숫자 1개를 포함해야 합니다: 0-9."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "패스워드는 최소 숫자 1개를 포함해야 합니다: 0-9."
        )


class LowercasePasswordValidator(object):
    def validate(self, password, user=None):
        if not re.findall('[a-z]', password):
            raise ValidationError(
                _("패스워드는 최소 영어 소문자 1개를 포함해야 합니다: a-z."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _(
            "패스워드는 최소 영어 소문자 1개를 포함해야 합니다: a-z."
        )
