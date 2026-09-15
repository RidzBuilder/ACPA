# Adapter Contract

Adapters isolate engine-specific execution.

Conceptual flow:
resolve(requirements, engine_context)
→ validate(canonical_plan)
→ compile(canonical_plan)
→ execution_package

An adapter may reject unsupported requirements. It must not silently invent or materially substitute a required capability.
