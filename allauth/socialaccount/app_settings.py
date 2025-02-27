class AppSettings(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def _setting(self, name, dflt):
        from django.conf import settings

        getter = getattr(
            settings,
            "ALLAUTH_SETTING_GETTER",
            lambda name, dflt: getattr(settings, name, dflt),
        )
        return getter(self.prefix + name, dflt)

    @property
    def QUERY_EMAIL(self):
        """
        Request e-mail address from 3rd party account provider?
        E.g. using OpenID AX
        """
        from allauth.account import app_settings as account_settings

        return self._setting("QUERY_EMAIL", account_settings.EMAIL_REQUIRED)

    @property
    def AUTO_SIGNUP(self):
        """
        Attempt to bypass the signup form by using fields (e.g. username,
        email) retrieved from the social account provider. If a conflict
        arises due to a duplicate e-mail signup form will still kick in.
        """
        return self._setting("AUTO_SIGNUP", True)

    @property
    def PROVIDERS(self):
        """
        Provider specific settings
        """
        ret = self._setting("PROVIDERS", {})
        oidc = ret.get("openid_connect")
        if oidc:
            ret["openid_connect"] = self._migrate_oidc(oidc)
        return ret

    def _migrate_oidc(self, oidc):
        servers = oidc.get("SERVERS")
        if servers is None:
            return oidc
        ret = {}
        apps = []
        for server in servers:
            app = dict(**server["APP"])
            app_settings = {}
            if "token_auth_method" in server:
                app_settings["token_auth_method"] = server["token_auth_method"]
            app_settings["server_url"] = server["server_url"]
            app.update(
                {
                    "name": server.get("name", ""),
                    "provider_id": server["id"],
                    "settings": app_settings,
                }
            )
            assert app["provider_id"]
            apps.append(app)
        ret["APPS"] = apps
        return ret

    @property
    def EMAIL_REQUIRED(self):
        """
        The user is required to hand over an e-mail address when signing up
        """
        from allauth.account import app_settings as account_settings

        return self._setting("EMAIL_REQUIRED", account_settings.EMAIL_REQUIRED)

    @property
    def EMAIL_VERIFICATION(self):
        """
        See e-mail verification method
        """
        from allauth.account import app_settings as account_settings

        return self._setting("EMAIL_VERIFICATION", account_settings.EMAIL_VERIFICATION)

    @property
    def ADAPTER(self):
        return self._setting(
            "ADAPTER",
            "allauth.socialaccount.adapter.DefaultSocialAccountAdapter",
        )

    @property
    def FORMS(self):
        return self._setting("FORMS", {})

    @property
    def LOGIN_ON_GET(self):
        return self._setting("LOGIN_ON_GET", False)

    @property
    def STORE_TOKENS(self):
        return self._setting("STORE_TOKENS", False)

    @property
    def UID_MAX_LENGTH(self):
        return 191

    @property
    def SOCIALACCOUNT_STR(self):
        return self._setting("SOCIALACCOUNT_STR", None)


# Ugly? Guido recommends this himself ...
# http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
import sys  # noqa


app_settings = AppSettings("SOCIALACCOUNT_")
app_settings.__name__ = __name__
sys.modules[__name__] = app_settings
