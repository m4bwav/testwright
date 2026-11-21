# Security

Report a vulnerability through GitHub's private vulnerability reporting on this repository (Security tab, "Report a vulnerability"). Please do not open a public issue.

testwright has no network code. `tw.py` reads local files, runs the test command of the project you point it at (dotnet, npx, pytest), and writes only the result files those runners produce. Run it only on code you trust, as you would run the tests yourself.
