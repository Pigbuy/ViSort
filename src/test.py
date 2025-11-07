from Errors import Errors, ViSortError

ViSortError.queue_error(Errors.ProgramLoopError.TestError, lol = "idk")
ViSortError.queue_error(Errors.SetupError.MoreTests, lol = "yea")

ViSortError.make_blame_err_if_errors_in_queue(Errors.ConfigurationError.FilterParseFailure, filter_name= "yeet")

ViSortError.queue_error(Errors.ProgramLoopError.TestError, lol = "idk")
ViSortError.make_blame_err_if_errors_in_queue(Errors.ProgramLoopError.TestError, lol = "asdgaewg")

ViSortError.if_errors_in_queue_raise()