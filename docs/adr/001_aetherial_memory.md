# ADR 001: Aetherial Memory System

## Context
Long-running autonomous sessions generate a large amount of interaction history. Including all history in the context window leads to:
1. Increased token costs.
2. Slower model response times.
3. Model "confusion" due to irrelevant or distracting information (context window bloat).

## Decision
We have implemented the 'Aetherial Memory' system, which consists of:
1. **Global Context Buffer**: A persistent store for all session interactions and metadata.
2. **ContextItem**: A structured data unit for memories, including content, timestamp, importance, and tags.
3. **Active Attention Filter**: A relevance-based filtering mechanism that scores items based on:
    - **Recency**: Newer items are more relevant (exponential decay).
    - **Keyword Matching**: Items containing keywords from the current query are prioritized.
    - **Importance**: Items explicitly marked as important (e.g., system alerts, final results) are weighted higher.
4. **Selective Injection**: Only the top-K most relevant items are injected into the active prompt context.

## Consequences
### Positive
- **Efficiency**: Significantly reduces context window size for long sessions.
- **Focus**: The model receives information most relevant to its current task.
- **Scalability**: Allows sessions to run indefinitely without hitting hard context limits.

### Negative
- **Context Loss**: Potential to filter out subtle but necessary information if not matched by keywords or recency.
- **Complexity**: Adds a layer of logic between the history and the model prompt.

## Alternatives Considered
- **FIFO Buffer**: Rejected because it loses critical early-session context (like initial goals).
- **Summarization**: Rejected as a primary method because it can lose fine-grained details, though it may be added as a complementary strategy later.
- **Vector-based RAG**: Considered but postponed to keep the initial implementation lightweight and dependency-free. Keyword matching provides a good balance for session-local context.

## Implementation Details
- Located in `aether/memory/context_buffer.py`.
- Tests in `aether/memory/test_context_buffer.py`.
- Scoring Formula: `Score = (Recency * W_r) + (KeywordMatch * W_k) + (Importance * W_i)`
