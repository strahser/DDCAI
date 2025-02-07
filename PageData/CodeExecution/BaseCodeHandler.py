
class BaseCodeHandler:
    """Base class for code handlers with common methods."""

    def __init__(self, conn):
        """
        Initializes the BaseCodeHandler.

        Args:
            conn: The database connection object.
        """
        self.conn = conn
        self.output_placeholder = None
        self.category = ""
        self.code = ""
        self.code_name = ""

    def set_output_placeholder(self, placeholder):
        """Sets a common placeholder for output."""
        self.output_placeholder = placeholder

    def reset_state(self):
        """Resets the state to default values."""
        self.code = ""
        self.code_name = ""
        self.category = ""
