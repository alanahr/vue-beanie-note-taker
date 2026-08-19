Plan: Fix Dependency Vulnerabilities and Deprecated Packages

1. Critical: Update Vitest and Related Dev Dependencies (Client)

    Upgrade vitest from ^2.1.8 to ^4.1.10 to fix a critical vulnerability (GHSA-5xrq-8626-4rwp) where the Vitest UI server allows arbitrary file read and execution
    Upgrade @vitest/ui from ^2.1.8 to ^4.1.10 to resolve the same critical issue
    This also resolves the high-severity Vite path traversal vulnerability (GHSA-fx2h-pf6j-xcff) and the moderate esbuild development server issue (GHSA-67mh-4wv8-2f99) since both are transitive dependencies of vitest

2. Moderate: Update Pytest (Server)

    Upgrade pytest from ==8.3.4 to ==9.0.3 in requirements-dev.txt to fix a local privilege escalation vulnerability (PYSEC-2026-1845) where predictable /tmp/pytest-of-{user} directory names allow local users to cause denial of service or gain privileges

3. Low: Remove Unused Dependencies (Client)

    Remove pinia (^4.0.2) from package.json dependencies -- it is declared but never imported or used anywhere in the source code
    Remove vue-router (^5.2.0) from package.json dependencies -- it is declared but never imported or used anywhere in the source code

4. Low: Update Outdated Tiptap Packages (Client)

    Bump all @tiptap/* packages from ^3.29.2 to ^3.30.1 to pick up the latest patch fixes across the editor extension ecosystem
    Bump vuetify from ^4.1.8 to ^4.1.10 for the latest patch release

5. Informational: Deprecated Transitive Packages (No Action Required)

    glob@10.5.0 is deprecated and pulled in transitively through @vue/test-utils -> js-beautify -> glob. Upgrading jsdom to ^30.0.1 or @vue/test-utils to a future release may resolve this, but neither has a current version that drops the old glob. No direct fix is available without breaking other dependencies.
    whatwg-encoding@3.1.1 is deprecated and pulled in transitively through jsdom -> whatwg-encoding. Upgrading jsdom to ^30.0.1 would resolve this but is a major version jump that may require test adjustments. Recommend deferring until @vue/test-utils officially supports jsdom 30.

6. Security: Exposed Bolt Database Anon Key in .env

    The .env file at the project root contains a hardcoded VITE_SUPABASE_ANON_KEY. While .env is in .gitignore and the anon key is designed to be public (it is sent to the browser by design), the JWT inside it has an exp of 1758881574 which is already in the past (expired August 2026). This key needs to be regenerated in the Bolt Database dashboard and replaced in the .env file. No code change is needed, but the user should be informed.

Summary of actions to take:
Priority	Package	Current	Target	Issue
Critical	vitest	^2.1.8	^4.1.10	GHSA-5xrq-8626-4rwp (CVSS 9.8)
Critical	@vitest/ui	^2.1.8	^4.1.10	Same as above
Moderate	pytest	==8.3.4	==9.0.3	PYSEC-2026-1845
Low	pinia	^4.0.2	remove	Unused dependency
Low	vue-router	^5.2.0	remove	Unused dependency
Low	@tiptap/*	^3.29.2	^3.30.1	Patch updates
Low	vuetify	^4.1.8	^4.1.10	Patch updates
Info	glob@10.5.0	transitive	--	Deprecated, no fix available
Info	whatwg-encoding@3.1.1	transitive	--	Deprecated, no fix available
Info	Bolt Database anon key	expired JWT	regenerate	Expired token in .env

The most important fix is upgrading vitest and @vitest/ui to version 4, which eliminates a critical-severity vulnerability with a CVSS score of 9.8. The pytest upgrade addresses a moderate local privilege escalation. Removing the unused pinia and vue-router dependencies reduces the attack surface and eliminates unnecessary packages from the lock file. The deprecated transitive packages (glob and whatwg-encoding) cannot be fixed without breaking upstream compatibility and should be monitored for future updates.