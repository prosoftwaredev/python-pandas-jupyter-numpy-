class BaseActivationBackend(object):
    """Base activation backend."""
    def get_activation_key(self, user):
        """
        Generate the activation key which will be emailed to the user.
        """
        return NotImplementedError()

    def validate_key(self, activation_key):
        """
        Verify that the activation key is valid and within the
        permitted activation time window, returning the username if
        valid or ``None`` if not.
        """
        return NotImplementedError()

    def get_user(self, username):
        """
        Given the verified username, look up and return the
        corresponding user account if it exists, or ``None`` if it
        doesn't.
        """
        return NotImplementedError()
