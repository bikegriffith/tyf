
class IterationError(Exception):
    pass

class CannotFulfillOverride(IterationError):
    pass

class NoAvailableOpponnentError(IterationError):
    pass