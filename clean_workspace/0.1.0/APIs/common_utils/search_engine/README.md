#  **Search Engine Integration**

This document provides guidance on integrating and configuring the search engine used within the Gmail simulation framework.

---

## **1. Default Engine Setup**

The search engine strategy is selected using the environment variable `DEFAULT_STRATEGY_NAME`, defaulting to `substring` if unspecified.

To override the default strategy in code:

```py
from gmail.SimulationEngine.search_engine import engine_manager
engine_manager.override_strategy_for_engine(strategy_name="keyword")
```

**Note:** Strategy configuration is typically done by scenario teams using Colab, as shown [here](https://colab.research.google.com/drive/1yd4H7qKaEFgWTbLUs0ur3KSJnX-kFic7?usp=sharing).

### **Supported Strategies**

Defined at `APIs/gmail/SimulationEngine/search_engine/strategies.py`:

* `substring` (case-insensitive substring matching, default strategy)  
* `keyword` (Whoosh-based)  
* `semantic` (Qdrant-based): This strategy uses the `QdrantSearchStrategy` for vector-based semantic search. It generates embeddings for text chunks using Google's Gemini model and stores them in a Qdrant vector database that runs in-memory. This allows for finding results based on meaning and context, not just keywords. The configuration for this strategy is more detailed, see `strategy_configs.json` and `APIs/gmail/SimulationEngine/search_engine/configs.py`. The `QdrantConfig` class defines settings like the model name, embedding size, and API key.
* `fuzzy` (RapidFuzz-based)
* `hybrid` (combines semantic and fuzzy)

### **Default Configurations**

Configurations reside in `strategy_configs.json`:

```json
{
  "keyword": {},
  "semantic": {"score_threshold": 0.60},
  "fuzzy": {"score_cutoff": 70},
  "hybrid": {
    "rapidfuzz_config": {"score_cutoff": 70},
    "semantic_config": {"score_threshold": 0.60}
  },
  "substring": {"case_sensitive": false}
}
```

Restore default configurations:

```py
engine_manager.reset_all_engines()
```

Modify configurations dynamically:

```py
fuzzy_engine = engine_manager.override_strategy_for_engine("fuzzy")
fuzzy_engine.config.score_cutoff = 90
```

---

## **2. Querying**

Example usage (`APIs/gmail/Users/Messages/__init__.py`):

```py
def search_ids(query_text, filter_kwargs):
    engine = engine_manager.get_engine()
    results = engine.search(query_text, filter=filter_kwargs)
    return set(obj["id"] for obj in results)
```

**Filters:**  
 All fields within chunk metadata (e.g., `resource_type`, `content_type`, `user_id`) are filterable. Extend metadata as needed to support additional filters.

### **Debugging Queries**

The `rawSearch()` method provides detailed, strategy-level search outputs without score cutoffs, useful for debugging and validation.

---

## **3. Custom Engines**

Custom search engines are defined in `custom_engine_definations.json`:

```json
[
  {
    "id": "list_messages_q_sender",
    "strategy_name": "keyword",
    "metadata": {"used_for": []}
  }
]
```

Fetch a custom engine:

```py
custom_engine = engine_manager.get_engine("list_messages_q_sender")
```

Override strategy for custom engines:

```py
engine_manager.override_strategy_for_engine("fuzzy", engine_id="list_messages_q_sender")
```

---

## **4. How Chunk Identification and Indexing Work**

Each searchable data item (chunk) is tracked using:

* `chunk_id`: a unique UUID derived from the chunk text content, used to detect content changes.  
* `original_json_obj_hash`: a hash of the original data object to detect metadata or payload updates.

When the database state changes, chunks are automatically reindexed if content or metadata changes.

---

## **Embedding Caching**

To improve performance and reduce API calls, the `QdrantSearchStrategy` uses a caching mechanism for text embeddings. This is handled by the `GeminiEmbeddingManager`.

### **Configuration**

The cache is configured in `APIs/gmail/SimulationEngine/search_engine/configs.py` within the `QdrantConfig` class.

*   `cache_file`: Path to the file where the cache will be stored.
*   `max_cache_size`: The maximum number of embeddings to store in the cache.

The `GeminiEmbeddingManager` (`APIs/gmail/SimulationEngine/llm_interface.py`) handles the logic. It uses an in-memory LRU (Least Recently Used) cache that is persisted to the `cache_file`.

### **Disabling Cache**

To disable caching, you can set `lru_cache_file_path` to `None` when initializing `GeminiEmbeddingManager`. In the context of the search engine, you can modify `QdrantConfig` to have `cache_file = None`. This will prevent the cache from being created and used.

---

## **5. Implementation for a New Service**

Integrating a new service involves minimal setup due to a provided abstract adapter base class:

* **Inherit from the base adapter class** (`adapter.py`).  
* **Implement the `db_to_searchable_documents()` method**:

**IMPORTANT:** 

* Strategy classes should remain generic and must not reference specific fields of documents directly. Only the service adapter should reference the database structure or resource-specific fields to ensure modularity and reusability.  
* Keep all the existing strategy classes in each service. Please write a few tests that run the API function by switching the engine strategies.

```py
class ServiceAdapter(Adapter):
    def db_to_searchable_documents(self) -> List[SearchableDocument]:
        # Retrieve data from your service DB
        # Return a list of SearchableDocument instances
```

### **Metadata for Filtering**

Ensure relevant fields are added to the `metadata` dictionary for efficient filtering in searches.

Then, use this adapter in APIs as follows:

```py
from gmail.SimulationEngine.search_engine import engine_manager

engine = engine_manager.get_engine()
results = engine.search(query_text, filter=filter_kwargs)
```

---

## **6. Demos and Testing**

* **Demo file:** `APIs/gmail/SimulationEngine/search_engine/demo.py`  
* **Unit tests:** `APIs/gmail/tests/test_search_engine_strategies.py`

This design allows easy integration, simplified configuration, and extensibility for additional services.

