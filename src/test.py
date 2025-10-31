from Errors import Errors, ViSortError

ViSortError.queue_error(Errors.ConfigurationError.TestAgain, lol = "idk")
ViSortError.queue_error(Errors.SetupError.MoreTests, lol = "yea")

ViSortError.if_errors_raise()