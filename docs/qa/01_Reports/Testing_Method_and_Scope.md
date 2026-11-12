# Testing method and scope

QA Lead: Abdullah Faruqui

Test Engineer: Deepthi A E

The project uses hybrid testing: automated Unit/Integration/regression and suitable tooling, plus targeted manual deployed journeys, real-inbox checks and accessibility samples. Automated cases are not relabelled manual. The course wording asks for manual execution; this packet describes the user's selected hybrid implementation explicitly. The 20 functional requirements each have at least eight mapped case entries, including Unit/Integration/System evidence; numeric mapping counts do not prove independent condition coverage.

Username/password with Django sessions is the revised login scope. Email remains the reset identifier. Mock payments remain in-process Pending initiation; gateway/tokenization are unimplemented. No full proposed REST/JWT/shipping interface is claimed. Original course/SRS/SAD/STP references remain in the full local reference collection.

The user ended capacity testing after existing 250-user runs and excluded month-long availability measurement. Preserve `500 users: Not tested`, `monthly availability: Not tested`, the actual failed 250-user timing and the unresolved admin breadcrumb finding. Full production RPO/RTO and untested accessibility criteria retain their limits. The twice-daily backup schedule adds headroom but does not rewrite historical failures.

CI, checkout, accessibility, capacity and recovery have different source SHAs. Historical browser reports are not silently retagged to the final build. Private credentials, cookies, reset links and database dumps are excluded from the publication packet.
