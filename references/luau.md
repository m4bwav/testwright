# Roblox Luau

`TW run` does not run Luau. Pick a route:

- Jest Roblox (Roblox moved to it from TestEZ): `Jest.runCLI(root, {ci = true}, projects)` returns results with `numFailedTests` and friends; print them as JSON to a file. https://roblox.github.io/jest-roblox-internal (checked 2026-11-21). The community jsdotlua/jest-lua (https://github.com/jsdotlua/jest-lua) runs through run-in-roblox and needs Studio on the machine.
- TestEZ (https://github.com/Roblox/TestEZ): legacy; walk the results tree for Success, Failure and Skipped and print a summary.
- CI without Studio: the Open Cloud Luau Execution API runs a script against a place version with the full DataModel; 5 minute limit, scope `universe.place.luau-execution-session:write`. https://create.roblox.com/docs/cloud/reference/features/luau-execution (checked). The API key is the owner's to create; never make one.
- Lune runs pure-logic modules only (no engine APIs).
- Seeded randomness: `Random.new(seed)`, log the seed on failure. Mutation: hand mutants. roblox-agent covers Studio and Rojo.
