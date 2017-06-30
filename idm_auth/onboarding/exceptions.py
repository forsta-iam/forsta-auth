from social_core.exceptions import AuthForbidden


class RegistrationClosed(AuthForbidden):
    def __str__(self):
        return "We didn't recognise you, and new registrations are currently closed."


class SAMLRegistrationClosed(RegistrationClosed):
    def __str__(self):
        return "We didn't recognise you, and new institutional login registrations are currently closed."


class SocialRegistrationClosed(RegistrationClosed):
    def __str__(self):
        return "We didn't recognise you, and new social registrations are currently closed."
