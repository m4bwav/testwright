# Unity Test Framework

Run headless (`TW run` does not start Unity):

```
Unity.exe -batchmode -projectPath P -runTests -testPlatform PlayMode -testResults out/results.xml -logFile out/log.txt [-testFilter "Ns.Class;!Ns.Skip"] [-testCategory Cat]
```

- Results are NUnit 3 XML: `TW parse out/results.xml`. Exit codes are not uniform; trust the XML. No results file means Unity failed before the tests: read the log (logwright `lgw.py query out/log.txt`).
- Do not pass `-quit` with `-runTests`. The default platform is EditMode. `-nographics` breaks rendering-dependent tests.
- Sources: https://docs.unity3d.com/Manual/test-framework/reference-command-line.html and https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html (checked 2026-11-21).
- One Unity instance per project: close the editor or use a worktree copy. unity-agent skills cover editor and CLI driving.
- Coverage: the Code Coverage package (com.unity.testtools.codecoverage) writes OpenCover XML; convert it with reportgenerator to Cobertura for `TW changed`. Check its command-line flags in the docs for the installed version.
- Mutation: no tool runs inside Unity's compile; use hand mutants (SKILL.md step 4).
- Play mode, input and game tests: games.md.
