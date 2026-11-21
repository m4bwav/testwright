# Game tests

## Unity play mode
- `[UnityTest]` IEnumerator tests yield frames (`yield return null`, `WaitForSeconds`); load scenes with `SceneManager.LoadSceneAsync`; use `[UnitySetUp]` and `[UnityTearDown]`.
- Input: derive from `InputTestFixture`, `InputSystem.AddDevice<Keyboard>()`, then `Press`, `Release`, `PressAndRelease`, `Set`. Add com.unity.inputsystem to `testables` in the manifest; register custom layouts in setup. https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Testing.html (checked 2026-11-21).

## Seed replays
Route all randomness through one seeded RNG (System.Random, Unity.Mathematics.Random, Luau `Random.new`) with a fixed timestep. A replay test feeds the same seed and recorded inputs and asserts the same state hash. Log the seed on every failure.

## Save/load round trips
1. Build a state (seeded or property-based), save, load, compare (deep equality or a Verify snapshot of the saved form).
2. Keep one golden save file per shipped save version and test that each still loads (migration).

## Bot playthroughs
A scripted or random-walk bot drives input or a game command API for N minutes and fails on any exception in the log, no progress within a time limit (softlock), or frame rate under a floor. Record the seed. Hand the log to logwright (`lgw.py query <log> --grind`) and its proposals to grindwright. Start with scripted bots; ML-Agents is heavy.

## Roblox
Jest Roblox specs for modules; round-trip DataStore code against a fake store; see luau.md.
