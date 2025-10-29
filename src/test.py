from Errors import Errors, ViSortError

ViSortError.queue_error(Errors.ConfigurationError.TestAgain, lol = "idk")
ViSortError.queue_error(Errors.SetupError.MoreTests, lol = "yea")

raise ViSortError(Errors.Other.QueuedErrors)