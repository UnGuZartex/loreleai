This codebase implements a neural guided learner, using the loreleai library found at: https://github.com/sebdumancic/loreleai

All self implemented files:

  - Every file in dir /Search is used for the search.
  - Every file in dir /utility is mainly used for formatting neural network inputs.
  - Every file in dir /filereaders is used to read data from the given example and bk files
  - /tests/solver_prolog_swipy_bktest.py implements a test, testing the evaluation capabilities of the SWI Prolog solver, showing a possible bug (?)

NOTE some other files of loreleai were also changes, these are:

   - Several expansion hooks are added to the default ones in loreleai, found in /loreleai/learning/language_filtering.py
   - The utitily methods used for the hooks in the previous point are found in /loreleai/learning/utilities.py
