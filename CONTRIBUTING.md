# Contributing

Work in a branch and open a pull request in the private repository.

1. Use Node.js 22 and Python 3.11 or newer. The app has no npm runtime dependencies; the surface runner uses Python's standard library.
2. Run `npm test` and `python scripts/check_distribution.py` before submitting changes.
3. If the Python runner or its guide changes, run `python scripts/package_runner.py`, then repeat the distribution check. Commit the generated ZIP with the source change.
4. Describe the concrete behavior changed and the checks performed. Keep uploaded model data, local outputs and credentials outside the repository.
5. Keep synthetic assumptions visible. Do not describe a queued operation as completed or a surface-input change as improved hydraulic performance.

For changes to parsing or accounting, include a meaningful regression case using fictional fixtures. For simple copy or styling changes, check the affected UI; do not add tests that only duplicate the implementation.

The DOM harness executes production event handlers. It cannot verify native file dialogs, browser layout or accessibility. Record those verification limits when relevant.

Public repository visibility, open-source licensing and public website publication require the project owner's separate decision.
