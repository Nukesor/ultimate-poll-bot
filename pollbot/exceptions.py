class RollbackException(Exception):
    """Issue a rollback.

    This exception should be thrown if an error occurs and
    the session should be rolled back.
    """

    def __init__(self, message):
        """
        Initialize the message

        Args:
            self: (todo): write your description
            message: (str): write your description
        """
        self.message = message
