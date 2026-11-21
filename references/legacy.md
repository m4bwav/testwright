# Legacy code (Feathers, Working Effectively with Legacy Code, 2004)

Legacy code is code without tests. The change algorithm:

1. Find the change points.
2. Find test points where behaviour can be observed.
3. Break dependencies at a seam: extract an interface, subclass and override, pass in the clock or random source.
4. Write characterization tests: call the code, record what it returns now (even if wrong), assert that. Verify (.NET), syrupy (pytest) and Vitest/Jest snapshots make this cheap.
5. Make the change, then refactor under the tests.

- New behaviour goes in a sprout method or class (new tested code called from the old) or a wrap method (old code called from new tested code), so untested code is touched as little as possible.
- A characterization test that pins a bug gets a comment naming the bug; it changes when the owner rules on the fix.
- Scratch refactoring to learn the code is thrown away.
